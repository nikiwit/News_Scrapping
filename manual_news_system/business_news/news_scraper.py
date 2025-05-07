#!/usr/bin/env python3
# news_scraper.py

import json
import time
import logging
import requests
import feedparser

from pathlib import Path
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
from newspaper import Article

# ─── CONFIG ───────────────────────────────────────────────────────────────────

USER_AGENT = "MyNewsBot/1.0 (+https://example.com/bot)"
RATE_LIMIT_SECONDS = 1.5
NEWS_DIR = Path("business_news/data")
STATE_FILE = Path("business_news/last_run.json")

NEWS_SOURCES = [
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "url": "https://techcrunch.com",
        "category": "tech"
    },
    {
        "name": "Forbes Entrepreneurs",
        "rss_url": "https://www.forbes.com/entrepreneurs/feed2/",
        "url": "https://www.forbes.com/entrepreneurs/",
        "category": "business"
    },
    # Add more sources...
]

# ─── SETUP ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("NewsScraper")

NEWS_DIR.mkdir(parents=True, exist_ok=True)

if STATE_FILE.exists():
    last_run = json.loads(STATE_FILE.read_text())
else:
    last_run = {}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

class RateLimiter:
    def __init__(self, delay):
        self.delay = delay
        self.last = {}

    def wait(self, domain):
        now = time.time()
        if domain in self.last:
            diff = now - self.last[domain]
            if diff < self.delay:
                time.sleep(self.delay - diff)
        self.last[domain] = time.time()

rate_limiter = RateLimiter(RATE_LIMIT_SECONDS)

def allowed_by_robots(url):
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if base not in allowed_by_robots.cache:
        rp = RobotFileParser()
        rp.set_url(f"{base}/robots.txt")
        try:
            rp.read()
        except:
            logger.warning(f"Could not read robots.txt from {base}")
            return False
        allowed_by_robots.cache[base] = rp
    return allowed_by_robots.cache[base].can_fetch(USER_AGENT, url)
allowed_by_robots.cache = {}

def fetch_url(url):
    if not allowed_by_robots(url):
        logger.warning(f"Disallowed by robots.txt: {url}")
        return None
    rate_limiter.wait(urlparse(url).netloc)
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code == 200:
            return resp.text
        logger.warning(f"HTTP {resp.status_code} for {url}")
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
    return None

def parse_rss(source, cutoff_dt):
    logger.info(f"Parsing RSS for {source['name']}")
    feed = feedparser.parse(source["rss_url"])
    for entry in feed.entries:
        if not hasattr(entry, "published_parsed"):
            continue
        pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if pub_dt <= cutoff_dt:
            continue
        yield {
            "title": entry.get("title", "").strip(),
            "url": entry.link,
            "content": entry.get("summary", "").strip(),
            "source": source["name"],
            "category": source["category"],
            "image_url": entry.get("media_thumbnail", [{}])[0].get("url"),
            "timestamp": pub_dt.isoformat()
        }

def parse_html(url, source, cutoff_dt):
    html = fetch_url(url)
    if not html:
        return None
    art = Article(url)
    art.download(input_html=html); art.parse()
    pub = art.publish_date
    if pub:
        pub = pub.astimezone(timezone.utc)
    if pub and pub <= cutoff_dt:
        return None

    # Fallback timestamp extraction
    if not pub:
        soup = BeautifulSoup(html, "html.parser")
        t = soup.find("time", {"datetime": True})
        if t:
            pub = date_parser.parse(t["datetime"]).astimezone(timezone.utc)
        else:
            jd = soup.find("script", {"type": "application/ld+json"})
            if jd:
                data = json.loads(jd.string or "{}")
                dt = data.get("datePublished")
                if dt:
                    pub = date_parser.parse(dt).astimezone(timezone.utc)
    if not pub or pub <= cutoff_dt:
        return None

    # Use Newspaper3K’s full-text extraction first:
    full_text = art.text.strip()
    if not full_text:
        # Fallback: manual paragraph join
        soup = BeautifulSoup(art.html, "html.parser")
        full_text = "\n\n".join(p.get_text().strip() for p in soup.find_all("p"))

    return {
        "title": art.title or "",
        "url": url,
        "content": full_text,
        "source": source["name"],
        "category": source["category"],
        "image_url": art.top_image or None,
        "timestamp": pub.isoformat()
    }


# ─── MAIN SCRAPE LOGIC ────────────────────────────────────────────────────────

def scrape_all(past_hours=3):
    global last_run
    base_cutoff = datetime.now(timezone.utc) - timedelta(hours=past_hours)
    all_results = []

    for src in NEWS_SOURCES:
        # Determine this source’s cutoff
        last_ts = last_run.get(src["name"])
        if last_ts:
            src_cutoff = max(base_cutoff, date_parser.parse(last_ts))
        else:
            src_cutoff = base_cutoff

        logger.info(f"=== Source: {src['name']} (since {src_cutoff.isoformat()}) ===")
        new_items = []

        # 1) RSS
        if src.get("rss_url"):
            for art in parse_rss(src, src_cutoff):
                new_items.append(art)

        # 2) HTML fallback
        else:
            html = fetch_url(src["url"])
            if html:
                soup = BeautifulSoup(html, "html.parser")
                links = [urljoin(src["url"], a["href"]) for a in soup.select("a[href]")]
                for link in set(links)[:10]:
                    art = parse_html(link, src, src_cutoff)
                    if art:
                        new_items.append(art)

        # Save new items
        if new_items:
            all_results.extend(new_items)
            # Update last_run to the newest timestamp we just saw
            latest_ts = max(item["timestamp"] for item in new_items)
            last_run[src["name"]] = latest_ts

    # Persist state
    STATE_FILE.write_text(json.dumps(last_run, indent=2))

    # Save articles if any
    if all_results:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = NEWS_DIR / f"news_{ts}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(all_results)} articles to {out}")
    else:
        logger.info("No new articles found.")

if __name__ == "__main__":
    scrape_all(past_hours=3)
