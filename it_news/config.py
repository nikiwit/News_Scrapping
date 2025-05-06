## config.py
import os
from pathlib import Path

# Directory settings
BASE_DIR = Path(__file__).resolve().parent
NEWS_DIR = BASE_DIR / "extracted_news"
NEWS_DIR.mkdir(exist_ok=True)

# Scraping settings
SCRAPING_INTERVAL = 30  # minutes
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
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "article_selector": "a.titlelink",
        "title_selector": "h1",  # Adjust based on target sites
        "content_selector": "div.body, article, div.content", # Adjust based on target sites
        "category": "programming"
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
        "name": "ZDNet",
        "url": "https://www.zdnet.com/topic/security/",
        "article_selector": "a.c-linkOverlay",
        "title_selector": "h1.c-contentHeader_headline",
        "content_selector": "div.c-contentBody",
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

# LLM settings
LLM_API_KEY = os.environ.get("LLM_API_KEY", "YOUR_API_KEY_HERE")
LLM_API_URL = "https://api.anthropic.com/v1/messages"  # Change if using a different provider

# Version numbering for extracted news
MAJOR_VERSION = 0
MINOR_VERSION = 1