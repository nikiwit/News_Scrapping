#!/usr/bin/env python3
"""
Scrape-only script - bypasses Telegram integration
Perfect for when you only want to scrape and summarize news
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add to path
sys.path.append(str(Path(__file__).parent))

from logging_setup import setup_logging
try:
    import config
except ImportError:
    # Fallback import path
    import os
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent_dir)
    import config

# Initialize logging
logger, log_file = setup_logging(module_name="ScrapeOnly")

# Import only scrapers (no Telegram)
from scrapers.it_news import TechNewsScraper
from scrapers.business_news import BusinessNewsScraper  
from scrapers.entrepreneurship_news import EntrepreneurshipNewsScraper
from scrapers.lifestyle_news import LifestyleNewsScraper

class SimpleScraper:
    """Simple scraper without Telegram integration"""
    
    def __init__(self):
        """Initialize scrapers with shared timestamp"""
        # Generate a single timestamp for all categories (fixes data collision)
        import pytz
        from datetime import datetime
        kuala_lumpur_tz = pytz.timezone('Asia/Kuala_Lumpur')
        now = datetime.now(pytz.UTC).astimezone(kuala_lumpur_tz)
        self.shared_date_folder = now.strftime("%d_%m_%Y")
        self.shared_time_folder = now.strftime("%H%M")
        
        # Initialize scrapers
        scrapers_classes = {
            "it_news": TechNewsScraper,
            "business_news": BusinessNewsScraper,
            "entrepreneurship_news": EntrepreneurshipNewsScraper,
            "lifestyle_news": LifestyleNewsScraper
        }
        
        self.scrapers = {}
        for category, scraper_class in scrapers_classes.items():
            scraper = scraper_class()
            # Override the data directory to use shared timestamp
            shared_dir = config.DATA_DIR / self.shared_date_folder / self.shared_time_folder / category
            shared_dir.mkdir(parents=True, exist_ok=True)
            scraper.data_dir = shared_dir
            self.scrapers[category] = scraper
            
        # Data location will be shown in output messages
        
    def scrape_all(self, past_hours=24):
        """Scrape all categories with progress tracking"""
        print(f"\n📰 Starting Full News Scrape ({past_hours}h)")
        print(f"📊 Processing {len(self.scrapers)} categories")
        print(f"💾 Data will be saved to: {config.DATA_DIR}/{self.shared_date_folder}/{self.shared_time_folder}\n")
        
        results = {}
        total_articles = 0
        
        # The base_scraper.py now handles progress bars for each category
        for category, scraper in self.scrapers.items():
            try:
                articles = scraper.scrape(past_hours)
                results[category] = articles
                total_articles += len(articles)
            except Exception as e:
                logger.error(f"❌ Error scraping {category}: {e}")
                results[category] = []
        
        print(f"\n🎉 Full scrape complete! Total: {total_articles} articles")
        return results
    
    def scrape_category(self, category, past_hours=24):
        """Scrape specific category"""
        if category not in self.scrapers:
            logger.error(f"Unknown category: {category}")
            return []
            
        logger.info(f"Scraping {category} (past {past_hours} hours)")
        try:
            scraper = self.scrapers[category]
            articles = scraper.scrape(past_hours)
            logger.info(f"✅ {category}: {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"❌ Error scraping {category}: {e}")
            return []

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple news scraper (no Telegram)")
    
    parser.add_argument(
        "--hours", 
        type=int,
        default=12,
        help="Hours to look back for articles (default: 12)"
    )
    
    parser.add_argument(
        "--category", 
        type=str,
        choices=["it_news", "business_news", "entrepreneurship_news", "lifestyle_news"],
        help="Specific category to scrape (default: all)"
    )
    
    args = parser.parse_args()
    
    scraper = SimpleScraper()
    
    if args.category:
        # Scrape specific category
        results = scraper.scrape_category(args.category, args.hours)
        print(f"\n🎯 Scraped {args.category}: {len(results)} articles")
    else:
        # Scrape all categories
        results = scraper.scrape_all(args.hours)
        total = sum(len(articles) for articles in results.values())
        print(f"\n🎉 Scraped all categories: {total} articles")
        
        for category, articles in results.items():
            print(f"  📁 {category}: {len(articles)} articles")

    # Show data location
    print(f"\n📂 Data saved to: {config.DATA_DIR}")
    print(f"📄 Log file: {log_file}")

if __name__ == "__main__":
    main()