#!/usr/bin/env python3
# config.py - Updated to include entrepreneurship news

import os
from pathlib import Path

# System paths
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
STATE_DIR = BASE_DIR / "state"

# Create necessary directories
for dir_path in [DATA_DIR, STATE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Create category directories - now with three categories
CATEGORIES = ["business_news", "it_news", "entrepreneurship_news"]
for category in CATEGORIES:
    (DATA_DIR / category).mkdir(exist_ok=True)

# Scraping configuration
USER_AGENT = "NewsBot/1.0 (+https://example.com/bot; contact@example.com)"
RATE_LIMIT_SECONDS = 2  # Time to wait between requests to the same domain
DEFAULT_SCRAPE_INTERVAL_HOURS = 3  # Default time to look back for new articles

# News sources configuration
TECH_NEWS_SOURCES = [
    {
        "name": "The Verge",
        "rss_url": "https://www.theverge.com/rss/index.xml",
        "url": "https://www.theverge.com",
        "category": "it_news"
    },
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "url": "https://techcrunch.com",
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
        "name": "ZDNet",
        "rss_url": "https://www.zdnet.com/news/rss.xml",
        "url": "https://www.zdnet.com",
        "category": "it_news"
    },
    {
        "name": "VentureBeat",
        "rss_url": "https://feeds.venturebeat.com/VentureBeat",
        "url": "https://venturebeat.com",
        "category": "it_news"
    },
    {
        "name": "GitHub Blog",
        "rss_url": "https://github.blog/feed/",
        "url": "https://github.blog",
        "category": "it_news"
    },
    {
        "name": "Wired",
        "rss_url": "https://www.wired.com/feed/rss",
        "url": "https://www.wired.com",
        "category": "it_news"
    },
    {
        "name": "MIT Technology Review",
        "rss_url": "https://www.technologyreview.com/topnews.rss",
        "url": "https://www.technologyreview.com",
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
        "rss_url": "http://feeds2.feedburner.com/thenextweb",
        "url": "https://thenextweb.com",
        "category": "it_news"
    },
    {
        "name": "Slashdot",
        "rss_url": "https://rss.slashdot.org/Slashdot/slashdotMain",
        "url": "https://slashdot.org",
        "category": "it_news"
    },
    {
        "name": "TechRadar",
        "rss_url": "https://feeds.webservice.techradar.com/rss/new",
        "url": "https://www.techradar.com",
        "category": "it_news"
    },
    {
        "name": "TechRepublic",
        "rss_url": "https://www.techrepublic.com/rssfeeds/articles/?feedType=rssfeeds&sort=latest",
        "url": "https://www.techrepublic.com",
        "category": "it_news"
    },
    {
        "name": "CNET News",
        "rss_url": "https://www.cnet.com/rss/news/",
        "url": "https://www.cnet.com/news",
        "category": "it_news"
    },
    {
        "name": "Tom's Hardware",
        "rss_url": "https://www.tomshardware.com/feeds/rss2/all.xml",
        "url": "https://www.tomshardware.com",
        "category": "it_news"
    },
    {
        "name": "PCWorld",
        "rss_url": "http://feeds.pcworld.com/pcworld/latestnews",
        "url": "https://www.pcworld.com",
        "category": "it_news"
    },
    {
        "name": "Computerworld",
        "rss_url": "https://www.computerworld.com/feed/",
        "url": "https://www.computerworld.com",
        "category": "it_news"
    },
    {
        "name": "TechSpot",
        "rss_url": "https://www.techspot.com/backend.xml",
        "url": "https://www.techspot.com",
        "category": "it_news"
    },
    {
        "name": "BetaNews",
        "rss_url": "https://betanews.com/feed/",
        "url": "https://betanews.com",
        "category": "it_news"
    },
    {
        "name": "TechMeme",
        "rss_url": "https://www.techmeme.com/feed.xml",
        "url": "https://www.techmeme.com",
        "category": "it_news"
    },
    {
        "name": "GeekWire",
        "rss_url": "https://www.geekwire.com/feed/",
        "url": "https://www.geekwire.com",
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
        "name": "Fortune",
        "rss_url": "https://fortune.com/feed/",
        "url": "https://fortune.com",
        "category": "business_news"
    },
    {
        "name": "Yahoo Finance",
        "rss_url": "https://finance.yahoo.com/rss",
        "url": "https://finance.yahoo.com",
        "category": "business_news"
    },
    {
        "name": "CNBC",
        "rss_url": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "url": "https://www.cnbc.com",
        "category": "business_news"
    },
    {
        "name": "Business Insider",
        "rss_url": "https://www.businessinsider.com/rss",
        "url": "https://www.businessinsider.com",
        "category": "business_news"
    },
    {
        "name": "McKinsey Insights",
        "rss_url": "https://www.mckinsey.com/featured-insights/rssfeeds/rss/media/newsfeed.xml",
        "url": "https://www.mckinsey.com/featured-insights",
        "category": "business_news"
    },
    {
        "name": "Moz Blog",
        "rss_url": "https://moz.com/blog/rss",
        "url": "https://moz.com/blog",
        "category": "business_news"
    },
    {
        "name": "Finextra",
        "rss_url": "https://www.finextra.com/rssfeeds",
        "url": "https://www.finextra.com",
        "category": "business_news"
    },
    {
        "name": "Entrepreneur Magazine",
        "rss_url": "https://www.entrepreneur.com/latest/feed",
        "url": "https://www.entrepreneur.com",
        "category": "business_news"
    },
    {
        "name": "The New York Times - Business",
        "rss_url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "url": "https://www.nytimes.com/section/business",
        "category": "business_news"
    },
    {
        "name": "BBC News - Business",
        "rss_url": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "url": "https://www.bbc.com/news/business",
        "category": "business_news"
    },
    {
        "name": "MarketWatch",
        "rss_url": "https://feeds.marketwatch.com/marketwatch/latestnews",
        "url": "https://www.marketwatch.com",
        "category": "business_news"
    },
    {
        "name": "ABC News - Business",
        "rss_url": "https://feeds.abcnews.com/abcnews/moneyheadlines",
        "url": "https://abcnews.go.com/business",
        "category": "business_news"
    },
    {
        "name": "Crunchbase News",
        "rss_url": "https://news.crunchbase.com/feed/",
        "url": "https://news.crunchbase.com",
        "category": "business_news"
    }
]

ENTREPRENEURSHIP_NEWS_SOURCES = [
    {
        "name": "Entrepreneur Magazine",
        "rss_url": "https://www.entrepreneur.com/latest/feed",
        "url": "https://www.entrepreneur.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Business Insider",
        "rss_url": "https://www.businessinsider.com/rss",
        "url": "https://www.businessinsider.com",
        "category": "business_news"
    },
    {
        "name": "Y Combinator Blog",
        "rss_url": "https://blog.ycombinator.com/feed/",
        "url": "https://blog.ycombinator.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Foundr",
        "rss_url": "https://foundr.com/feed",
        "url": "https://foundr.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Success Magazine",
        "rss_url": "https://www.success.com/feed/",
        "url": "https://www.success.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "TechMeme",
        "rss_url": "https://www.techmeme.com/feed.xml",
        "url": "https://www.techmeme.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "TechCrunch Startups",
        "rss_url": "https://techcrunch.com/startups/feed/",
        "url": "https://techcrunch.com/startups",
        "category": "entrepreneurship_news"
    },
    {
        "name": "AI Boom",
        "rss_url": "https://aiboom.io/feed/",
        "url": "https://aiboom.io",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Crunchbase News",
        "rss_url": "https://news.crunchbase.com/feed/",
        "url": "https://news.crunchbase.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Product Hunt Daily",
        "rss_url": "https://www.producthunt.com/rss",
        "url": "https://www.producthunt.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "BetaKit",
        "rss_url": "https://betakit.com/feed/",
        "url": "https://betakit.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Springwise",
        "rss_url": "http://www.springwise.com/features/updates/feed",
        "url": "https://www.springwise.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Techstars News",
        "rss_url": "https://www.techstars.com/news-rss",
        "url": "https://www.techstars.com/news",
        "category": "entrepreneurship_news"
    },
    {
        "name": "HackerNoon",
        "rss_url": "https://hackernoon.com/feed",
        "url": "https://hackernoon.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "SiliconRepublic",
        "rss_url": "https://www.siliconrepublic.com/rss",
        "url": "https://www.siliconrepublic.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "VentureBeat",
        "rss_url": "https://venturebeat.com/feed/",
        "url": "https://venturebeat.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Entrepreneurship.org",
        "rss_url": "https://www.entrepreneurship.org/feed",
        "url": "https://www.entrepreneurship.org",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Startup Grind",
        "rss_url": "https://www.startupgrind.com/feed/",
        "url": "https://www.startupgrind.com",
        "category": "entrepreneurship_news"
    }
]

LIFESTYLE_NEWS_SOURCES = [
    {
        "name": "Lifehacker",
        "rss_url": "https://lifehacker.com/rss/regular/",
        "url": "https://lifehacker.com",
        "category": "manual_news_system"
    },
    {
        "name": "HiConsumption",
        "rss_url": "https://hiconsumption.com/feed/",
        "url": "https://hiconsumption.com",
        "category": "manual_news_system"
    },
    {
        "name": "Cool Tools",
        "rss_url": "https://kk.org/cooltools/feed/",
        "url": "https://kk.org/cooltools",
        "category": "manual_news_system"
    },
    {
        "name": "Men's Health",
        "rss_url": "https://www.menshealth.com/rss/all.xml",
        "url": "https://www.menshealth.com",
        "category": "manual_news_system"
    },
    {
        "name": "BuzzFeed Lifestyle",
        "rss_url": "https://www.buzzfeed.com/lifestyle/index.xml",
        "url": "https://www.buzzfeed.com/lifestyle",
        "category": "manual_news_system"
    },
    {
        "name": "Apartment Therapy",
        "rss_url": "https://www.apartmenttherapy.com/feed/",
        "url": "https://www.apartmenttherapy.com",
        "category": "manual_news_system"
    },
    {
        "name": "Travel+Leisure",
        "rss_url": "https://www.travelandleisure.com/news/rss",
        "url": "https://www.travelandleisure.com",
        "category": "manual_news_system"
    },
    {
        "name": "Food & Wine",
        "rss_url": "https://www.foodandwine.com/feed",
        "url": "https://www.foodandwine.com",
        "category": "manual_news_system"
    },
    {
        "name": "Gizmodo Life",
        "rss_url": "https://gizmodo.com/life/rss",
        "url": "https://gizmodo.com/life",
        "category": "manual_news_system"
    },
    {
        "name": "Refinery29",
        "rss_url": "https://www.refinery29.com/lite.xml",
        "url": "https://www.refinery29.com",
        "category": "manual_news_system"
    },
    {
        "name": "Lonely Planet",
        "rss_url": "https://www.lonelyplanet.com/news/feed/",
        "url": "https://www.lonelyplanet.com/news",
        "category": "manual_news_system"
    },
    {
        "name": "Mental Floss",
        "rss_url": "https://www.mentalfloss.com/rss",
        "url": "https://www.mentalfloss.com",
        "category": "manual_news_system"
    },
    {
        "name": "The Guardian - Life & Style",
        "rss_url": "https://www.theguardian.com/lifeandstyle/rss",
        "url": "https://www.theguardian.com/lifeandstyle",
        "category": "manual_news_system"
    },
    {
        "name": "Prevention",
        "rss_url": "https://www.prevention.com/feed/",
        "url": "https://www.prevention.com",
        "category": "manual_news_system"
    }
]

# All news sources combined
ALL_NEWS_SOURCES = TECH_NEWS_SOURCES + BUSINESS_NEWS_SOURCES + ENTREPRENEURSHIP_NEWS_SOURCES + LIFESTYLE_NEWS_SOURCES

# Telegram configuration
TELEGRAM_BOT_TOKENS = {
    "business_news": os.environ.get("BUSINESS_BOT_TOKEN", "7753587635:AAGG8-qTogDPtCSL83mr7FBRgIKdijvz89Q"),
    "it_news": os.environ.get("IT_BOT_TOKEN", "7797865654:AAHIBliz3W_GrOy9ruD6vXwoW5OcLgbhifw"),
    "entrepreneurship_news": os.environ.get("ENTREPRENEUR_BOT_TOKEN", "7763104070:AAE2RPRGcB7neO1Y8AWt5MVzP9GmVtxUf6g")
}

# Telegram channels
TELEGRAM_CHANNELS = {
    "business_news": "@business_news_hub",
    "it_news": "@it_geeks_hub",
    "entrepreneurship_news": "@entrepreneurship_hub"
}

# Bot-to-channel mapping
BOT_CHANNEL_MAPPING = {
    "business_news": "business_news",
    "it_news": "it_news",
    "entrepreneurship_news": "entrepreneurship_news"
}

# LLM configuration
LLM_API_KEY = os.environ.get("LLM_API_KEY", "your_api_key_here")
LLM_API_URL = "https://api.openai.com/v1/completions"  # Example for GPT