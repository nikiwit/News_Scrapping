#!/usr/bin/env python3
# scrapers/base_scraper.py - Fixed with proper logging integration

import json
import logging
import hashlib
import pytz
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from newspaper import Article
from typing import List, Dict, Any, Optional

# Import enhanced utilities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.request_manager import RequestManager
import config

# Configure module logger - FIXED NAME
logger = logging.getLogger("NewsSystem.Scraper.Base")

class NewsScraperBase:
    """
    Enhanced scraper that works with existing synchronous scrapers
    but uses enhanced request management.
    """
    
    def __init__(self, news_sources, category, user_agent=None, rate_limit=None):
        """Initialize the scraper with proper logging setup."""
        self.news_sources = news_sources
        self.category = category
        self.user_agent = user_agent or config.USER_AGENT
        
        # Set up category-specific logger
        self.logger = logging.getLogger(f"NewsSystem.Scraper.{category.capitalize()}")
        self.logger.info(f"Initialized enhanced {category} scraper")
        
        # Initialize enhanced request manager with conservative settings
        safe_config = config.REQUEST_MANAGER_CONFIG.copy()
        safe_config['robots_config']['respect_robots'] = False  # Disable robots checking
        safe_config['rate_limit_config']['default_delay'] = 1.0  # Faster for testing
        
        self.request_manager = RequestManager(safe_config)
        
        # Override blocking detection to be very conservative
        self.request_manager._is_blocked_response = self._conservative_blocking_check
        
        # Setup directories (same as original)
        self.base_data_dir = config.DATA_DIR
        self.category_dir = self.base_data_dir / category
        self.category_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_dir = self.get_date_based_folder()
        
        # Setup tracking
        self.tracking_file = config.STATE_DIR / f"{category}_articles_tracking.json"
        config.STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.tracked_articles = self._load_tracking_data()
        
        self.state_file = config.STATE_DIR / f"{category}_last_run.json"
        self.last_run = self._load_state_data()
    
    def _conservative_blocking_check(self, response):
        """Very conservative blocking detection - only real HTTP errors."""
        return response.status_code in [403, 429, 503, 520, 521, 522, 524]
    
    def get_date_based_folder(self):
        """Get date-based folder (same as original)."""
        kuala_lumpur_tz = pytz.timezone('Asia/Kuala_Lumpur')
        now = datetime.now(pytz.UTC).astimezone(kuala_lumpur_tz)
        
        date_folder = now.strftime("%d_%m_%Y")
        time_folder = now.strftime("%H%M")
        
        date_dir = self.base_data_dir / date_folder / time_folder / self.category
        date_dir.mkdir(parents=True, exist_ok=True)
        
        return date_dir
    
    def _load_tracking_data(self):
        """Load tracking data."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, "r") as f:
                    tracked = json.load(f)
                self.logger.info(f"Loaded tracking data with {len(tracked['urls'])} tracked articles")
                return tracked
            except:
                self.logger.warning(f"Invalid tracking file {self.tracking_file}, creating new one")
        return {"urls": [], "ids": []}
    
    def _load_state_data(self):
        """Load state data."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                self.logger.info(f"Loaded last run state with {len(state)} sources")
                return state
            except:
                self.logger.warning(f"Invalid state file {self.state_file}, creating new one")
        return {}
    
    def _fetch_url(self, url):
        """Enhanced URL fetching using request manager."""
        try:
            response = self.request_manager.get(url)
            
            if response and response.status_code == 200:
                return response.text
            else:
                self.logger.warning(f"HTTP {response.status_code if response else 'No response'} for {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _parse_rss(self, source, cutoff_dt):
        """Parse RSS feed (fixed timezone handling)."""
        import feedparser
        
        self.logger.info(f"Parsing RSS for {source['name']}")
        
        try:
            response = self.request_manager.get(source["rss_url"])
            if not response or response.status_code != 200:
                self.logger.warning(f"Failed to fetch RSS for {source['name']}")
                return
            
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                self.logger.warning(f"No entries found in RSS feed for {source['name']}")
                return
                
            self.logger.info(f"Found {len(feed.entries)} entries in RSS feed for {source['name']}")
            
            for entry in feed.entries:
                try:
                    if not hasattr(entry, "published_parsed"):
                        self.logger.warning(f"Entry has no published date, skipping: {entry.get('title', 'Unknown title')}")
                        continue
                    
                    # Fixed timezone handling
                    pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    
                    # Ensure cutoff_dt is timezone aware
                    if cutoff_dt.tzinfo is None:
                        cutoff_dt = cutoff_dt.replace(tzinfo=timezone.utc)
                    
                    # Skip if too old
                    if pub_dt <= cutoff_dt:
                        self.logger.debug(f"Article too old (published {pub_dt.isoformat()}), skipping: {entry.get('title', 'Unknown title')}")
                        continue
                    
                    # Generate URL hash for duplicate detection
                    url_hash = hashlib.md5(entry.link.encode()).hexdigest()
                    
                    # Skip if already scraped
                    if entry.link in self.tracked_articles["urls"] or url_hash in self.tracked_articles["ids"]:
                        self.logger.info(f"Skipping already scraped article: {entry.link}")
                        continue
                        
                    # Generate unique ID for article
                    article_id = url_hash[:10]
                    
                    # Extract text content
                    content = ""
                    if hasattr(entry, "content") and entry.content:
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
                    
                    self.logger.info(f"New article found: {entry.get('title', 'Unknown title')}")
                    
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
                    self.logger.warning(f"Error processing RSS entry: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error parsing RSS for {source['name']}: {e}")
    
    def _parse_article(self, article_info):
        """Parse full article content."""
        url = article_info["url"]
        self.logger.info(f"Fetching article: {url}")
        
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
            self.logger.error(f"Error parsing article {url}: {e}")
            return article_info
    
    def scrape(self, past_hours=None):
        """
        Synchronous scrape method (backward compatible).
        """
        past_hours = past_hours or config.DEFAULT_SCRAPE_INTERVAL_HOURS
        
        # Create timezone-aware cutoff
        base_cutoff = datetime.now(timezone.utc) - timedelta(hours=past_hours)
        all_results = []
        
        self.logger.info(f"Starting scrape for {self.category} (looking back {past_hours} hours)")
        
        # Refresh the data directory for this run
        self.data_dir = self.get_date_based_folder()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.news_sources:
            self.logger.warning(f"No news sources configured for {self.category}")
            return []
            
        self.logger.info(f"Processing {len(self.news_sources)} news sources")
        
        for src in self.news_sources:
            # Determine this source's cutoff
            last_ts = self.last_run.get(src["name"])
            if last_ts:
                try:
                    src_cutoff = max(base_cutoff, date_parser.parse(last_ts))
                    self.logger.info(f"Using last run timestamp for {src['name']}: {last_ts}")
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid timestamp in last_run for {src['name']}: {last_ts}")
                    src_cutoff = base_cutoff
            else:
                src_cutoff = base_cutoff
                
            self.logger.info(f"=== Source: {src['name']} (since {src_cutoff.isoformat()}) ===")
            new_items = []
            
            # Get articles from RSS
            if src.get("rss_url"):
                for art in self._parse_rss(src, src_cutoff):
                    new_items.append(art)
            
            if not new_items:
                self.logger.info(f"No new articles found for {src['name']}")
                continue
                
            self.logger.info(f"Found {len(new_items)} new articles from {src['name']}")
            
            # Fetch full content for each article
            for i, article in enumerate(new_items):
                self.logger.info(f"Processing article {i+1}/{len(new_items)} from {src['name']}")
                new_items[i] = self._parse_article(article)
                
                # Add to tracking list
                self.tracked_articles["urls"].append(article["url"])
                self.tracked_articles["ids"].append(article["id"])
            
            # Save new items
            if new_items:
                all_results.extend(new_items)
                # Update last_run to the newest timestamp we just saw
                latest_ts = max(item["timestamp"] for item in new_items)
                self.last_run[src["name"]] = latest_ts
                self.logger.info(f"Updated last run timestamp for {src['name']} to {latest_ts}")
        
        # Save state and tracking
        self._save_state()
        self._save_tracking()
        
        # Save articles if any
        if all_results:
            self._save_articles(all_results)
            self.logger.info(f"Saved {len(all_results)} articles to {self.data_dir}")
        else:
            self.logger.info("No new articles found.")
            
        return all_results
    
    def _save_state(self):
        """Save state data."""
        self.logger.info(f"Saving state to {self.state_file}")
        with open(self.state_file, "w") as f:
            json.dump(self.last_run, f, indent=2)
    
    def _save_tracking(self):
        """Save tracking data."""
        # Limit size
        if len(self.tracked_articles["urls"]) > 10000:
            self.tracked_articles["urls"] = self.tracked_articles["urls"][-10000:]
            self.tracked_articles["ids"] = self.tracked_articles["ids"][-10000:]
        
        self.logger.info(f"Saving tracking data to {self.tracking_file}")
        with open(self.tracking_file, "w") as f:
            json.dump(self.tracked_articles, f, indent=2)
    
    def _save_articles(self, articles):
        """Save articles to files."""
        # Save individual files
        for i, article in enumerate(articles):
            version = f"{i+1}"
            article_file = self.data_dir / f"extracted_{version}.json"
            with open(article_file, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
        
        # Save batch file
        batch_file = self.data_dir / "batch.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)