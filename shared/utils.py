# shared/utils.py

import os
import json
import logging
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from datetime import datetime
import time

class ScraperUtils:
    """Utility class for common scraping operations"""
    
    def __init__(self, user_agent, rate_limit=5):
        self.headers = {"User-Agent": user_agent}
        self.rate_limit = rate_limit
        self.last_request_time = {}
        self.robots_cache = {}
        self.logger = logging.getLogger(__name__)
        
    def is_allowed_by_robots(self, url):
        """Check if URL is allowed to be scraped according to robots.txt"""
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
                self.logger.warning(f"Error reading robots.txt for {domain}: {e}")
                # If we can't read robots.txt, be conservative and don't scrape
                return False
        
        # Check if our user agent is allowed to access URL
        return self.robots_cache[domain].can_fetch(self.headers["User-Agent"], url)

    def respect_rate_limits(self, domain):
        """Ensure we don't overload servers with requests"""
        current_time = time.time()
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        
        self.last_request_time[domain] = time.time()

    def fetch_page(self, url):
        """Fetch a webpage with proper rate limiting and checks"""
        # Check if scraping is allowed
        if not self.is_allowed_by_robots(url):
            self.logger.warning(f"Scraping not allowed for {url} according to robots.txt")
            return None
        
        domain = urlparse(url).netloc
        self.respect_rate_limits(domain)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                self.logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_article_links(self, source_url, selector, base_url=None):
        """Extract article links from a source page"""
        page_content = self.fetch_page(source_url)
        if not page_content:
            return []
        
        soup = BeautifulSoup(page_content, "html.parser")
        article_links = []
        
        try:
            for link in soup.select(selector):
                if "href" in link.attrs:
                    # Make sure URL is absolute
                    article_url = urljoin(base_url or source_url, link["href"])
                    article_links.append(article_url)
        except Exception as e:
            self.logger.error(f"Error extracting links from {source_url}: {str(e)}")
        
        return article_links[:5]  # Limit to 5 articles per source

class TelegramUtils:
    """Utility class for Telegram operations"""
    
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.logger = logging.getLogger(__name__)
        
    def send_message(self, text, parse_mode="HTML", disable_web_page_preview=False):
        """Send a message to the Telegram channel"""
        url = f"{self.base_url}/sendMessage"
        
        # Make sure the text is not too long (Telegram has 4096 character limit)
        if len(text) > 4000:
            text = text[:3997] + "..."
            
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                self.logger.info(f"Message sent successfully to {self.channel_id}")
                return response.json()
            else:
                self.logger.error(f"Failed to send message: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return None

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def save_json(data, filepath, ensure_ascii=False, indent=2):
        """Save data as a JSON file"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
            return True
        except Exception as e:
            logging.getLogger(__name__).error(f"Error saving file {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_json(filepath):
        """Load data from a JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error loading file {filepath}: {str(e)}")
            return None
