#!/usr/bin/env python3
# telegram/bot.py - Updated for multiple Telegram bots

import logging
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from telegram import Bot, ParseMode, InputMediaPhoto

logger = logging.getLogger("TelegramBot")

class NewsBot:
    """
    Telegram bot for posting news to channels.
    Supports multiple bots for different categories.
    """
    
    def __init__(self, category=None, token=None):
        """
        Initialize the news bot.
        
        Args:
            category (str, optional): Category to use for bot selection
            token (str, optional): Telegram bot token (overrides category selection)
        """
        if token:
            self.token = token
            self.category = None
        elif category and category in config.TELEGRAM_BOT_TOKENS:
            self.token = config.TELEGRAM_BOT_TOKENS[category]
            self.category = category
        else:
            # Default to first available bot
            self.category = next(iter(config.TELEGRAM_BOT_TOKENS.keys()))
            self.token = config.TELEGRAM_BOT_TOKENS[self.category]
            
        self.bot = Bot(token=self.token)
        self.channels = config.TELEGRAM_CHANNELS
        
    async def send_message(self, chat_id, text, parse_mode=ParseMode.MARKDOWN, 
                           disable_web_page_preview=False):
        """
        Send a text message to a chat.
        
        Args:
            chat_id (str): Telegram chat ID
            text (str): Message text
            parse_mode: Message parse mode
            disable_web_page_preview (bool): Whether to disable link previews
            
        Returns:
            Message: Sent message
        """
        try:
            return await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return None
            
    async def send_photo(self, chat_id, photo_url, caption=None, 
                        parse_mode=ParseMode.MARKDOWN):
        """
        Send a photo with optional caption.
        
        Args:
            chat_id (str): Telegram chat ID
            photo_url (str): URL of the photo
            caption (str, optional): Photo caption
            parse_mode: Caption parse mode
            
        Returns:
            Message: Sent message
        """
        try:
            return await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Error sending photo to {chat_id}: {e}")
            # Fallback to text-only if photo fails
            if caption:
                return await self.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode=parse_mode
                )
            return None
            
    async def post_article(self, article, channel_id=None):
        """
        Post an article to a Telegram channel.
        
        Args:
            article (dict): Article data
            channel_id (str, optional): Channel ID to post to
            
        Returns:
            Message: Sent message
        """
        # Determine appropriate channel
        if not channel_id:
            category = article.get("category", "business_news")
            channel_id = self.channels.get(category)
            
        if not channel_id:
            logger.error(f"No channel found for category: {category}")
            return None
            
        # Format the message
        title = article.get("title", "Untitled")
        url = article.get("url", "")
        source = article.get("source", "Unknown source")
        
        # Create the message text
        message = f"*{title}*\n\n"
        
        # Add summary if available
        summary = article.get("summary", "")
        if summary:
            if len(summary) > 300:
                summary = summary[:297] + "..."
            message += f"{summary}\n\n"
            
        # Add source and link
        message += f"Source: {source}\n[Read more]({url})"
        
        # Send with image if available
        image_url = article.get("image_url")
        if image_url:
            return await self.send_photo(
                chat_id=channel_id,
                photo_url=image_url,
                caption=message
            )
        else:
            return await self.send_message(
                chat_id=channel_id,
                text=message
            )
            
    async def post_article_from_file(self, file_path, channel_id=None):
        """
        Post an article from a JSON file.
        
        Args:
            file_path (str or Path): Path to article JSON file
            channel_id (str, optional): Channel ID to post to
            
        Returns:
            Message: Sent message
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                article = json.load(f)
            return await self.post_article(article, channel_id)
        except Exception as e:
            logger.error(f"Error posting article from {file_path}: {e}")
            return None
            
    async def post_generated_content(self, content, article_data=None, channel_id=None):
        """
        Post LLM-generated content based on an article.
        
        Args:
            content (str): Generated content to post
            article_data (dict, optional): Original article data
            channel_id (str, optional): Channel ID to post to
            
        Returns:
            Message: Sent message
        """
        if article_data:
            category = article_data.get("category", "business_news")
            if not channel_id:
                channel_id = self.channels.get(category)
                
            # If there's an image in the article data, send as photo
            image_url = article_data.get("image_url")
            if image_url:
                return await self.send_photo(
                    chat_id=channel_id,
                    photo_url=image_url,
                    caption=content
                )
        
        # Default to text-only message
        if not channel_id:
            channel_id = next(iter(self.channels.values()))
            
        return await self.send_message(
            chat_id=channel_id,
            text=content
        )

class NewsBotManager:
    """
    Manager for multiple news bots.
    """
    
    def __init__(self):
        """Initialize the news bot manager."""
        self.bots = {}
        
    def get_bot(self, category):
        """
        Get a bot for a specific category.
        
        Args:
            category (str): Category to get bot for
            
        Returns:
            NewsBot: Bot for the category
        """
        if category not in self.bots:
            self.bots[category] = NewsBot(category)
        return self.bots[category]
        
    def get_appropriate_bot(self, article_data):
        """
        Get the appropriate bot for an article.
        
        Args:
            article_data (dict): Article data
            
        Returns:
            NewsBot: Appropriate bot
        """
        category = article_data.get("category", "business_news")
        return self.get_bot(category)
        
    async def post_article(self, article, channel_id=None):
        """
        Post an article with the appropriate bot.
        
        Args:
            article (dict): Article data
            channel_id (str, optional): Channel ID to post to
            
        Returns:
            Message: Sent message
        """
        bot = self.get_appropriate_bot(article)
        return await bot.post_article(article, channel_id)
        
    async def post_article_from_file(self, file_path, channel_id=None):
        """
        Post an article from a file with the appropriate bot.
        
        Args:
            file_path (str or Path): Path to article JSON file
            channel_id (str, optional): Channel ID to post to
            
        Returns:
            Message: Sent message
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                article = json.load(f)
            return await self.post_article(article, channel_id)
        except Exception as e:
            logger.error(f"Error posting article from {file_path}: {e}")
            return None
            
    async def post_generated_content(self, content, article_data, channel_id=None):
        """
        Post LLM-generated content with the appropriate bot.
        
        Args:
            content (str): Generated content
            article_data (dict): Article data
            channel_id (str, optional): Channel ID to post to
            
        Returns:
            Message: Sent message
        """
        bot = self.get_appropriate_bot(article_data)
        return await bot.post_generated_content(content, article_data, channel_id)

# Simple test
async def test_bots():
    """Test both bots."""
    manager = NewsBotManager()
    
    # Test IT news bot
    it_bot = manager.get_bot("it_news")
    tech_article = {
        "title": "Test Tech Article",
        "url": "https://example.com/tech",
        "summary": "This is a test tech article.",
        "source": "Tech Source",
        "category": "it_news",
        "image_url": "https://via.placeholder.com/500"
    }
    
    await it_bot.post_article(tech_article)
    
    # Test business news bot
    business_bot = manager.get_bot("business_news")
    business_article = {
        "title": "Test Business Article",
        "url": "https://example.com/business",
        "summary": "This is a test business article.",
        "source": "Business Source",
        "category": "business_news",
        "image_url": "https://via.placeholder.com/500"
    }
    
    await business_bot.post_article(business_article)
    
    logger.info("Test messages sent")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_bots())