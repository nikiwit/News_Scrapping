#!/usr/bin/env python3
# scrapers/business_news.py - Business news scraper implementation

import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import NewsScraperBase
import config

logger = logging.getLogger("BusinessNewsScraper")

class BusinessNewsScraper(NewsScraperBase):
    """Business news scraper implementation."""
    
    def __init__(self):
        """Initialize business news scraper with business sources."""
        super().__init__(
            news_sources=config.BUSINESS_NEWS_SOURCES,
            category="business_news"
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape business news.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: New articles
        """
        logger.info("Starting business news scrape")
        results = super().scrape(past_hours)
        logger.info(f"Business news scrape complete, found {len(results)} new articles")
        return results

if __name__ == "__main__":
    # Execute standalone if run directly
    scraper = BusinessNewsScraper()
    scraper.scrape()