#!/usr/bin/env python3
# main.py - Main script for the news scraping and posting system (with per-run logging)

import asyncio
import argparse
import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
import time

# Import our logging setup
from logging_setup import setup_logging

# Initialize the logger with individual log files for each run
logger = setup_logging()

# Import modules
from scrapers.tech_news import TechNewsScraper
from scrapers.business_news import BusinessNewsScraper
from telegram_client.bot import NewsBot, NewsBotManager
from telegram_client.channel_manager import ChannelManager
from llm.formatter import ContentGenerator
import config

class NewsSystem:
    """
    Main system for scraping news and posting to Telegram.
    """
    
    def __init__(self):
        """Initialize the news system."""
        self.tech_scraper = TechNewsScraper()
        self.business_scraper = BusinessNewsScraper()
        self.bot_manager = NewsBotManager()
        
        # Initialize channel manager with appropriate category
        if len(config.TELEGRAM_BOT_TOKENS) > 0:
            default_category = next(iter(config.TELEGRAM_BOT_TOKENS.keys()))
            self.channel_manager = ChannelManager(category=default_category)
        else:
            self.channel_manager = ChannelManager()
            
        self.content_generator = ContentGenerator()
        
    async def setup_channels(self):
        """
        Setup Telegram channels.
        """
        logger.info("Setting up channels...")
        
        # Check each channel
        for category, channel_id in config.TELEGRAM_CHANNELS.items():
            # Get the appropriate bot
            bot = self.bot_manager.get_bot(category)
            manager = ChannelManager(bot.token)
            
            exists = await manager.channel_exists(channel_id)
            
            if exists:
                logger.info(f"Channel for {category} exists: {channel_id}")
                # Check permissions
                perms = await manager.check_bot_permissions(channel_id)
                if perms["can_post_messages"]:
                    logger.info(f"Bot has posting permissions in {channel_id}")
                else:
                    logger.warning(f"Bot lacks posting permissions in {channel_id}")
                    instructions = await manager.add_bot_as_admin(channel_id)
                    logger.info(f"Instructions to add bot as admin: {instructions}")
            else:
                logger.warning(f"Channel for {category} does not exist: {channel_id}")
                create_instructions = await manager.create_channel(f"{category.title()} News")
                logger.info(f"Channel creation instructions: {create_instructions}")
                
    async def scrape_all(self, past_hours=None):
        """
        Scrape news from all sources.
        
        Args:
            past_hours (int, optional): Hours to look back for new articles
            
        Returns:
            dict: Scraped articles by category
        """
        logger.info(f"Starting news scrape (past_hours={past_hours})...")
        
        tech_results = self.tech_scraper.scrape(past_hours)
        logger.info(f"Tech news scrape complete, found {len(tech_results)} new articles")
        
        business_results = self.business_scraper.scrape(past_hours)
        logger.info(f"Business news scrape complete, found {len(business_results)} new articles")
        
        return {
            "it_news": tech_results,
            "business_news": business_results
        }
        
    async def post_latest(self, count=1, category=None, style=None):
        """
        Post the latest articles to Telegram.
        
        Args:
            count (int): Number of articles to post
            category (str, optional): Category to post from
            style (str, optional): Posting style
            
        Returns:
            int: Number of articles posted
        """
        logger.info(f"Posting latest articles (count={count}, category={category}, style={style})...")
        
        # Get all category directories
        if category:
            categories = [category]
        else:
            categories = config.CATEGORIES
            
        posted = 0
        
        for cat in categories:
            logger.info(f"Processing category: {cat}")
            
            # Find the latest date directory
            date_dirs = sorted(list(config.DATA_DIR.glob("*_*_*")), key=lambda d: d.stat().st_mtime, reverse=True)
            
            if not date_dirs:
                logger.warning(f"No date directories found for category: {cat}")
                continue
                
            # Find the latest time directory within the latest date directory
            time_dirs = sorted(list(date_dirs[0].glob("*")), key=lambda d: d.stat().st_mtime, reverse=True)
            
            if not time_dirs:
                logger.warning(f"No time directories found in {date_dirs[0]}")
                continue
                
            # Check if the category directory exists in the latest time directory
            data_dir = time_dirs[0] / cat
            
            if not data_dir.exists():
                logger.warning(f"No directory for category {cat} in {time_dirs[0]}")
                continue
                
            # Get all article files
            article_files = sorted(
                [f for f in data_dir.glob("extracted_*.json")],
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            
            if not article_files:
                logger.info(f"No articles found in {data_dir}")
                continue
                
            # Post latest articles
            for file in article_files[:count]:
                logger.info(f"Processing article: {file}")
                
                try:
                    # Generate content
                    result = self.content_generator.generate_from_file(file, style)
                    
                    if not result.get("generated_content"):
                        logger.error(f"Failed to generate content for {file}")
                        continue
                        
                    # Post to channel using appropriate bot
                    article = result["article"]
                    channel_id = config.TELEGRAM_CHANNELS.get(cat)
                    
                    if not channel_id:
                        logger.error(f"No channel defined for category: {cat}")
                        continue
                        
                    logger.info(f"Posting to channel: {channel_id}")
                    await self.bot_manager.post_generated_content(
                        result["generated_content"],
                        article,
                        channel_id
                    )
                    
                    posted += 1
                    
                    # Avoid rate limiting
                    if posted < len(article_files[:count]):
                        time.sleep(2)
                        
                except Exception as e:
                    logger.error(f"Error posting article {file}: {e}", exc_info=True)
                    
        logger.info(f"Posted {posted} articles")
        return posted
        
    async def post_from_file(self, file_path, style=None):
        """
        Post a specific article file to Telegram.
        
        Args:
            file_path (str or Path): Path to article JSON file
            style (str, optional): Posting style
            
        Returns:
            bool: True if posted successfully
        """
        logger.info(f"Posting article from file: {file_path}")
        
        try:
            # Generate content
            result = self.content_generator.generate_from_file(file_path, style)
            
            if not result.get("generated_content"):
                logger.error(f"Failed to generate content for {file_path}")
                return False
                
            # Post using appropriate bot
            return await self.bot_manager.post_generated_content(
                result["generated_content"],
                result["article"]
            )
            
        except Exception as e:
            logger.error(f"Error posting article {file_path}: {e}")
            return False
            
    async def run_scheduled(self, interval_hours=3, posts_per_category=1):
        """
        Run the system on a schedule.
        
        Args:
            interval_hours (int): Hours between runs
            posts_per_category (int): Number of posts per category
        """
        logger.info(f"Starting scheduled runs (interval={interval_hours}h, posts={posts_per_category})")
        
        while True:
            try:
                # Create a new log file for this run
                new_logger = setup_logging()
                
                # Scrape news
                new_logger.info(f"Starting scheduled scrape run (interval={interval_hours}h, posts={posts_per_category})")
                await self.scrape_all(interval_hours)
                
                # Post latest
                await self.post_latest(posts_per_category)
                
                # Wait for next run
                new_logger.info(f"Sleeping for {interval_hours} hours...")
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled run: {e}")
                await asyncio.sleep(300)  # Sleep 5 minutes on error

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="News scraping and posting system")
    
    parser.add_argument(
        "--setup", 
        action="store_true",
        help="Setup Telegram channels"
    )
    
    parser.add_argument(
        "--scrape", 
        action="store_true",
        help="Scrape news"
    )
    
    parser.add_argument(
        "--post", 
        action="store_true",
        help="Post latest articles"
    )
    
    parser.add_argument(
        "--file", 
        type=str,
        help="Post a specific article file"
    )
    
    parser.add_argument(
        "--schedule", 
        action="store_true",
        help="Run on a schedule"
    )
    
    parser.add_argument(
        "--hours", 
        type=int,
        default=3,
        help="Hours to look back for new articles or interval between runs"
    )
    
    parser.add_argument(
        "--count", 
        type=int,
        default=1,
        help="Number of articles to post per category"
    )
    
    parser.add_argument(
        "--category", 
        type=str,
        choices=config.CATEGORIES,
        help="Category to scrape or post from"
    )
    
    parser.add_argument(
        "--style", 
        type=str,
        choices=["viral", "educational", "quick"],
        help="Posting style"
    )
    
    args = parser.parse_args()
    
    system = NewsSystem()
    
    if args.setup:
        await system.setup_channels()
        
    if args.scrape:
        await system.scrape_all(args.hours)
        
    if args.post:
        await system.post_latest(args.count, args.category, args.style)
        
    if args.file:
        await system.post_from_file(args.file, args.style)
        
    if args.schedule:
        await system.run_scheduled(args.hours, args.count)
        
    # Default action if none specified
    if not any([args.setup, args.scrape, args.post, args.file, args.schedule]):
        logger.info("No action specified. Running setup, scrape, and post.")
        await system.setup_channels()
        await system.scrape_all()
        await system.post_latest()

if __name__ == "__main__":
    asyncio.run(main())