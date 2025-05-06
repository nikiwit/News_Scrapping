## news_scraper.py
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import os
from pathlib import Path

from config import (
    NEWS_SOURCES, NEWS_DIR, USER_AGENT, RATE_LIMIT,
    MAJOR_VERSION, MINOR_VERSION
)

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
        self.major_version = MAJOR_VERSION
        self.minor_version = MINOR_VERSION
        self.robots_cache = {}  # Cache robots.txt content

    def is_allowed_by_robots(self, url):
        """Check if URL is allowed to be scraped according to robots.txt"""
        from urllib.parse import urlparse
        from urllib.robotparser import RobotFileParser
        
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check if robots.txt is already cached
        if domain not in self.robots_cache:
            robots_url = f"{domain}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_cache[domain] = rp
            except Exception as e:
                logger.warning(f"Error reading robots.txt for {domain}: {e}")
                # If we can't read robots.txt, be conservative and don't scrape
                return False
        
        # Check if our user agent is allowed to access URL
        return self.robots_cache[domain].can_fetch(USER_AGENT, url)

    def respect_rate_limits(self, domain):
        """Ensure we don't overload servers with requests"""
        current_time = time.time()
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            if elapsed < RATE_LIMIT:
                time.sleep(RATE_LIMIT - elapsed)
        
        self.last_request_time[domain] = time.time()

    def fetch_page(self, url):
        """Fetch a webpage with proper rate limiting and checks"""
        from urllib.parse import urlparse
        
        # Check if scraping is allowed
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
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_article_links(self, source):
        """Extract article links from a news source homepage"""
        page_content = self.fetch_page(source["url"])
        if not page_content:
            return []
        
        soup = BeautifulSoup(page_content, "html.parser")
        article_links = []
        
        try:
            for link in soup.select(source["article_selector"]):
                if "href" in link.attrs:
                    # Make sure URL is absolute
                    article_url = urljoin(source["url"], link["href"])
                    article_links.append(article_url)
        except Exception as e:
            logger.error(f"Error extracting links from {source['name']}: {str(e)}")
        
        return article_links[:5]  # Limit to 5 articles per source

    def extract_article_content(self, url, source):
        """Extract article content from a specific URL"""
        page_content = self.fetch_page(url)
        if not page_content:
            return None
        
        soup = BeautifulSoup(page_content, "html.parser")
        
        try:
            # Extract title
            title_element = soup.select_one(source["title_selector"])
            title = title_element.get_text().strip() if title_element else "No title found"
            
            # Extract content
            content_element = soup.select_one(source["content_selector"])
            if not content_element:
                return None
                
            # Get clean text without scripts, styles, etc.
            for tag in content_element.find_all(["script", "style"]):
                tag.decompose()
            
            # Extract paragraphs
            paragraphs = [p.get_text().strip() for p in content_element.find_all("p")]
            content = "\n\n".join(paragraphs)
            
            return {
                "title": title,
                "url": url,
                "content": content,
                "source": source["name"],
                "category": source["category"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None

    def save_news(self, articles):
        """Save extracted news to files with versioned filenames"""
        if not articles:
            logger.warning("No articles to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create structured filename
        filename = f"extracted_news_{self.major_version}.{self.minor_version}_{timestamp}.json"
        filepath = NEWS_DIR / filename
        
        # Save to JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        
        # Increment version for next run
        self.minor_version += 1
        
        return filepath

    def scrape_all_sources(self):
        """Scrape all configured news sources"""
        all_articles = []
        
        for source in NEWS_SOURCES:
            logger.info(f"Scraping {source['name']}...")
            article_links = self.extract_article_links(source)
            logger.info(f"Found {len(article_links)} articles on {source['name']}")
            
            for url in article_links:
                article = self.extract_article_content(url, source)
                if article:
                    all_articles.append(article)
                    
        return self.save_news(all_articles)