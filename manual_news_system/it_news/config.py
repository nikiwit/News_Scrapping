# config.py
import os
from pathlib import Path

# Directory settings
BASE_DIR = Path(__file__).resolve().parent
NEWS_DIR = BASE_DIR / "extracted_news"
NEWS_DIR.mkdir(exist_ok=True)

# Scraping settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
RATE_LIMIT = 5  # seconds between requests to the same domain

# IT News sources - focused on tech, programming, and cybersecurity
NEWS_SOURCES = [
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/tech",
        "article_selector": "a.group-hover\\:shadow-underline-franklin",
        "title_selector": "h2",
        "content_selector": "div.duet--article--article-body-component",
        "category": "tech"
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "article_selector": "a.post-block__title__link",
        "title_selector": "h1.article__title",
        "content_selector": "div.article-content",
        "category": "ai"
    },
    {
        "name": "Ars Technica",
        "url": "https://arstechnica.com/information-technology/",
        "article_selector": "a.article-title",
        "title_selector": "h1.article-title",
        "content_selector": "div.article-content",
        "category": "tech"
    },
    {
        "name": "The Register",
        "url": "https://www.theregister.com/security/",
        "article_selector": "a.story_link",
        "title_selector": "h1",
        "content_selector": "div#body",
        "category": "security"
    },
    {
        "name": "VentureBeat",
        "url": "https://venturebeat.com/category/ai/",
        "article_selector": "h2.article-title a",
        "title_selector": "h1.article-title",
        "content_selector": "div.article-content",
        "category": "ai"
    },
    {
        "name": "GitHub Blog",
        "url": "https://github.blog/category/engineering/",
        "article_selector": "h2.h4 a",
        "title_selector": "h1.h2-mktg",
        "content_selector": "div.post-content",
        "category": "programming"
    }
]

# Telegram settings
TELEGRAM_BOT_TOKEN = os.environ.get("IT_TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHANNEL_ID = os.environ.get("IT_TELEGRAM_CHANNEL_ID", "@your_it_channel")
