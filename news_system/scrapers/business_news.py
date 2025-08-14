#!/usr/bin/env python3
# scrapers/business_news.py - Fixed business news scraper

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# First, set up logging before any other imports
from logging_setup import setup_logging

# Then import other modules
from scrapers.base_scraper import NewsScraperBase
try:
    import config
except ImportError:
    # Fallback import path
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    import config

class BusinessNewsScraper(NewsScraperBase):
    """Business news scraper implementation."""
    
    def __init__(self):
        """Initialize business news scraper with business sources."""
        # Initialize base class first - it handles the logging setup
        super().__init__(
            news_sources=config.BUSINESS_NEWS_SOURCES,
            category="business_news",
            user_agent=config.USER_AGENT
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape business news.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: New articles
        """
        self.logger.info(f"Starting business news scrape (past_hours={past_hours})...")
        
        # Call the parent class scrape method
        articles = super().scrape(past_hours)
        
        self.logger.info(f"Business news scrape complete, found {len(articles)} new articles")
        return articles

if __name__ == "__main__":
    # Set up logging when run directly
    main_logger, log_file = setup_logging(module_name="NewsSystem.Scraper.Business")
    print(f"Log file created at: {log_file}")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape business news")
    parser.add_argument("--past_hours", type=int, default=24,
                      help="Hours to look back for new articles (default: 24)")
    args = parser.parse_args()
    
    # Execute with parsed arguments
    main_logger.info(f"Starting business news scraper with past_hours={args.past_hours}")
    
    try:
        scraper = BusinessNewsScraper()
        articles = scraper.scrape(args.past_hours)
        main_logger.info(f"Business news scrape found {len(articles)} articles")
        
        if articles:
            print(f"✅ Success! Found {len(articles)} articles")
            print(f"📁 Data saved to: {scraper.data_dir}")
            print(f"📜 Logs saved to: {log_file}")
        else:
            print("ℹ️  No new articles found")
            
    except Exception as e:
        main_logger.error(f"Business news scraper failed: {e}", exc_info=True)
        print(f"❌ Scraper failed: {e}")