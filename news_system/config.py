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
        "name": "The Register",
        "rss_url": "https://www.theregister.com/headlines.atom",
        "url": "https://www.theregister.com/security/",
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
        "rss_url": "https://venturebeat.com/feed/",
        "url": "https://venturebeat.com",
        "category": "it_news"
    },
    {
        "name": "GitHub Blog",
        "rss_url": "https://github.blog/feed/",
        "url": "https://github.blog/category/engineering/",
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
        "rss_url": "https://www.technologyreview.com/feed/",
        "url": "https://www.technologyreview.com",
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

ENTREPRENEURSHIP_NEWS_SOURCES = [
    # === Core Entrepreneurship Sources ===
    {
        "name": "Entrepreneur Magazine",
        "rss_url": "https://www.entrepreneur.com/latest.rss",
        "url": "https://www.entrepreneur.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Inc.",
        "rss_url": "https://www.inc.com/rss.xml",
        "url": "https://www.inc.com",
        "category": "entrepreneurship_news"
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
        "name": "Indie Hackers",
        "rss_url": "https://www.indiehackers.com/feed.xml",
        "url": "https://www.indiehackers.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "SaaStr",
        "rss_url": "https://www.saastr.com/feed/",
        "url": "https://www.saastr.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "A16Z Blog",
        "rss_url": "https://a16z.com/feed/",
        "url": "https://a16z.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "First Round Review",
        "rss_url": "https://review.firstround.com/feed.xml",
        "url": "https://review.firstround.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "TechCrunch Startups",
        "rss_url": "https://techcrunch.com/category/startups/feed/",
        "url": "https://techcrunch.com/category/startups/",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Entrepreneur Asia Pacific",
        "rss_url": "https://www.entrepreneur.com/asiapacific/rss",
        "url": "https://www.entrepreneur.com/asiapacific",
        "category": "entrepreneurship_news"
    },
    
    # === Neuroscience & Cognitive Science for Self-Improvement ===
    {
        "name": "Neuroleadership Institute",
        "rss_url": "https://neuroleadership.com/your-brain-at-work/feed/",
        "url": "https://neuroleadership.com/your-brain-at-work",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Mindful",
        "rss_url": "https://www.mindful.org/feed/",
        "url": "https://www.mindful.org",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Brain Pickings",
        "rss_url": "https://www.brainpickings.org/feed/",
        "url": "https://www.brainpickings.org",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Farnam Street",
        "rss_url": "https://fs.blog/feed/",
        "url": "https://fs.blog",
        "category": "entrepreneurship_news"
    },
    
    # === Selected Tech News Sources ===
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "url": "https://techcrunch.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "VentureBeat",
        "rss_url": "https://venturebeat.com/feed/",
        "url": "https://venturebeat.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "MIT Technology Review",
        "rss_url": "https://www.technologyreview.com/feed/",
        "url": "https://www.technologyreview.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "The Next Web",
        "rss_url": "https://thenextweb.com/feed/",
        "url": "https://thenextweb.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Wired",
        "rss_url": "https://www.wired.com/feed/rss",
        "url": "https://www.wired.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "The Verge",
        "rss_url": "https://www.theverge.com/rss/index.xml",
        "url": "https://www.theverge.com",
        "category": "entrepreneurship_news"
    },
    
    # === Selected Business News Sources ===
    {
        "name": "Forbes Entrepreneurs",
        "rss_url": "https://www.forbes.com/entrepreneurs/feed/",
        "url": "https://www.forbes.com/entrepreneurs/",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Harvard Business Review",
        "rss_url": "https://hbr.org/feed",
        "url": "https://hbr.org",
        "category": "entrepreneurship_news"
    },
    {
        "name": "The Hustle",
        "rss_url": "https://thehustle.co/feed/",
        "url": "https://thehustle.co",
        "category": "entrepreneurship_news"
    },
    {
        "name": "McKinsey Insights",
        "rss_url": "https://www.mckinsey.com/insights/rss.aspx",
        "url": "https://www.mckinsey.com/insights",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Bloomberg Entrepreneurs",
        "rss_url": "https://feed.bloomberg.com/feed/entrepreneurs",
        "url": "https://www.bloomberg.com/entrepreneurs",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Business Insider",
        "rss_url": "https://www.businessinsider.com/rss",
        "url": "https://www.businessinsider.com",
        "category": "business_news"
    },
    
    # === Lifestyle News for Young Entrepreneurs ===
    {
        "name": "Fast Company",
        "rss_url": "https://www.fastcompany.com/feed",
        "url": "https://www.fastcompany.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Forbes Under 30",
        "rss_url": "https://www.forbes.com/30-under-30/feed/",
        "url": "https://www.forbes.com/30-under-30/",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Success Magazine",
        "rss_url": "https://www.success.com/feed/",
        "url": "https://www.success.com",
        "category": "entrepreneurship_news"
    },
    
    # === Tech & Business Celebrities/Popular People ===
    {
        "name": "Tech Meme",
        "rss_url": "https://www.techmeme.com/feed.xml",
        "url": "https://www.techmeme.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "GeekWire",
        "rss_url": "https://www.geekwire.com/feed/",
        "url": "https://www.geekwire.com",
        "category": "entrepreneurship_news"
    },
    
    # === Social Media & Funny Tech/Startup Content ===
    {
        "name": "AI Boom",
        "rss_url": "https://ai-data-base.com/feed",
        "url": "https://ai-data-base.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Mashable Startups",
        "rss_url": "https://mashable.com/feeds/rss/startups",
        "url": "https://mashable.com/startups",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Morning Brew",
        "rss_url": "https://www.morningbrew.com/feed",
        "url": "https://www.morningbrew.com",
        "category": "entrepreneurship_news"
    },
    {
        "name": "Product Hunt Daily",
        "rss_url": "https://www.producthunt.com/feed",
        "url": "https://www.producthunt.com",
        "category": "entrepreneurship_news"
    }
]

# All news sources combined
ALL_NEWS_SOURCES = TECH_NEWS_SOURCES + BUSINESS_NEWS_SOURCES + ENTREPRENEURSHIP_NEWS_SOURCES

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