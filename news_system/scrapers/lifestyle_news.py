#!/usr/bin/env python3
# scrapers/lifestyle_news.py - Lifestyle news scraper implementation

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
import config

class LifestyleNewsScraper(NewsScraperBase):
    """Lifestyle news scraper implementation."""
    
    def __init__(self):
        """Initialize lifestyle news scraper with lifestyle sources."""
        # Initialize logger for this specific module
        self.module_logger = logging.getLogger("NewsSystem.Scraper.Lifestyle")
        self.module_logger.info("Initializing LifestyleNewsScraper")
        
        # Initialize base class
        super().__init__(
            news_sources=config.LIFESTYLE_NEWS_SOURCES,
            category="manual_news_system"
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape lifestyle news.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: New articles
        """
        self.module_logger.info(f"Starting lifestyle news scrape (past_hours={past_hours})")
        results = super().scrape(past_hours)
        self.module_logger.info(f"Lifestyle news scrape complete, found {len(results)} new articles")
        return results

if __name__ == "__main__":
    # Set up logging when run directly
    main_logger, log_file = setup_logging(module_name="NewsSystem.Scraper.Lifestyle")
    print(f"Log file created at: {log_file}")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape lifestyle news")
    parser.add_argument("--past_hours", type=int, default=24,
                      help="Hours to look back for new articles (default: 24)")
    args = parser.parse_args()
    
    # Execute with parsed arguments
    main_logger.info(f"Starting lifestyle news scraper with past_hours={args.past_hours}")
    scraper = LifestyleNewsScraper()
    articles = scraper.scrape(args.past_hours)
    main_logger.info(f"Lifestyle news scrape found {len(articles)} articles")