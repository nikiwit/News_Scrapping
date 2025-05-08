#!/usr/bin/env python3
# scrapers/entrepreneurship_news.py - Scraper for entrepreneurship news sources

import logging
import config
import argparse
from scrapers.base_scraper import NewsScraperBase

logger = logging.getLogger("NewsSystem")

class EntrepreneurshipNewsScraper(NewsScraperBase):
    """
    Scraper for entrepreneurship news sources.
    """
    
    def __init__(self):
        """Initialize the entrepreneurship news scraper."""
        super().__init__(
            news_sources=config.ENTREPRENEURSHIP_NEWS_SOURCES,
            category="entrepreneurship_news",
            user_agent=config.USER_AGENT,
            rate_limit=config.RATE_LIMIT_SECONDS
        )
        logger.info("Initialized EntrepreneurshipNewsScraper")
    
    def scrape(self, past_hours=None):
        """
        Scrape entrepreneurship news sources.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            list: Scraped articles
        """
        logger.info(f"Starting entrepreneurship news scrape (past_hours={past_hours})...")
        
        # Call the parent class scrape method which handles all the logic
        articles = super().scrape(past_hours)
        
        logger.info(f"Entrepreneurship news scrape complete, found {len(articles)} new articles")
        return articles

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape entrepreneurship news")
    parser.add_argument("--past_hours", type=int, default=24,
                      help="Hours to look back for new articles (default: 24)")
    args = parser.parse_args()
    
    # Execute with parsed arguments
    scraper = EntrepreneurshipNewsScraper()
    scraper.scrape(args.past_hours)