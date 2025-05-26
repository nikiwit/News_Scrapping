#!/usr/bin/env python3
# scrapers/it_news.py - Updated with proper logging

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path when run directly
sys.path.append(str(Path(__file__).parent.parent))

# IMPORTANT: Import and setup logging FIRST
from logging_setup import setup_logging

# Then import other modules
from scrapers.base_scraper import NewsScraperBase
import config

class TechNewsScraper(NewsScraperBase):
    """
    Scraper for tech news sources with proper logging.
    """
    
    def __init__(self):
        """Initialize the tech news scraper."""
        # The parent class will create its own logger, but this ensures proper setup
        super().__init__(
            news_sources=config.TECH_NEWS_SOURCES,
            category="it_news",
            user_agent=config.USER_AGENT
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape tech news sources.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: Scraped articles
        """
        self.logger.info(f"Starting tech news scrape (past_hours={past_hours})...")
        
        # Call the parent class scrape method
        articles = super().scrape(past_hours)
        
        self.logger.info(f"Tech news scrape complete, found {len(articles)} new articles")
        return articles

if __name__ == "__main__":
    # Set up logging when run directly - THIS IS THE KEY FIX
    main_logger, log_file = setup_logging(module_name="NewsSystem.Scraper.Tech")
    print(f"Log file created at: {log_file}")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape tech news")
    parser.add_argument("--past_hours", type=int, default=24,
                      help="Hours to look back for new articles (default: 24)")
    args = parser.parse_args()
    
    # Execute with parsed arguments
    main_logger.info(f"Starting tech news scraper with past_hours={args.past_hours}")
    
    try:
        scraper = TechNewsScraper()
        articles = scraper.scrape(args.past_hours)
        main_logger.info(f"Tech news scrape found {len(articles)} articles")
        
        if articles:
            print(f"✅ Success! Found {len(articles)} articles")
            print(f"📁 Data saved to: {scraper.data_dir}")
            print(f"📜 Logs saved to: {log_file}")
        else:
            print("ℹ️  No new articles found")
            
    except Exception as e:
        main_logger.error(f"Tech news scraper failed: {e}", exc_info=True)
        print(f"❌ Scraper failed: {e}")