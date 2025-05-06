# telegram_poster.py
import logging
import json
import requests
import time
from pathlib import Path

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, NEWS_DIR

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
    
    def send_message_with_photo(self, text, photo_url=None, parse_mode="HTML"):
        """Send a message with a photo to the Telegram channel"""
        if photo_url:
            # Send photo with caption
            url = f"{self.base_url}/sendPhoto"
            
            # Telegram caption has a 1024 character limit
            caption = text[:1000] + "..." if len(text) > 1000 else text
            
            payload = {
                "chat_id": self.channel_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": parse_mode
            }
            
            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    logger.info(f"Photo message sent successfully to {self.channel_id}")
                    return response.json()
                else:
                    logger.error(f"Failed to send photo message: {response.text}")
                    # Fall back to text-only message
                    return self.send_message(text, parse_mode)
            except Exception as e:
                logger.error(f"Error sending photo message: {str(e)}")
                # Fall back to text-only message
                return self.send_message(text, parse_mode)
        else:
            # No photo URL provided, send text-only message
            return self.send_message(text, parse_mode)
    
    def list_saved_news_files(self):
        """List all saved news files"""
        files = list(NEWS_DIR.glob("business_news_*.json"))
        for i, file in enumerate(files):
            print(f"{i+1}. {file.name}")
        return files
    
    def post_article_from_file(self):
        """Post a single article from a saved news file"""
        # List available files
        files = self.list_saved_news_files()
        if not files:
            print("No saved news files found.")
            return False
        
        # Ask user to select a file
        file_index = input("Enter file number to use, or 0 to exit: ")
        try:
            file_index = int(file_index)
            if file_index == 0:
                return False
            if 1 <= file_index <= len(files):
                selected_file = files[file_index-1]
                
                # Load the file
                with open(selected_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                
                # List articles in the file
                print(f"\nFile contains {len(articles)} articles.\n")
                for i, article in enumerate(articles):
                    print(f"{i+1}. {article['title']} ({article['source']})")
                
                # Ask user to select an article
                article_index = input("\nEnter article number to post, or 0 to exit: ")
                try:
                    article_index = int(article_index)
                    if article_index == 0:
                        return False
                    if 1 <= article_index <= len(articles):
                        article = articles[article_index-1]
                        
                        # Ask for formatted text
                        print("\nArticle details:")
                        print(f"Title: {article['title']}")
                        print(f"Source: {article['source']}")
                        print(f"URL: {article['url']}")
                        print(f"Category: {article['category']}")
                        print("\nFirst 200 characters of content:")
                        print(article['content'][:200] + "...")
                        
                        # Allow user to enter or paste their formatted text
                        print("\nEnter your formatted text for Telegram (HTML formatting supported):")
                        print("Type or paste your text, then press Enter followed by Ctrl+D (Unix) or Ctrl+Z then Enter (Windows).")
                        formatted_text = []
                        while True:
                            try:
                                line = input()
                                formatted_text.append(line)
                            except EOFError:
                                break
                        formatted_text = "\n".join(formatted_text)
                        
                        # Send the message
                        if formatted_text:
                            # Check if the article has an image URL
                            image_url = article.get('image_url')
                            if image_url:
                                print(f"\nImage URL found: {image_url}")
                                use_image = input("Include this image? (y/n): ").lower().strip() == 'y'
                                if use_image:
                                    result = self.send_message_with_photo(formatted_text, image_url)
                                else:
                                    result = self.send_message(formatted_text)
                            else:
                                result = self.send_message(formatted_text)
                            
                            if result:
                                print("\nMessage sent successfully!")
                                return True
                            else:
                                print("\nFailed to send message. Check logs for details.")
                                return False
                        else:
                            print("\nNo text entered. Message not sent.")
                            return False
                    else:
                        print("\nInvalid article number.")
                        return False
                except ValueError:
                    print("\nInvalid input.")
                    return False
            else:
                print("\nInvalid file number.")
                return False
        except ValueError:
            print("\nInvalid input.")
            return False

if __name__ == "__main__":
    poster = TelegramPoster()
    poster.post_article_from_file()