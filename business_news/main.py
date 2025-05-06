## main.py
import os
import logging
import argparse
from pathlib import Path

from news_scraper import NewsScraperLegal
from llm_processor import LLMProcessor
from telegram_poster import TelegramPoster
from scheduler import NewsScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("business_news/logs/business_main.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    """Run the complete news processing pipeline"""
    logger.info("Starting Business news processing pipeline")
    
    # Initialize components
    scraper = NewsScraperLegal()
    llm = LLMProcessor()
    telegram = TelegramPoster()
    
    # Step 1: Scrape news
    logger.info("Scraping Business news...")
    news_file = scraper.scrape_all_sources()
    
    if not news_file:
        logger.error("Failed to scrape news")
        return False
        
    # Step 2: Process with LLM
    logger.info("Processing news with LLM...")
    processed_news_file = llm.process_news_file(news_file)
    
    if not processed_news_file:
        logger.error("Failed to process news with LLM")
        return False
        
    # Step 3: Post to Telegram
    logger.info("Posting news to Telegram...")
    success_count = telegram.post_processed_news(processed_news_file)
    
    logger.info(f"Pipeline completed. Posted {success_count} articles to Telegram")
    return True

def main():
    """Main function to parse arguments and start the application"""
    parser = argparse.ArgumentParser(description="Business news scraping and Telegram posting system")
    
    parser.add_argument(
        "--mode", 
        choices=["schedule", "once", "stop"],
        default="once",
        help="Run mode: schedule (run every X minutes), once (run once), or stop (stop scheduler)"
    )
    
    args = parser.parse_args()
    
    # Initialize scheduler with the pipeline function
    scheduler = NewsScheduler(run_pipeline)
    
    if args.mode == "schedule":
        logger.info("Starting scheduler")
        scheduler.start_scheduler()
        
        # Keep the main thread alive
        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping scheduler")
            scheduler.stop_scheduler()
            
    elif args.mode == "once":
        logger.info("Running once")
        scheduler.run_once()
        
    elif args.mode == "stop":
        logger.info("Stopping scheduler")
        scheduler.stop_scheduler()
    
if __name__ == "__main__":
    main()