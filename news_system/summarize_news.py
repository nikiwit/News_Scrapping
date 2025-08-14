#!/usr/bin/env python3
"""
Simple script to summarize latest news using Llama 3.1:8B
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add to path
sys.path.append(str(Path(__file__).parent))

from llm.llama_summarizer import LlamaNewsSummarizer
try:
    import config
except ImportError:
    # Fallback import path
    import os
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent_dir)
    import config

def main():
    """Summarize the latest scraped news"""
    print("🦙 Llama News Summarizer")
    print("=" * 40)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize summarizer
    print("Connecting to Ollama...")
    summarizer = LlamaNewsSummarizer()
    
    # Find the latest data directory
    data_base = config.DATA_DIR
    if not data_base.exists():
        print(f"❌ Data directory not found: {data_base}")
        return 1
    
    # Get latest date directory (look for DD_MM_YYYY pattern, skip category directories)
    date_dirs = []
    for d in data_base.iterdir():
        if d.is_dir():
            name = d.name
            # Look for date pattern DD_MM_YYYY (should have exactly 2 underscores and digits)
            if name.count('_') == 2 and all(part.isdigit() for part in name.split('_')):
                date_dirs.append(d)
    
    date_dirs = sorted(date_dirs, reverse=True)
    if not date_dirs:
        print(f"❌ No date directories found in {data_base}")
        print("Available directories:")
        for d in data_base.iterdir():
            if d.is_dir():
                print(f"  - {d.name}")
        return 1
    
    latest_date = date_dirs[0]
    print(f"📅 Using latest date: {latest_date.name}")
    
    # Get all time directories from the latest date (to handle multiple timestamps from long scrapes)
    time_dirs = []
    for d in latest_date.iterdir():
        if d.is_dir() and d.name.isdigit() and len(d.name) >= 3:
            time_dirs.append(d)
    
    time_dirs = sorted(time_dirs, reverse=True)
    if not time_dirs:
        print(f"❌ No time directories found in {latest_date}")
        print("Available directories in latest date:")
        for d in latest_date.iterdir():
            if d.is_dir():
                print(f"  - {d.name}")
        return 1
    
    print(f"📅 Found {len(time_dirs)} time directories from latest scraping session")
    
    # Process timestamps from the latest scraping session
    # A scraping session can span multiple timestamps (e.g., 1038, 1039)
    # We'll include all recent timestamps that are close together (within 10 minutes)
    latest_time = int(time_dirs[0].name)
    session_time_dirs = []
    
    for time_dir in time_dirs:
        time_value = int(time_dir.name)
        # Include timestamps within 10 minutes of the latest
        if latest_time - time_value <= 10:  # 10 minute window
            session_time_dirs.append(time_dir)
    
    print(f"🕐 Processing latest session timestamps: {[d.name for d in session_time_dirs]}")
    
    # Collect articles from all timestamps in the latest session
    all_time_dirs = []
    total_article_count = 0
    
    for time_dir in session_time_dirs:
        article_count_in_dir = 0
        categories_found = []
        
        for category_dir in time_dir.iterdir():
            if category_dir.is_dir():
                articles = list(category_dir.glob("extracted_*.json"))
                if articles:
                    article_count_in_dir += len(articles)
                    categories_found.append(f"{category_dir.name}({len(articles)})")
        
        if article_count_in_dir > 0:
            all_time_dirs.append(time_dir)
            total_article_count += article_count_in_dir
            print(f"  ⏰ {time_dir.name}: {article_count_in_dir} articles [{', '.join(categories_found)}]")
    
    if total_article_count == 0:
        print(f"❌ No articles found in any time directories")
        return 1
    
    print(f"📊 Total articles to summarize: {total_article_count}")
    
    # Process only the latest directory
    output_file = config.DATA_DIR / f"summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print(f"🔄 Processing articles from latest session ({len(all_time_dirs)} timestamps)")
    print(f"📊 Starting summarization of {total_article_count} articles...")
    print(f"💡 Note: Only processing latest session to avoid re-summarizing old articles")
    print()  # Empty line for progress bar space
    
    results = summarizer.process_multiple_directories(all_time_dirs, output_file)
    
    if results:
        print(f"\n✅ Successfully summarized {len(results)} articles!")
        print(f"💾 Results saved to: {output_file}")
        print(f"📄 Markdown summary: {output_file.with_suffix('.md')}")
        
        # Show quick preview
        print(f"\n📰 Preview of summaries:")
        for i, result in enumerate(results[:3], 1):
            article = result['original_article']
            print(f"{i}. {article.get('title', 'Untitled')[:60]}...")
            print(f"   Summary: {result['summary'][:100]}...")
            print(f"   URL: {article.get('url', '')}")
            print()
        
        if len(results) > 3:
            print(f"... and {len(results) - 3} more articles")
    else:
        print("❌ No articles found to summarize")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())