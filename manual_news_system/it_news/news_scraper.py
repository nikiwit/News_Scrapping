#!/usr/bin/env python3
# news_scraper.py

import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from pathlib import Path

from config import (
    NEWS_SOURCES, NEWS_DIR, USER_AGENT, RATE_LIMIT
)

# Added imports
from newspaper import Article
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("it_news/logs/it_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsScraperLegal:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}
        self.last_request_time = {}  # Track last request time per domain
        self.robots_cache = {}  # Cache robots.txt content

    def is_allowed_by_robots(self, url):
        """Check if URL is allowed to be scraped according to robots.txt"""
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if domain not in self.robots_cache:
            robots_url = f"{domain}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_cache[domain] = rp
            except Exception as e:
                logger.warning(f"Error reading robots.txt for {domain}: {e}")
                return False

        return self.robots_cache[domain].can_fetch(USER_AGENT, url)

    def respect_rate_limits(self, domain):
        current_time = time.time()
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            if elapsed < RATE_LIMIT:
                time.sleep(RATE_LIMIT - elapsed)
        self.last_request_time[domain] = time.time()

    def fetch_page(self, url):
        if not self.is_allowed_by_robots(url):
            logger.warning(f"Scraping not allowed for {url} according to robots.txt")
            return None
        domain = urlparse(url).netloc
        self.respect_rate_limits(domain)
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def extract_article_links(self, source):
        page_content = self.fetch_page(source["url"])
        if not page_content:
            return []
        soup = BeautifulSoup(page_content, "html.parser")
        article_links = []
        try:
            for link in soup.select(source["article_selector"]):
                if "href" in link.attrs:
                    article_url = urljoin(source["url"], link["href"])
                    article_links.append(article_url)
        except Exception as e:
            logger.error(f"Error extracting links from {source['name']}: {e}")
        return article_links[:5]

    def extract_article_content(self, url, source):
        """Extract full article content from a specific URL"""
        page_content = self.fetch_page(url)
        if not page_content:
            return None

        # 1) Parse with Newspaper3K for full-text extraction
        art = Article(url)
        art.download(input_html=page_content)
        art.parse()
        full_text = art.text.strip()

        # 2) If Newspaper3K failed, fall back
        soup = None
        if not full_text:
            soup = BeautifulSoup(page_content, "html.parser")
            # Extract title
            title_element = soup.select_one(source["title_selector"])
            title = title_element.get_text().strip() if title_element else "No title found"
            # Extract container
            content_element = soup.select_one(source["content_selector"])
            if not content_element:
                return None
            for tag in content_element.find_all(["script", "style"]):
                tag.decompose()
            paragraphs = [p.get_text().strip() for p in content_element.find_all("p")]
            full_text = "\n\n".join(paragraphs)
        else:
            # Got full_text; still retrieve title via BeautifulSoup
            soup = BeautifulSoup(page_content, "html.parser")
            title_element = soup.select_one(source["title_selector"])
            title = title_element.get_text().strip() if title_element else art.title or "No title found"

        # Image URL
        image_url = None
        if not soup:
            soup = BeautifulSoup(page_content, "html.parser")
        image_tag = soup.find('meta', property='og:image')
        if image_tag and image_tag.get('content'):
            image_url = image_tag['content']

        return {
            "title": title,
            "url": url,
            "content": full_text,
            "source": source["name"],
            "category": source["category"],
            "image_url": image_url,
            "timestamp": datetime.now().isoformat()
        }

    def save_news(self, articles):
        if not articles:
            logger.warning("No articles to save")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"it_news_{timestamp}.json"
        filepath = NEWS_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return filepath

    def scrape_all_sources(self):
        all_articles = []
        for source in NEWS_SOURCES:
            logger.info(f"Scraping {source['name']}...")
            links = self.extract_article_links(source)
            logger.info(f"Found {len(links)} articles on {source['name']}")
            for url in links:
                art = self.extract_article_content(url, source)
                if art:
                    all_articles.append(art)
        return self.save_news(all_articles)

    def list_saved_news_files(self):
        files = list(NEWS_DIR.glob("it_news_*.json"))
        for i, file in enumerate(files):
            print(f"{i+1}. {file.name}")
        return files

if __name__ == "__main__":
    scraper = NewsScraperLegal()
    action = input("Enter action (scrape or list): ").strip().lower()
    if action == "scrape":
        print("Scraping news...")
        path = scraper.scrape_all_sources()
        if path:
            print(f"News saved to {path}")
    elif action == "list":
        files = scraper.list_saved_news_files()
        if not files:
            print("No saved news files found.")
        else:
            idx = int(input("Enter file number to view or 0 to exit: "))
            if 1 <= idx <= len(files):
                data = json.loads(files[idx-1].read_text(encoding="utf-8"))
                print(f"\nContains {len(data)} articles:\n")
                for i, a in enumerate(data,1):
                    print(f"{i}. {a['title']} ({a['source']})")
    else:
        print("Invalid action. Use 'scrape' or 'list'.")