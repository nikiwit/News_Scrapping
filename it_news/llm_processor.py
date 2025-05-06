# it_llm_processor.py
import os
import json
import logging
import openai
from pathlib import Path

from config import LLM_API_KEY, LLM_API_URL, NEWS_DIR
from prompts import (
    TECH_NEWS_PROMPT,
    AI_NEWS_PROMPT,
    PROGRAMMING_NEWS_PROMPT,
    SECURITY_NEWS_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("it_news/logs/it_llm.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize OpenAI (AIMLAPI) client
openai.api_key  = "cc7a53d5d84a486695240b9f1576b91d"
openai.api_base = "https://api.aimlapi.com/v1"

class LLMProcessor:
    def __init__(self):
        pass

    def get_prompt_for_category(self, category):
        """Select the appropriate prompt based on article category."""
        return {
            "tech": TECH_NEWS_PROMPT,
            "ai": AI_NEWS_PROMPT,
            "programming": PROGRAMMING_NEWS_PROMPT,
            "security": SECURITY_NEWS_PROMPT
        }.get(category, TECH_NEWS_PROMPT)

    def format_article_with_llm(self, article):
        """Process an article with AIMLAPI to create a formatted post."""
        prompt = self.get_prompt_for_category(article.get("category", "tech")).format(
            title=article["title"],
            source=article["source"],
            url=article["url"],
            content=article["content"]
        )

        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o",             # or another supported model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return resp.choices[0].message.content

        except Exception as e:
            logger.error(f"AIMLAPI error: {e}")
            return self.create_fallback_format(article)

    def create_fallback_format(self, article):
        """Create a basic formatted post if LLM processing fails."""
        title = article["title"]
        source = article["source"]
        url = article["url"]
        category = article.get("category", "tech")

        summary = article["content"].split("\n\n")[0] or "No summary available"
        emoji = {
            "tech": "💻",
            "ai": "🤖",
            "programming": "👨‍💻",
            "security": "🔐"
        }.get(category, "⚡")

        return (
            f"{emoji} <b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"Read more: <a href='{url}'>{source}</a>"
        )

    def process_news_file(self, news_file_path):
        """Process all articles in a news file with AIMLAPI."""
        try:
            with open(news_file_path, encoding="utf-8") as f:
                articles = json.load(f)

            processed = []
            for art in articles:
                logger.info(f"Processing article: {art['title']}")
                art["formatted_text"] = self.format_article_with_llm(art)
                processed.append(art)

            out_path = Path(news_file_path).with_suffix(".processed.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(processed, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(processed)} formatted articles to {out_path}")
            return str(out_path)

        except Exception as e:
            logger.error(f"Error processing news file: {e}")
            return None
