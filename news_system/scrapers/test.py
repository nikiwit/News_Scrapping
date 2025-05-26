#!/usr/bin/env python3
# test_all_enhanced_scrapers.py - Test all fixed scrapers

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from logging_setup import setup_logging

def test_all_scrapers():
    """Test all enhanced scrapers."""
    print("🧪 Testing All Enhanced Scrapers")
    print("=" * 50)
    
    # Setup logging
    main_logger, log_file = setup_logging(module_name="NewsSystem.TestAll")
    print(f"📜 Master log file: {log_file}")
    print()
    
    scrapers_to_test = [
        ("Tech News", "scrapers.tech_news", "TechNewsScraper"),
        ("Business News", "scrapers.business_news", "BusinessNewsScraper"), 
        ("Entrepreneurship News", "scrapers.entrepreneurship_news", "EntrepreneurshipNewsScraper"),
        ("Lifestyle News", "scrapers.lifestyle_news", "LifestyleNewsScraper"),
        ("Russian News", "scrapers.russian_news", "RussianNewsScraper")
    ]
    
    results = {}
    
    for name, module_name, class_name in scrapers_to_test:
        print(f"🔍 Testing {name}...")
        
        try:
            # Import the scraper module
            module = __import__(module_name, fromlist=[class_name])
            scraper_class = getattr(module, class_name)
            
            # Create scraper instance
            scraper = scraper_class()
            
            # Test scraping with more hours for better chance of finding articles
            articles = scraper.scrape(past_hours=72)
            
            results[name] = {
                'success': True,
                'articles': len(articles),
                'data_dir': str(scraper.data_dir),
                'error': None
            }
            
            print(f"  ✅ {name}: Found {len(articles)} articles")
            if articles:
                print(f"     📁 Saved to: {scraper.data_dir}")
                print(f"     📰 Sample: {articles[0].get('title', 'No title')[:60]}...")
            else:
                print(f"     ℹ️  No new articles (may have been scraped recently)")
                
        except Exception as e:
            results[name] = {
                'success': False,
                'articles': 0,
                'data_dir': None,
                'error': str(e)
            }
            
            print(f"  ❌ {name}: Failed - {e}")
            main_logger.error(f"{name} scraper failed: {e}", exc_info=True)
        
        print()
    
    # Summary
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    successful = 0
    total_articles = 0
    
    for name, result in results.items():
        if result['success']:
            successful += 1
            total_articles += result['articles']
            status = f"✅ SUCCESS ({result['articles']} articles)"
        else:
            status = f"❌ FAILED ({result['error'][:50]}...)"
        
        print(f"{name:20}: {status}")
    
    print()
    print(f"🎯 Summary: {successful}/{len(scrapers_to_test)} scrapers working")
    print(f"📰 Total articles found: {total_articles}")
    print(f"📜 Logs saved to: {log_file}")
    
    if successful == len(scrapers_to_test):
        print("\n🎉 ALL SCRAPERS WORKING! Enhanced system ready!")
    elif successful > 0:
        print(f"\n⚠️  {successful} scrapers working, {len(scrapers_to_test) - successful} need fixes")
    else:
        print("\n🚨 No scrapers working - need to investigate")
    
    return results

if __name__ == "__main__":
    test_all_scrapers()