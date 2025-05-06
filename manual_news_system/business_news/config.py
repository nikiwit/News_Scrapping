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

# Business News sources - focused on startups, entrepreneurship, and business tech
NEWS_SOURCES = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/category/startups/",
        "article_selector": "a.post-block__title__link",
        "title_selector": "h1.article__title",
        "content_selector": "div.article-content",
        "category": "startups"
    },
    {
        "name": "Forbes",
        "url": "https://www.forbes.com/entrepreneurs/",
        "article_selector": "a.stream-item__title",
        "title_selector": "h1.fs-headline",
        "content_selector": "div.article-body",
        "category": "entrepreneurship"
    },
    {
        "name": "Inc.",
        "url": "https://www.inc.com/startups",
        "article_selector": "a.card-hed-link",
        "title_selector": "h1.articleHeadline__title",
        "content_selector": "div.articleContainer",
        "category": "startups"
    },
    {
        "name": "Fast Company",
        "url": "https://www.fastcompany.com/section/startups",
        "article_selector": "a.link.link-wrapper",
        "title_selector": "h1.post__title",
        "content_selector": "div.post__article-content",
        "category": "startups"
    },
    {
        "name": "CNBC",
        "url": "https://www.cnbc.com/entrepreneur/",
        "article_selector": "a.Card-title",
        "title_selector": "h1.ArticleHeader-headline",
        "content_selector": "div.ArticleBody-articleBody",
        "category": "entrepreneurship"
    },
    {
        "name": "Business Insider",
        "url": "https://www.businessinsider.com/prime/startups",
        "article_selector": "a.tout-title-link",
        "title_selector": "h1",
        "content_selector": "div.post-content",
        "category": "startups"
    },
    {
        "name": "VentureBeat",
        "url": "https://venturebeat.com/category/business/",
        "article_selector": "h2.article-title a",
        "title_selector": "h1.article-title",
        "content_selector": "div.article-content",
        "category": "business"
    }
]

# Telegram settings
TELEGRAM_BOT_TOKEN = os.environ.get("BUSINESS_TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHANNEL_ID = os.environ.get("BUSINESS_TELEGRAM_CHANNEL_ID", "@your_business_channel")
