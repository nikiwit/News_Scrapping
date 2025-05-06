## llm_processor.py
import os
import json
import logging
import requests
from pathlib import Path

from config import LLM_API_KEY, LLM_API_URL, NEWS_DIR
from prompts import (
    STARTUPS_NEWS_PROMPT, ENTREPRENEURSHIP_NEWS_PROMPT, 
    BUSINESS_NEWS_PROMPT, SILICON_VALLEY_NEWS_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("business_llm.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, api_key=LLM_API_KEY, api_url=LLM_API_URL):
        self.api_key = api_key
        self.api_url = api_url
        
    def get_prompt_for_category(self, category):
        """Select the appropriate prompt based on article category"""
        category_prompts = {
            "startups": STARTUPS_NEWS_PROMPT,
            "entrepreneurship": ENTREPRENEURSHIP_NEWS_PROMPT,
            "business": BUSINESS_NEWS_PROMPT,
            "silicon_valley": SILICON_VALLEY_NEWS_PROMPT
        }
        return category_prompts.get(category, BUSINESS_NEWS_PROMPT)
        
    def format_article_with_llm(self, article):
        """Process an article with the LLM API to create a formatted post"""
        prompt_template = self.get_prompt_for_category(article.get("category", "business"))
        
        # Fill the prompt template with article data
        prompt = prompt_template.format(
            title=article["title"],
            source=article["source"],
            url=article["url"],
            content=article["content"]
        )
        
        # Prepare the API request payload
        # This example uses Anthropic's Claude API format; adjust for your chosen LLM
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                formatted_text = result["content"][0]["text"]
                return formatted_text
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                # Fallback formatting if API fails
                return self.create_fallback_format(article)
        except Exception as e:
            logger.error(f"Error processing article with LLM: {str(e)}")
            return self.create_fallback_format(article)
    
    def create_fallback_format(self, article):
        """Create a basic formatted post if LLM processing fails"""
        title = article["title"]
        source = article["source"]
        url = article["url"]
        category = article.get("category", "business")
        
        # Get first paragraph as summary
        content_lines = article["content"].split("\n\n")
        summary = content_lines[0] if content_lines else "No summary available"
        
        # Get emoji based on category
        emoji_map = {
            "startups": "🚀",
            "entrepreneurship": "👨‍💼",
            "business": "📊",
            "silicon_valley": "💻"
        }
        emoji = emoji_map.get(category, "💼")
        
        # Format a basic post
        formatted_text = (
            f"{emoji} <b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"Read more: <a href='{url}'>{source}</a>"
        )
        
        return formatted_text
        
    def process_news_file(self, news_file_path):
        """Process all articles in a news file with LLM"""
        processed_path = None
        
        try:
            with open(news_file_path, 'r', encoding='utf-8') as file:
                articles = json.load(file)
                
            processed_articles = []
            
            for article in articles:
                logger.info(f"Processing article: {article['title']}")
                formatted_text = self.format_article_with_llm(article)
                
                processed_article = article.copy()
                processed_article["formatted_text"] = formatted_text
                processed_articles.append(processed_article)
                
            # Save processed articles
            processed_path = news_file_path.replace(".json", "_processed.json")
            
            with open(processed_path, 'w', encoding='utf-8') as file:
                json.dump(processed_articles, file, ensure_ascii=False, indent=2)
                
            logger.info(f"Processed {len(processed_articles)} articles and saved to {processed_path}")
            
        except Exception as e:
            logger.error(f"Error processing news file: {str(e)}")
            
        return processed_path
