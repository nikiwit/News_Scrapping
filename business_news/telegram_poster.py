## telegram_poster.py
import logging
import json
import requests
import time
from pathlib import Path

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("business_telegram.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, channel_id=TELEGRAM_CHANNEL_ID):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, text, parse_mode="HTML", disable_web_page_preview=False):
        """Send a message to the Telegram channel"""
        url = f"{self.base_url}/sendMessage"
        
        # Make sure the text is not too long (Telegram has 4096 character limit)
        if len(text) > 4000:
            text = text[:3997] + "..."
            
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {self.channel_id}")
                return response.json()
            else:
                logger.error(f"Failed to send message: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None
            
    def post_processed_news(self, processed_news_path):
        """Post processed news to Telegram channel"""
        try:
            with open(processed_news_path, 'r', encoding='utf-8') as file:
                news_items = json.load(file)
                
            success_count = 0
            
            for item in news_items:
                if self.send_message(item['formatted_text']):
                    success_count += 1
                    # Add delay between messages to avoid hitting rate limits
                    time.sleep(1)
            
            logger.info(f"Posted {success_count}/{len(news_items)} news items to Telegram")
            return success_count
        except Exception as e:
            logger.error(f"Error posting news: {str(e)}")
            return 0