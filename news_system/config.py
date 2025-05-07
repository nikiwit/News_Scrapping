#!/usr/bin/env python3
# config.py - Updated for two bots and two channels

import os
from pathlib import Path

# System paths
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
STATE_DIR = BASE_DIR / "state"

# Create necessary directories
for dir_path in [DATA_DIR, STATE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Create category directories - only two categories for this setup
CATEGORIES = ["business_news", "it_news"]
for category in CATEGORIES:
    (DATA_DIR / category).mkdir(exist_ok=True)

# Scraping configuration
USER_AGENT = "NewsBot/1.0 (+https://example.com/bot; contact@example.com)"
RATE_LIMIT_SECONDS = 2  # Time to wait between requests to the same domain
DEFAULT_SCRAPE_INTERVAL_HOURS = 3  # Default time to look back for new articles

# News sources configuration
TECH_NEWS_SOURCES = [
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "url": "https://techcrunch.com",
        "category": "it_news"
    },
    {
        "name": "The Verge",
        "rss_url": "https://www.theverge.com/rss/index.xml",
        "url": "https://www.theverge.com",
        "category": "it_news"
    },
    {
        "name": "Wired",
        "rss_url": "https://www.wired.com/feed/rss",
        "url": "https://www.wired.com",
        "category": "it_news"
    },
    {
        "name": "Ars Technica",
        "rss_url": "https://feeds.arstechnica.com/arstechnica/index",
        "url": "https://arstechnica.com",
        "category": "it_news"
    }
]

BUSINESS_NEWS_SOURCES = [
    {
        "name": "Forbes",
        "rss_url": "https://www.forbes.com/business/feed/",
        "url": "https://www.forbes.com/business/",
        "category": "business_news"
    },
    {
        "name": "Business Insider",
        "rss_url": "https://www.businessinsider.com/rss",
        "url": "https://www.businessinsider.com",
        "category": "business_news"
    },
    {
        "name": "Fast Company",
        "rss_url": "https://www.fastcompany.com/latest/rss",
        "url": "https://www.fastcompany.com",
        "category": "business_news"
    },
    {
        "name": "Inc.",
        "rss_url": "https://www.inc.com/rss.xml",
        "url": "https://www.inc.com",
        "category": "business_news"
    }
]

# All news sources combined (no lifestyle category anymore)
ALL_NEWS_SOURCES = TECH_NEWS_SOURCES + BUSINESS_NEWS_SOURCES

# Telegram configuration for TWO SEPARATE BOTS
TELEGRAM_BOT_TOKENS = {
    "business_news": os.environ.get("BUSINESS_BOT_TOKEN", "7753587635:AAGG8-qTogDPtCSL83mr7FBRgIKdijvz89Q"),
    "it_news": os.environ.get("IT_BOT_TOKEN", "7797865654:AAHIBliz3W_GrOy9ruD6vXwoW5OcLgbhifw")
}

# Telegram channels
TELEGRAM_CHANNELS = {
    "business_news": "@business_news_hub",
    "it_news": "@it_geeks_hub"
}

# Bot-to-channel mapping
BOT_CHANNEL_MAPPING = {
    "business_news": "business_news",  # Business bot posts to business channel
    "it_news": "it_news"               # IT bot posts to IT channel
}

# LLM configuration
LLM_API_KEY = os.environ.get("LLM_API_KEY", "your_api_key_here")
LLM_API_URL = "https://api.openai.com/v1/completions"  # Example for GPT