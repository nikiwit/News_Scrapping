#!/usr/bin/env python3
# scrapers/entrepreneurship_news.py - Fixed entrepreneurship news scraper

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path when run directly
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

class EntrepreneurshipNewsScraper(NewsScraperBase):
    """
    Scraper for entrepreneurship news sources.
    """
    
    def __init__(self):
        """Initialize the entrepreneurship news scraper."""
        # Initialize base class - it handles the logging setup
        super().__init__(
            news_sources=config.ENTREPRENEURSHIP_NEWS_SOURCES,
            category="entrepreneurship_news",
            user_agent=config.USER_AGENT
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape entrepreneurship news sources.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: Scraped articles
        """
        self.logger.info(f"Starting entrepreneurship news scrape (past_hours={past_hours})...")
        
        # Call the parent class scrape method which handles all the logic
        articles = super().scrape(past_hours)
        
        self.logger.info(f"Entrepreneurship news scrape complete, found {len(articles)} new articles")
        return articles

if __name__ == "__main__":
    # Set up logging when run directly
    main_logger, log_file = setup_logging(module_name="NewsSystem.Scraper.Entrepreneurship")
    print(f"Log file created at: {log_file}")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape entrepreneurship news")
    parser.add_argument("--past_hours", type=int, default=24,
                      help="Hours to look back for new articles (default: 24)")
    args = parser.parse_args()
    
    # Execute with parsed arguments
    main_logger.info(f"Starting entrepreneurship news scraper with past_hours={args.past_hours}")
    
    try:
        scraper = EntrepreneurshipNewsScraper()
        articles = scraper.scrape(args.past_hours)
        main_logger.info(f"Entrepreneurship news scrape found {len(articles)} articles")
        
        if articles:
            print(f"✅ Success! Found {len(articles)} articles")
            print(f"📁 Data saved to: {scraper.data_dir}")
            print(f"📜 Logs saved to: {log_file}")
        else:
            print("ℹ️  No new articles found")
            
    except Exception as e:
        main_logger.error(f"Entrepreneurship news scraper failed: {e}", exc_info=True)
        print(f"❌ Scraper failed: {e}")