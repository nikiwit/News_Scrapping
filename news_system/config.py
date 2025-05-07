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
    },
    {
        "name": "Hacker News",
        "rss_url": "https://news.ycombinator.com/rss",
        "url": "https://news.ycombinator.com",
        "category": "it_news"
    },
    {
        "name": "MIT Technology Review",
        "rss_url": "https://www.technologyreview.com/feed/",
        "url": "https://www.technologyreview.com",
        "category": "it_news"
    },
    {
        "name": "ZDNet",
        "rss_url": "https://www.zdnet.com/news/rss.xml",
        "url": "https://www.zdnet.com",
        "category": "it_news"
    },
    {
        "name": "Mashable Tech",
        "rss_url": "https://mashable.com/feeds/rss/tech",
        "url": "https://mashable.com/tech",
        "category": "it_news"
    },
    {
        "name": "Engadget",
        "rss_url": "https://www.engadget.com/rss.xml",
        "url": "https://www.engadget.com",
        "category": "it_news"
    },
    {
        "name": "The Next Web",
        "rss_url": "https://thenextweb.com/feed/",
        "url": "https://thenextweb.com",
        "category": "it_news"
    },
    {
        "name": "ReadWrite",
        "rss_url": "https://readwrite.com/feed/",
        "url": "https://readwrite.com",
        "category": "it_news"
    },
    {
        "name": "Slashdot",
        "rss_url": "https://rss.slashdot.org/Slashdot/slashdotMain",
        "url": "https://slashdot.org",
        "category": "it_news"
    },
    {
        "name": "VentureBeat",
        "rss_url": "https://venturebeat.com/feed/",
        "url": "https://venturebeat.com",
        "category": "it_news"
    },
    {
        "name": "TechRadar",
        "rss_url": "https://www.techradar.com/rss",
        "url": "https://www.techradar.com",
        "category": "it_news"
    },
    {
        "name": "Gizmodo",
        "rss_url": "https://gizmodo.com/rss",
        "url": "https://gizmodo.com",
        "category": "it_news"
    },
    {
        "name": "CNET",
        "rss_url": "https://www.cnet.com/rss/all/",
        "url": "https://www.cnet.com",
        "category": "it_news"
    },
    {
        "name": "Bleeping Computer",
        "rss_url": "https://www.bleepingcomputer.com/feed/",
        "url": "https://www.bleepingcomputer.com",
        "category": "it_news"
    },
    {
        "name": "Tech Republic",
        "rss_url": "https://www.techrepublic.com/rssfeeds/articles/",
        "url": "https://www.techrepublic.com",
        "category": "it_news"
    },
    {
        "name": "Digital Trends",
        "rss_url": "https://www.digitaltrends.com/feed/",
        "url": "https://www.digitaltrends.com",
        "category": "it_news"
    },
    {
        "name": "Hackaday",
        "rss_url": "https://hackaday.com/blog/feed/",
        "url": "https://hackaday.com",
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
        "name": "Entrepreneur Magazine",
        "rss_url": "https://www.entrepreneur.com/latest.rss",
        "url": "https://www.entrepreneur.com",
        "category": "business_news"
    },
    {
        "name": "Inc.",
        "rss_url": "https://www.inc.com/rss.xml",
        "url": "https://www.inc.com",
        "category": "business_news"
    },
    {
        "name": "Harvard Business Review",
        "rss_url": "https://hbr.org/feed",
        "url": "https://hbr.org",
        "category": "business_news"
    },
    {
        "name": "Reuters Business",
        "rss_url": "https://feeds.reuters.com/reuters/businessNews",
        "url": "https://www.reuters.com/business/",
        "category": "business_news"
    },
    {
        "name": "CNBC",
        "rss_url": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "url": "https://www.cnbc.com",
        "category": "business_news"
    },
    {
        "name": "Financial Times",
        "rss_url": "https://www.ft.com/rss/home",
        "url": "https://www.ft.com",
        "category": "business_news"
    },
    {
        "name": "The Economist",
        "rss_url": "https://www.economist.com/business/rss.xml",
        "url": "https://www.economist.com/business",
        "category": "business_news"
    },
    {
        "name": "Wall Street Journal",
        "rss_url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
        "url": "https://www.wsj.com",
        "category": "business_news"
    },
    {
        "name": "Fortune",
        "rss_url": "https://fortune.com/feed/",
        "url": "https://fortune.com",
        "category": "business_news"
    },
    {
        "name": "The Hustle",
        "rss_url": "https://thehustle.co/feed/",
        "url": "https://thehustle.co",
        "category": "business_news"
    },
    {
        "name": "Quartz",
        "rss_url": "https://qz.com/feed/",
        "url": "https://qz.com",
        "category": "business_news"
    },
    {
        "name": "Yahoo Finance",
        "rss_url": "https://finance.yahoo.com/news/rssindex",
        "url": "https://finance.yahoo.com",
        "category": "business_news"
    },
    {
        "name": "McKinsey Insights",
        "rss_url": "https://www.mckinsey.com/insights/rss.aspx",
        "url": "https://www.mckinsey.com/insights",
        "category": "business_news"
    },
    {
        "name": "Moz Blog",
        "rss_url": "https://moz.com/blog/feed",
        "url": "https://moz.com/blog",
        "category": "business_news"
    },
    # New replacements for blocked sources
    {
        "name": "Finextra",
        "rss_url": "https://www.finextra.com/rss/headlines.aspx",
        "url": "https://www.finextra.com",
        "category": "business_news"
    },
    {
        "name": "Banking Dive",
        "rss_url": "https://www.bankingdive.com/feeds/news/",
        "url": "https://www.bankingdive.com",
        "category": "business_news"
    },
    {
        "name": "Payments Dive",
        "rss_url": "https://www.paymentsdive.com/feeds/news/",
        "url": "https://www.paymentsdive.com",
        "category": "business_news"
    },
    {
        "name": "The Financial Brand",
        "rss_url": "https://thefinancialbrand.com/feed/",
        "url": "https://thefinancialbrand.com",
        "category": "business_news"
    }
]

# All news sources combined
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