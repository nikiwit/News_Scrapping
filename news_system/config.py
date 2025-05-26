#!/usr/bin/env python3
# config.py - Enhanced configuration with JavaScript rendering and content discovery

import os
from pathlib import Path

# System paths
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
STATE_DIR = BASE_DIR / "state"

# Create necessary directories
for dir_path in [DATA_DIR, STATE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Create category directories
CATEGORIES = ["business_news", "it_news", "entrepreneurship_news", "russian_news"]
for category in CATEGORIES:
    (DATA_DIR / category).mkdir(exist_ok=True)

# =============================================================================
# ENHANCED SCRAPING CONFIGURATION
# =============================================================================

# Basic scraping settings
USER_AGENT = "NewsBot/1.0 (+https://example.com/bot; contact@example.com)"
DEFAULT_SCRAPE_INTERVAL_HOURS = 3

# =============================================================================
# REQUEST MANAGER CONFIGURATION (from Step 1)
# =============================================================================

REQUEST_MANAGER_CONFIG = {
    # Basic request settings
    'timeout': 30,
    'max_retries': 3,
    'backoff_factor': 0.3,
    
    # Anti-detection settings
    'bypass_robots': True,  # Set to True for aggressive scraping
    
    # Session configuration
    'session_config': {
        'session_lifetime': 3600,  # 1 hour
        'max_sessions': 50,
        'connection_pool_size': 10,
        'connection_pool_maxsize': 20,
        'retry_total': 3,
        'retry_backoff_factor': 0.3,
        'retry_status_codes': [500, 502, 503, 504]
    },
    
    # Browser mimicry configuration
    'browser_config': {
        'rotation_enabled': True,
        'profile_rotation_threshold': 25
    },
    
    # Rate limiting configuration
    'rate_limit_config': {
        'default_delay': 5.0,  # Slower requests
        'max_delay': 120.0,
        'min_delay': 2.0,
        'adaptive_enabled': True,
        'response_time_threshold': 10.0,  # More lenient
        'block_penalty_multiplier': 2.0,  # Less penalty
        'success_reward_factor': 0.95,   # Slower improvement
        'jitter_enabled': True,
        'jitter_range': 0.5,  # More randomness
        'burst_size': 1,      # No burst requests
        'burst_window': 120
    },
    
    # Robots.txt configuration
    'robots_config': {
        'respect_robots': False,  # Set to False to bypass robots.txt
        'cache_ttl': 3600,
        'request_timeout': 10,
        'max_retries': 2,
        'aggressive_mode': True,
        'domain_overrides': {},
        'whitelist_domains': [
            'techcrunch.com', 'theverge.com', 'arstechnica.com',
            'venturebeat.com', 'wired.com', 'engadget.com'
        ],
        'blacklist_domains': []
    }
}

# =============================================================================
# JAVASCRIPT RENDERING CONFIGURATION (Step 2)
# =============================================================================

# Browser Manager Configuration
BROWSER_MANAGER_CONFIG = {
    'max_browsers': 3,
    'max_contexts_per_browser': 5,
    'browser_lifetime': 1800,  # 30 minutes
    'context_lifetime': 600,   # 10 minutes
    'headless': True,
    'browser_type': 'chromium',  # chromium, firefox, webkit
    'stealth_mode': True,
    'default_timeout': 30000,  # 30 seconds
    'wait_for_network': True,
    'block_resources': ['image', 'font', 'media']  # Block to speed up loading
}

# JavaScript Renderer Configuration  
JS_RENDERER_CONFIG = {
    'auto_detect': True,  # Automatically detect when JS is needed
    'js_threshold': 0.3,  # Content difference threshold for JS detection
    'max_render_time': 30,
    'cache_results': True,
    'cache_ttl': 3600,  # 1 hour
    
    # Browser configuration
    'browser_config': BROWSER_MANAGER_CONFIG,
    
    # Force JS rendering for these domains (always render with JS)
    'force_js_domains': [
        'medium.com', 'notion.so', 'airtable.com',
        'trello.com', 'asana.com', 'slack.com',
        'discord.com', 'figma.com', 'canva.com',
        'spotify.com', 'netflix.com'
    ],
    
    # Never use JS for these domains (always use basic HTTP)
    'never_js_domains': [
        'reddit.com',  # RSS works fine
        'hackernews.ycombinator.com',  # Simple HTML
    ]
}

# =============================================================================
# CONTENT DISCOVERY CONFIGURATION (Step 2)
# =============================================================================

CONTENT_DISCOVERY_CONFIG = {
    'max_pages_per_source': 10,
    'max_articles_per_source': 50,
    'discovery_timeout': 300,  # 5 minutes
    'max_article_age_days': 7,
    
    # Article URL patterns to recognize
    'article_url_patterns': [
        r'/article/', r'/post/', r'/news/', r'/story/',
        r'/blog/', r'/press/', r'/release/', r'/update/',
        r'/feature/', r'/report/', r'/interview/', r'/review/',
        r'/\d{4}/\d{2}/', r'/\d{4}-\d{2}-\d{2}/',
        r'/\d{4}/\d{2}/\d{2}/', r'/articles/\d+',
        r'/posts/\d+', r'/news/\d+'
    ]
}

# URL Patterns Configuration
URL_PATTERNS_CONFIG = {
    'enable_pattern_generation': True,
    'max_generated_urls': 100,
    'date_range_days': 7
}

# =============================================================================
# SOURCE-SPECIFIC CONFIGURATIONS
# =============================================================================

# Sources that require JavaScript rendering
JS_REQUIRED_SOURCES = [
    'medium.com', 'dev.to', 'hashnode.com',
    'substack.com', 'ghost.org', 'notion.site'
]

# Sources that have good sitemaps
SITEMAP_FRIENDLY_SOURCES = [
    'techcrunch.com', 'theverge.com', 'arstechnica.com',
    'wired.com', 'engadget.com', 'venturebeat.com'
]

# Sources known for archive pages
ARCHIVE_FRIENDLY_SOURCES = [
    'bbc.com', 'cnn.com', 'reuters.com',
    'nytimes.com', 'wsj.com', 'guardian.com'
]

# Content discovery strategies per source type
SOURCE_DISCOVERY_STRATEGIES = {
    'tech_blogs': ['rss', 'sitemap', 'homepage'],
    'news_sites': ['rss', 'sitemap', 'archives', 'categories'],
    'personal_blogs': ['rss', 'archives', 'patterns'],
    'corporate_blogs': ['sitemap', 'categories', 'patterns']
}

# Source-specific configurations
SOURCE_SPECIFIC_CONFIG = {
    'techcrunch.com': {
        'js_required': False,
        'discovery_strategies': ['rss', 'sitemap', 'categories'],
        'rate_limit_override': 1.5,
        'custom_selectors': {
            'title': 'h1.post-title, .article-title',
            'content': '.article-content, .post-content',
            'date': '.post-date, time[datetime]'
        }
    },
    'medium.com': {
        'js_required': True,
        'discovery_strategies': ['sitemap', 'patterns'],
        'rate_limit_override': 3.0,
        'js_wait_selector': 'article',
        'js_wait_time': 3000
    },
    'dev.to': {
        'js_required': True,
        'discovery_strategies': ['rss', 'patterns'],
        'rate_limit_override': 2.0,
        'js_wait_selector': '.crayons-article',
        'js_wait_time': 2000
    },
    'hackernoon.com': {
        'js_required': False,
        'discovery_strategies': ['rss', 'sitemap'],
        'rate_limit_override': 2.5
    }
}

# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================

# Concurrent processing limits
CONCURRENCY_CONFIG = {
    'max_concurrent_sources': 5,
    'max_concurrent_articles': 10,
    'max_concurrent_js_renders': 2,
    'request_semaphore_limit': 20
}

# Caching configuration
CACHE_CONFIG = {
    'enable_content_cache': True,
    'content_cache_ttl': 1800,  # 30 minutes
    'enable_discovery_cache': True,
    'discovery_cache_ttl': 3600,  # 1 hour
    'enable_js_detection_cache': True,
    'js_detection_cache_ttl': 7200,  # 2 hours
    'max_cache_size_mb': 100
}

# =============================================================================
# LEGACY SETTINGS (for backward compatibility)
# =============================================================================

RATE_LIMIT_SECONDS = REQUEST_MANAGER_CONFIG['rate_limit_config']['default_delay']

# =============================================================================
# NEWS SOURCES CONFIGURATION (Enhanced with discovery metadata)
# =============================================================================

TECH_NEWS_SOURCES = [
    {
        "name": "The Verge",
        "rss_url": "https://www.theverge.com/rss/index.xml",
        "url": "https://www.theverge.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "url": "https://techcrunch.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap", "categories"],
        "js_required": False
    },
    {
        "name": "Ars Technica",
        "rss_url": "https://feeds.arstechnica.com/arstechnica/index",
        "url": "https://arstechnica.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "Hacker News",
        "rss_url": "https://news.ycombinator.com/rss",
        "url": "https://news.ycombinator.com",
        "category": "it_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    {
        "name": "ZDNet",
        "rss_url": "https://www.zdnet.com/news/rss.xml",
        "url": "https://www.zdnet.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    {
        "name": "VentureBeat",
        "rss_url": "https://feeds.venturebeat.com/VentureBeat",
        "url": "https://venturebeat.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "GitHub Blog",
        "rss_url": "https://github.blog/feed/",
        "url": "https://github.blog",
        "category": "it_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    {
        "name": "Wired",
        "rss_url": "https://www.wired.com/feed/rss",
        "url": "https://www.wired.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "MIT Technology Review",
        "rss_url": "https://www.technologyreview.com/topnews.rss",
        "url": "https://www.technologyreview.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    {
        "name": "Engadget",
        "rss_url": "https://www.engadget.com/rss.xml",
        "url": "https://www.engadget.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "The Next Web",
        "rss_url": "http://feeds2.feedburner.com/thenextweb",
        "url": "https://thenextweb.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "homepage"],
        "js_required": False
    },
    {
        "name": "Slashdot",
        "rss_url": "https://rss.slashdot.org/Slashdot/slashdotMain",
        "url": "https://slashdot.org",
        "category": "it_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    {
        "name": "TechRadar",
        "rss_url": "https://feeds.webservice.techradar.com/rss/new",
        "url": "https://www.techradar.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    {
        "name": "TechRepublic",
        "rss_url": "https://www.techrepublic.com/rssfeeds/articles/?feedType=rssfeeds&sort=latest",
        "url": "https://www.techrepublic.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    {
        "name": "CNET News",
        "rss_url": "https://www.cnet.com/rss/news/",
        "url": "https://www.cnet.com/news",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "Tom's Hardware",
        "rss_url": "https://www.tomshardware.com/feeds/rss2/all.xml",
        "url": "https://www.tomshardware.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "PCWorld",
        "rss_url": "http://feeds.pcworld.com/pcworld/latestnews",
        "url": "https://www.pcworld.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    {
        "name": "Computerworld",
        "rss_url": "https://www.computerworld.com/feed/",
        "url": "https://www.computerworld.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "TechSpot",
        "rss_url": "https://www.techspot.com/backend.xml",
        "url": "https://www.techspot.com",
        "category": "it_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    {
        "name": "BetaNews",
        "rss_url": "https://betanews.com/feed/",
        "url": "https://betanews.com",
        "category": "it_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    {
        "name": "TechMeme",
        "rss_url": "https://www.techmeme.com/feed.xml",
        "url": "https://www.techmeme.com",
        "category": "it_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    {
        "name": "GeekWire",
        "rss_url": "https://www.geekwire.com/feed/",
        "url": "https://www.geekwire.com",
        "category": "it_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    # Add some JS-heavy sources for testing
    {
        "name": "Dev.to",
        "rss_url": "https://dev.to/feed",
        "url": "https://dev.to",
        "category": "it_news",
        "discovery_strategies": ["rss", "patterns"],
        "js_required": True
    },
    {
        "name": "Hashnode",
        "url": "https://hashnode.com",
        "category": "it_news",
        "discovery_strategies": ["patterns", "sitemap"],
        "js_required": True
    }
]

# Business and other sources (simplified for brevity)
BUSINESS_NEWS_SOURCES = [
    {
        "name": "Forbes",
        "rss_url": "https://www.forbes.com/business/feed/",
        "url": "https://www.forbes.com/business/",
        "category": "business_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    {
        "name": "Fortune",
        "rss_url": "https://fortune.com/feed/",
        "url": "https://fortune.com",
        "category": "business_news",
        "discovery_strategies": ["rss", "archives"],
        "js_required": False
    },
    # ... (other business sources)
]

ENTREPRENEURSHIP_NEWS_SOURCES = [
    {
        "name": "Entrepreneur Magazine",
        "rss_url": "https://www.entrepreneur.com/latest/feed",
        "url": "https://www.entrepreneur.com",
        "category": "entrepreneurship_news",
        "discovery_strategies": ["rss", "sitemap"],
        "js_required": False
    },
    # ... (other entrepreneurship sources)
]

RUSSIAN_NEWS_SOURCES = [
    {
        "name": "RT News",
        "rss_url": "https://www.rt.com/rss/",
        "url": "https://www.rt.com",
        "category": "russian_news",
        "discovery_strategies": ["rss"],
        "js_required": False
    },
    # ... (other Russian sources)
]

# All news sources combined
ALL_NEWS_SOURCES = TECH_NEWS_SOURCES + BUSINESS_NEWS_SOURCES + ENTREPRENEURSHIP_NEWS_SOURCES + RUSSIAN_NEWS_SOURCES

# =============================================================================
# TELEGRAM CONFIGURATION (unchanged)
# =============================================================================

TELEGRAM_BOT_TOKENS = {
    "business_news": os.environ.get("BUSINESS_BOT_TOKEN", "7753587635:AAGG8-qTogDPtCSL83mr7FBRgIKdijvz89Q"),
    "it_news": os.environ.get("IT_BOT_TOKEN", "7797865654:AAHIBliz3W_GrOy9ruD6vXwoW5OcLgbhifw"),
    "entrepreneurship_news": os.environ.get("ENTREPRENEUR_BOT_TOKEN", "7763104070:AAE2RPRGcB7neO1Y8AWt5MVzP9GmVtxUf6g"),
    "russian_news": os.environ.get("RUSSIAN_BOT_TOKEN", "your_russian_bot_token_here")
}

TELEGRAM_CHANNELS = {
    "business_news": "@business_news_hub",
    "it_news": "@it_geeks_hub",
    "entrepreneurship_news": "@entrepreneurship_hub",
    "russian_news": "@russian_news_hub"
}

BOT_CHANNEL_MAPPING = {
    "business_news": "business_news",
    "it_news": "it_news",
    "entrepreneurship_news": "entrepreneurship_news",
    "russian_news": "russian_news"
}

# =============================================================================
# LLM CONFIGURATION (unchanged)
# =============================================================================

LLM_API_KEY = os.environ.get("LLM_API_KEY", "your_api_key_here")
LLM_API_URL = "https://api.openai.com/v1/completions"