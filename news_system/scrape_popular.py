#!/usr/bin/env python3
"""
Scrape only the 10 most popular sources across all categories
Perfect for quick, focused news updates
"""

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
logger, log_file = setup_logging(module_name="PopularScraper")

# Import scrapers
from scrapers.base_scraper import NewsScraperBase

# TOP 10 MOST POPULAR SOURCES (hand-picked from each category)
POPULAR_SOURCES = [
    # Tech (4 sources)
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "url": "https://techcrunch.com",
        "category": "it_news"
    },
    {
        "name": "The Verge",
        "rss_url": "https://www.theverge.com/rss/index.xml",
        "url": "https://www.theverge.com",
        "category": "it_news"
    },
    {
        "name": "Ars Technica",
        "rss_url": "https://feeds.arstechnica.com/arstechnica/index",
        "url": "https://arstechnica.com",
        "category": "it_news"
    },
    {
        "name": "Wired",
        "rss_url": "https://www.wired.com/feed/rss",
        "url": "https://www.wired.com",
        "category": "it_news"
    },
    
    # Business (3 sources)
    {
        "name": "Business Insider",
        "rss_url": "https://www.businessinsider.com/rss",
        "url": "https://www.businessinsider.com",
        "category": "business_news"
    },
    {
        "name": "Forbes",
        "rss_url": "https://www.forbes.com/business/feed/",
        "url": "https://www.forbes.com/business/",
        "category": "business_news"
    },
    {
        "name": "Harvard Business Review",
        "rss_url": "https://hbr.org/feed",
        "url": "https://hbr.org",
        "category": "business_news"
    },
    
    # Entrepreneurship (2 sources)
    {
        "name": "Entrepreneur Magazine",
        "rss_url": "https://www.entrepreneur.com/latest.rss",
        "url": "https://www.entrepreneur.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Inc.",
        "rss_url": "https://www.inc.com/rss.xml",
        "url": "https://www.inc.com",
        "category": "entrepreneurship_news"
    },
    
    # Lifestyle (1 source)
    {
        "name": "Lifehacker",
        "rss_url": "https://lifehacker.com/rss",
        "url": "https://lifehacker.com",
        "category": "manual_news_system"
    }
]

class PopularSourcesScraper:
    """Scraper for the 10 most popular sources"""
    
    def __init__(self):
        """Initialize popular sources scraper"""
        # Initializing Popular Sources Scraper (output shown below)
        
        # Group sources by category
        self.sources_by_category = {}
        for source in POPULAR_SOURCES:
            category = source['category']
            if category not in self.sources_by_category:
                self.sources_by_category[category] = []
            self.sources_by_category[category].append(source)
        
        # Generate a single timestamp for all categories (fixes data collision)
        import pytz
        from datetime import datetime
        kuala_lumpur_tz = pytz.timezone('Asia/Kuala_Lumpur')
        now = datetime.now(pytz.UTC).astimezone(kuala_lumpur_tz)
        self.shared_date_folder = now.strftime("%d_%m_%Y")
        self.shared_time_folder = now.strftime("%H%M")
        
        # Create category scrapers with shared timestamp
        self.scrapers = {}
        for category, sources in self.sources_by_category.items():
            # Category setup (info shown in final output)
            scraper = NewsScraperBase(
                news_sources=sources,
                category=category
            )
            # Override the data directory to use shared timestamp
            shared_dir = config.DATA_DIR / self.shared_date_folder / self.shared_time_folder / category
            shared_dir.mkdir(parents=True, exist_ok=True)
            scraper.data_dir = shared_dir
            self.scrapers[category] = scraper
    
    def scrape_all(self, past_hours=12):
        """Scrape all popular sources with progress tracking"""
        print(f"\n🌟 Starting Popular Sources Scrape ({past_hours}h)")
        print(f"📊 Processing {len(POPULAR_SOURCES)} popular sources across {len(self.scrapers)} categories")
        print(f"💾 Data will be saved to: {config.DATA_DIR}/{self.shared_date_folder}/{self.shared_time_folder}\n")
        
        results = {}
        total_articles = 0
        
        # The base_scraper.py now handles progress bars for each category
        for category, scraper in self.scrapers.items():
            source_count = len(self.sources_by_category[category])
            
            try:
                articles = scraper.scrape(past_hours)
                results[category] = articles
                total_articles += len(articles)
            except Exception as e:
                logger.error(f"❌ Error scraping {category}: {e}")
                results[category] = []
        
        print(f"\n🎉 Popular sources scrape complete!")
        print(f"📰 Total: {total_articles} articles from {len(POPULAR_SOURCES)} popular sources")
        
        return results
    
    def list_sources(self):
        """List all popular sources"""
        print("🌟 TOP 10 POPULAR NEWS SOURCES:")
        print("=" * 50)
        
        for category, sources in self.sources_by_category.items():
            print(f"\n📁 {category.upper()} ({len(sources)} sources):")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source['name']}")
                print(f"     🔗 {source['url']}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape 10 most popular news sources")
    
    parser.add_argument(
        "--hours", 
        type=int,
        default=12,
        help="Hours to look back for articles (default: 12)"
    )
    
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List the 10 popular sources and exit"
    )
    
    args = parser.parse_args()
    
    scraper = PopularSourcesScraper()
    
    if args.list:
        scraper.list_sources()
        return 0
    
    # Scrape popular sources
    results = scraper.scrape_all(args.hours)
    total = sum(len(articles) for articles in results.values())
    
    print(f"\n🌟 Scraped {len(POPULAR_SOURCES)} popular sources: {total} articles")
    print("📊 Breakdown:")
    for category, articles in results.items():
        source_count = len(scraper.sources_by_category[category])
        print(f"  📁 {category}: {len(articles)} articles ({source_count} sources)")
    
    print(f"\n📂 Data saved to: {config.DATA_DIR}")
    print(f"📄 Log file: {log_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())