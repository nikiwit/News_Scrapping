#!/usr/bin/env python3
# scrapers/base_scraper.py - Enhanced with progress tracking and timeouts

import json
import logging
import hashlib
import pytz
import signal
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from newspaper import Article
from typing import List, Dict, Any, Optional
import sys
import time

# Import enhanced utilities
sys.path.append(str(Path(__file__).parent.parent))

from utils.request_manager import RequestManager
try:
    import config
except ImportError:
    # Fallback import path
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    import config

# Configure module logger - FIXED NAME
logger = logging.getLogger("NewsSystem.Scraper.Base")

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

class NewsScraperBase:
    """
    Enhanced scraper with progress tracking and timeout handling
    """
    
    def __init__(self, news_sources, category, user_agent=None, rate_limit=None):
        """Initialize the scraper with proper logging setup."""
        self.news_sources = news_sources
        self.category = category
        self.user_agent = user_agent or config.USER_AGENT
        
        # Set up category-specific logger
        self.logger = logging.getLogger(f"NewsSystem.Scraper.{category.capitalize()}")
        # Initialization message removed to reduce spam
        
        # Initialize enhanced request manager with optimized settings (quiet mode)
        safe_config = config.REQUEST_MANAGER_CONFIG.copy()
        safe_config['robots_config']['respect_robots'] = False  # Disable robots checking
        safe_config['rate_limit_config']['default_delay'] = 1.0  # Faster scraping
        safe_config['timeout'] = 20  # 20s timeout for requests
        safe_config['max_retries'] = 2  # Only 2 retries to save time
        
        # Temporarily suppress logging during initialization
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.ERROR)  # Only show errors
        
        # Also suppress specific loggers that spam during initialization
        request_logger = logging.getLogger('NewsSystem.Utils.RequestManager')
        session_logger = logging.getLogger('NewsSystem.Utils.SessionManager')
        browser_logger = logging.getLogger('NewsSystem.Utils.BrowserMimicry')
        rate_logger = logging.getLogger('NewsSystem.Utils.RateLimiter')
        
        original_levels = {
            'root': original_level,
            'request': request_logger.level,
            'session': session_logger.level,
            'browser': browser_logger.level,
            'rate': rate_logger.level
        }
        
        request_logger.setLevel(logging.ERROR)
        session_logger.setLevel(logging.ERROR)
        browser_logger.setLevel(logging.ERROR)
        rate_logger.setLevel(logging.ERROR)
        
        self.request_manager = RequestManager(safe_config)
        
        # Restore logging levels
        logging.getLogger().setLevel(original_levels['root'])
        request_logger.setLevel(original_levels['request'])
        session_logger.setLevel(original_levels['session'])
        browser_logger.setLevel(original_levels['browser'])
        rate_logger.setLevel(original_levels['rate'])
        
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
        
        # Progress tracking
        self._progress_start_time = None
        self._current_source = ""
        self._current_article = ""
    
    def _conservative_blocking_check(self, response):
        """Very conservative blocking detection - only real HTTP errors."""
        return response.status_code in [403, 429, 503, 520, 521, 522, 524]
    
    def _print_progress(self, current, total, prefix="Progress", start_time=None, current_item="", stage=""):
        """Print a dynamic progress bar on a single line"""
        import sys
        
        if total == 0:
            return
            
        percent = 100.0 * current / total
        bar_length = 25  # Shorter bar for scraping
        filled_length = int(bar_length * current / total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Calculate time estimates
        time_info = ""
        if start_time and current > 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / current
            remaining = avg_time * (total - current)
            
            if remaining > 60:
                time_info = f" | ETA: {remaining/60:.1f}m"
            else:
                time_info = f" | ETA: {remaining:.0f}s"
        
        # Format current item info
        item_info = ""
        if current_item:
            # Truncate long names
            if len(current_item) > 35:
                current_item = current_item[:32] + "..."
            item_info = f" | {current_item}"
            
        if stage:
            item_info += f" ({stage})"
        
        # Create progress line
        progress_line = f"\r{prefix}: {bar} {percent:5.1f}% ({current}/{total}){time_info}{item_info}"
        
        # Clear the line and print
        sys.stdout.write('\033[K')  # Clear line
        sys.stdout.write(progress_line)
        sys.stdout.flush()
        
        # Print newline when complete
        if current == total:
            print()  # Move to next line when done
    
    def _timeout_handler(self, signum, frame):
        """Handle timeout signal"""
        raise TimeoutError("Operation timed out")
    
    def _with_timeout(self, func, timeout_seconds=60, *args, **kwargs):
        """Execute function with timeout"""
        result = {'value': None, 'error': None}
        exception = {'error': None}
        
        def target():
            try:
                result['value'] = func(*args, **kwargs)
            except Exception as e:
                exception['error'] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_seconds)
        
        if thread.is_alive():
            # Thread is still running, operation timed out
            return None, TimeoutError(f"Operation timed out after {timeout_seconds}s")
        
        if exception['error']:
            return None, exception['error']
            
        return result['value'], None
    
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
                # Loaded tracking data (count shown during scraping)
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
                # Loaded state data (count shown during scraping)
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
        
        # RSS parsing (progress shown in progress bar)
        
        try:
            response = self.request_manager.get(source["rss_url"])
            if not response or response.status_code != 200:
                self.logger.warning(f"Failed to fetch RSS for {source['name']}")
                return
            
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                self.logger.warning(f"No entries found in RSS feed for {source['name']}")
                return
                
            # Found entries (count shown in progress bar)
            
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
                        # Skip already scraped (no logging to reduce spam)
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
                    
                    # Removed individual article logging to reduce spam
                    
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
        # Article fetching (progress shown in progress bar)
        
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
        Synchronous scrape method with progress tracking and timeouts.
        """
        past_hours = past_hours or config.DEFAULT_SCRAPE_INTERVAL_HOURS
        
        # Create timezone-aware cutoff
        base_cutoff = datetime.now(timezone.utc) - timedelta(hours=past_hours)
        all_results = []
        
        # Starting scrape (info shown in progress output)
        
        # Refresh the data directory for this run
        self.data_dir = self.get_date_based_folder()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.news_sources:
            self.logger.warning(f"No news sources configured for {self.category}")
            return []
        
        # Initialize progress tracking
        total_sources = len(self.news_sources)
        self._progress_start_time = time.time()
        print(f"\n🔄 Scraping {self.category}: {total_sources} sources")
        
        for src_idx, src in enumerate(self.news_sources):
            source_name = src["name"]
            self._current_source = source_name
            
            # Update progress
            self._print_progress(src_idx, total_sources, "Scraping", self._progress_start_time, 
                               source_name, "RSS")
            
            # Determine this source's cutoff
            last_ts = self.last_run.get(source_name)
            if last_ts:
                try:
                    src_cutoff = max(base_cutoff, date_parser.parse(last_ts))
                except (ValueError, TypeError):
                    src_cutoff = base_cutoff
            else:
                src_cutoff = base_cutoff
            
            new_items = []
            
            # Get articles from RSS with timeout
            if src.get("rss_url"):
                rss_result, error = self._with_timeout(
                    lambda: list(self._parse_rss(src, src_cutoff)), 
                    timeout_seconds=30  # 30s timeout for RSS parsing
                )
                
                if error:
                    self.logger.warning(f"RSS timeout/error for {source_name}: {error}")
                    continue
                    
                if rss_result:
                    new_items.extend(rss_result)
            
            if not new_items:
                continue
            
            # Process articles with progress and timeouts
            successful_articles = []
            total_articles = len(new_items)
            
            for art_idx, article in enumerate(new_items):
                # Update progress for article processing
                article_title = article.get('title', 'Unknown')[:30]
                self._print_progress(src_idx, total_sources, "Scraping", self._progress_start_time, 
                                   f"{source_name}: {article_title}", f"Article {art_idx+1}/{total_articles}")
                
                # Parse article with timeout
                parsed_article, error = self._with_timeout(
                    self._parse_article, 
                    timeout_seconds=45,  # 45s timeout per article
                    article_info=article
                )
                
                if error:
                    self.logger.warning(f"Article timeout/error: {article_title[:20]}... - {error}")
                    # Use original article data as fallback
                    parsed_article = article
                
                # Add to tracking
                self.tracked_articles["urls"].append(article["url"])
                self.tracked_articles["ids"].append(article["id"])
                successful_articles.append(parsed_article)
            
            # Save successful items
            if successful_articles:
                all_results.extend(successful_articles)
                # Update last_run to the newest timestamp
                latest_ts = max(item["timestamp"] for item in successful_articles)
                self.last_run[source_name] = latest_ts
        
        # Final progress update
        self._print_progress(total_sources, total_sources, "Scraping", self._progress_start_time)
        
        # Save state and tracking
        self._save_state()
        self._save_tracking()
        
        # Save articles if any
        if all_results:
            self._save_articles(all_results)
            print(f"✅ Found {len(all_results)} new articles in {self.category}")
        else:
            print(f"ℹ️  No new articles found in {self.category}")
            
        return all_results
    
    def _save_state(self):
        """Save state data."""
        # Saving state data
        with open(self.state_file, "w") as f:
            json.dump(self.last_run, f, indent=2)
    
    def _save_tracking(self):
        """Save tracking data."""
        # Limit size
        if len(self.tracked_articles["urls"]) > 10000:
            self.tracked_articles["urls"] = self.tracked_articles["urls"][-10000:]
            self.tracked_articles["ids"] = self.tracked_articles["ids"][-10000:]
        
        # Saving tracking data
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