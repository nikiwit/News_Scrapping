#!/usr/bin/env python3
# scrapers/tech_news.py - Tech news scraper implementation

import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import NewsScraperBase
import config

logger = logging.getLogger("TechNewsScraper")

class TechNewsScraper(NewsScraperBase):
    """Tech news scraper implementation."""
    
    def __init__(self):
        """Initialize tech news scraper with tech sources."""
        super().__init__(
            news_sources=config.TECH_NEWS_SOURCES,
            category="it_news"
        )
    
    def scrape(self, past_hours=None):
        """
        Scrape tech news.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: New articles
        """
        logger.info("Starting tech news scrape")
        results = super().scrape(past_hours)
        logger.info(f"Tech news scrape complete, found {len(results)} new articles")
        return results

if __name__ == "__main__":
    # Execute standalone if run directly
    scraper = TechNewsScraper()
    scraper.scrape()