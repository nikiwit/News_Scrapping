#!/usr/bin/env python3
# scrapers/entrepreneurship_news.py - Scraper for entrepreneurship news sources

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
import config

class EntrepreneurshipNewsScraper(NewsScraperBase):
    """
    Scraper for entrepreneurship news sources.
    """
    
    def __init__(self):
        """Initialize the entrepreneurship news scraper."""
        # Initialize logger for this specific module
        self.module_logger = logging.getLogger("NewsSystem.Scraper.Entrepreneurship")
        self.module_logger.info("Initializing EntrepreneurshipNewsScraper")
        
        # Initialize base class
        super().__init__(
            news_sources=config.ENTREPRENEURSHIP_NEWS_SOURCES,
            category="entrepreneurship_news",
            user_agent=config.USER_AGENT,
            rate_limit=config.RATE_LIMIT_SECONDS
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape entrepreneurship news sources.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: Scraped articles
        """
        self.module_logger.info(f"Starting entrepreneurship news scrape (past_hours={past_hours})...")
        
        # Call the parent class scrape method which handles all the logic
        articles = super().scrape(past_hours)
        
        self.module_logger.info(f"Entrepreneurship news scrape complete, found {len(articles)} new articles")
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
    scraper = EntrepreneurshipNewsScraper()
    articles = scraper.scrape(args.past_hours)
    main_logger.info(f"Entrepreneurship news scrape found {len(articles)} articles")