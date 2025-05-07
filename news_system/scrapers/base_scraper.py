#!/usr/bin/env python3
# scrapers/base_scraper.py - Base news scraper functionality

import json
import logging
import requests
import feedparser
import hashlib

from pathlib import Path
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from newspaper import Article

# Import our utilities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.rate_limiter import RateLimiter
from utils.robots_checker import RobotsChecker
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("NewsScraper")

class NewsScraperBase:
    """
    Base class for news scrapers with common functionality.
    """
    
    def __init__(self, news_sources, category, user_agent=None, rate_limit=None):
        """
        Initialize the news scraper.
        
        Args:
            news_sources (list): List of news source dictionaries
            category (str): News category (folder to save to)
            user_agent (str, optional): User agent string
            rate_limit (float, optional): Rate limit in seconds
        """
        self.news_sources = news_sources
        self.category = category
        self.user_agent = user_agent or config.USER_AGENT
        self.rate_limit = rate_limit or config.RATE_LIMIT_SECONDS
        
        # Initialize utilities
        self.rate_limiter = RateLimiter(self.rate_limit)
        self.robots_checker = RobotsChecker(self.user_agent)
        
        # Setup directories
        self.data_dir = config.DATA_DIR / category
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = config.STATE_DIR / f"{category}_last_run.json"
        
        # Load state if it exists
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                self.last_run = json.load(f)
        else:
            self.last_run = {}
            
    def _fetch_url(self, url):
        """
        Fetch a URL with rate limiting and robots.txt checking.
        
        Args:
            url (str): URL to fetch
            
        Returns:
            str or None: HTML content if successful, None otherwise
        """
        if not self.robots_checker.allowed(url):
            logger.warning(f"Disallowed by robots.txt: {url}")
            return None
            
        self.rate_limiter.wait(url)
        
        try:
            resp = requests.get(
                url, 
                headers={"User-Agent": self.user_agent}, 
                timeout=10
            )
            
            if resp.status_code == 200:
                return resp.text
                
            logger.warning(f"HTTP {resp.status_code} for {url}")
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            
        return None
        
    def _parse_rss(self, source, cutoff_dt):
        """
        Parse an RSS feed for articles.
        
        Args:
            source (dict): News source dictionary
            cutoff_dt (datetime): Cutoff datetime
            
        Yields:
            dict: Article information
        """
        logger.info(f"Parsing RSS for {source['name']}")
        
        try:
            feed = feedparser.parse(source["rss_url"])
            
            for entry in feed.entries:
                if not hasattr(entry, "published_parsed"):
                    continue
                    
                # Convert time tuple to datetime
                pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                
                # Skip if too old
                if pub_dt <= cutoff_dt:
                    continue
                    
                # Generate unique ID for article
                article_id = hashlib.md5(entry.link.encode()).hexdigest()[:10]
                
                # Extract text content
                content = ""
                if hasattr(entry, "content"):
                    content = entry.content[0].value
                elif hasattr(entry, "summary"):
                    content = entry.summary
                
                # Basic cleanup of HTML
                if content:
                    soup = BeautifulSoup(content, "html.parser")
                    content = soup.get_text()
                
                # Get image URL if available
                image_url = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get("url")
                elif hasattr(entry, "media_content") and entry.media_content:
                    media = entry.media_content[0]
                    if media.get("medium") == "image":
                        image_url = media.get("url")
                
                yield {
                    "id": article_id,
                    "title": entry.get("title", "").strip(),
                    "url": entry.link,
                    "summary": content.strip(),
                    "content": None,  # Will be fetched in detail if needed
                    "source": source["name"],
                    "category": source["category"],
                    "image_url": image_url,
                    "timestamp": pub_dt.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error parsing RSS for {source['name']}: {e}")
    
    def _parse_article(self, article_info):
        """
        Fetch and parse a full article.
        
        Args:
            article_info (dict): Basic article information
            
        Returns:
            dict: Updated article information with full content
        """
        url = article_info["url"]
        logger.info(f"Fetching article: {url}")
        
        html = self._fetch_url(url)
        if not html:
            return article_info
            
        try:
            art = Article(url)
            art.set_html(html)
            art.parse()
            
            # Update article info with full content
            article_info["content"] = art.text.strip()
            
            # Update image if we didn't have one
            if not article_info.get("image_url") and art.top_image:
                article_info["image_url"] = art.top_image
                
            # Try to get a better timestamp if available
            if art.publish_date:
                pub_date = art.publish_date
                if not pub_date.tzinfo:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                article_info["timestamp"] = pub_date.isoformat()
                
            return article_info
            
        except Exception as e:
            logger.error(f"Error parsing article {url}: {e}")
            return article_info
    
    def scrape(self, past_hours=None):
        """
        Scrape news from all sources.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: New articles
        """
        past_hours = past_hours or config.DEFAULT_SCRAPE_INTERVAL_HOURS
        base_cutoff = datetime.now(timezone.utc) - timedelta(hours=past_hours)
        all_results = []
        
        for src in self.news_sources:
            # Determine this source's cutoff
            last_ts = self.last_run.get(src["name"])
            if last_ts:
                src_cutoff = max(base_cutoff, date_parser.parse(last_ts))
            else:
                src_cutoff = base_cutoff
                
            logger.info(f"=== Source: {src['name']} (since {src_cutoff.isoformat()}) ===")
            new_items = []
            
            # Get articles from RSS
            if src.get("rss_url"):
                for art in self._parse_rss(src, src_cutoff):
                    new_items.append(art)
            
            # HTML fallback (optional implementation)
            else:
                html = self._fetch_url(src["url"])
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    links = [urljoin(src["url"], a["href"]) for a in soup.select("a[href]")]
                    for link in set(links)[:10]:  # Limit to first 10 links
                        if not any(urlparse(link).netloc == urlparse(src["url"]).netloc for src in self.news_sources):
                            continue
                        
                        art = self._process_html_article(link, src, src_cutoff)
                        if art:
                            new_items.append(art)
            
            # Fetch full content for each article
            for i, article in enumerate(new_items):
                logger.info(f"Processing article {i+1}/{len(new_items)} from {src['name']}")
                new_items[i] = self._parse_article(article)
            
            # Save new items
            if new_items:
                all_results.extend(new_items)
                # Update last_run to the newest timestamp we just saw
                latest_ts = max(item["timestamp"] for item in new_items)
                self.last_run[src["name"]] = latest_ts
                
        # Persist state
        with open(self.state_file, "w") as f:
            json.dump(self.last_run, f, indent=2)
            
        # Save articles if any
        if all_results:
            # Save batched by timestamp
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            
            # Also save individual files for LLM processing
            for i, article in enumerate(all_results):
                version = f"{ts}_{i+1}"
                article_file = self.data_dir / f"extracted_{version}.json"
                with open(article_file, "w", encoding="utf-8") as f:
                    json.dump(article, f, ensure_ascii=False, indent=2)
                
            # Save batch file
            batch_file = self.data_dir / f"news_{ts}.json"
            with open(batch_file, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved {len(all_results)} articles to {self.data_dir}")
        else:
            logger.info("No new articles found.")
            
        return all_results
            
    def _process_html_article(self, link, source, cutoff_dt):
        """
        Process an article from a direct HTML link (fallback when no RSS).
        
        Args:
            link (str): Article URL
            source (dict): News source information
            cutoff_dt (datetime): Cutoff datetime
            
        Returns:
            dict or None: Article information or None if too old
        """
        html = self._fetch_url(link)
        if not html:
            return None
            
        try:
            art = Article(link)
            art.set_html(html)
            art.parse()
            
            pub = art.publish_date
            if pub:
                if not pub.tzinfo:
                    pub = pub.replace(tzinfo=timezone.utc)
                    
                if pub <= cutoff_dt:
                    return None
            
            # Generate unique ID for article
            article_id = hashlib.md5(link.encode()).hexdigest()[:10]
            
            return {
                "id": article_id,
                "title": art.title or "",
                "url": link,
                "summary": art.text[:500] + "..." if len(art.text) > 500 else art.text,
                "content": art.text,
                "source": source["name"],
                "category": source["category"],
                "image_url": art.top_image or None,
                "timestamp": pub.isoformat() if pub else datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing HTML article {link}: {e}")
            return None