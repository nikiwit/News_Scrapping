#!/usr/bin/env python3
# scrapers/lifestyle_news.py - Lifestyle news scraper implementation

import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import NewsScraperBase
import config

logger = logging.getLogger("LifestyleNewsScraper")

class LifestyleNewsScraper(NewsScraperBase):
    """Lifestyle news scraper implementation."""
    
    def __init__(self):
        """Initialize lifestyle news scraper with lifestyle sources."""
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
        logger.info("Starting lifestyle news scrape")
        results = super().scrape(past_hours)
        logger.info(f"Lifestyle news scrape complete, found {len(results)} new articles")
        return results

if __name__ == "__main__":
    # Execute standalone if run directly
    scraper = LifestyleNewsScraper()
    scraper.scrape()