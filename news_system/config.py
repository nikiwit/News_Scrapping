#!/usr/bin/env python3
# config.py - Enhanced configuration with JavaScript rendering and content discovery

import os
from pathlib import Path

# System paths
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
STATE_DIR = BASE_DIR / "state"
SUMMARIES_DIR = BASE_DIR / "news_summaries"

# Create necessary directories
for dir_path in [DATA_DIR, STATE_DIR, SUMMARIES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Create category directories
CATEGORIES = ["business_news", "it_news", "entrepreneurship_news", "lifestyle_news"]
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

LIFESTYLE_NEWS_SOURCES = [
    # Popular and Active Lifestyle Blogs
    {
        "name": "Cup of Jo",
        "rss_url": "https://feeds.feedburner.com/blogspot/bboSV",
        "url": "https://cupofjo.com",
        "category": "manual_news_system"
    },
    {
        "name": "Lifehacker",
        "rss_url": "https://lifehacker.com/rss",
        "url": "https://lifehacker.com",
        "category": "manual_news_system"
    },
    
    # Health & Wellness
    {
        "name": "MindBodyGreen",
        "rss_url": "https://www.mindbodygreen.com/rss/feed.xml",
        "url": "https://www.mindbodygreen.com/health",
        "category": "manual_news_system"
    },
    {
        "name": "Health eHealth Square",
        "rss_url": "https://ehealthsquare.com/feed",
        "url": "https://ehealthsquare.com",
        "category": "manual_news_system"
    },
    
    # Self-Improvement
    {
        "name": "Tiny Buddha",
        "rss_url": "https://tinybuddha.com/feed/",
        "url": "https://tinybuddha.com",
        "category": "manual_news_system"
    },
    {
        "name": "BrainFlow",
        "rss_url": "https://brainflow.co/feed",
        "url": "https://brainflow.co",
        "category": "manual_news_system"
    },
    
    # Science & Knowledge
    {
        "name": "Science Daily",
        "rss_url": "https://www.sciencedaily.com/rss/top/health.xml",
        "url": "https://www.sciencedaily.com",
        "category": "manual_news_system"
    },
    
    # Fitness & Nutrition
    {
        "name": "The Betty Rocker",
        "rss_url": "https://thebettyrocker.com/feed",
        "url": "https://thebettyrocker.com",
        "category": "manual_news_system"
    },
    
    # Home & Design
    {
        "name": "Apartment Therapy",
        "rss_url": "https://www.apartmenttherapy.com/main.rss",
        "url": "https://www.apartmenttherapy.com",
        "category": "manual_news_system"
    },
    
    # Entertaining Content
    {
        "name": "The Onion",
        "rss_url": "https://www.theonion.com/rss",
        "url": "https://www.theonion.com",
        "category": "manual_news_system"
    }
]

# All news sources combined
ALL_NEWS_SOURCES = TECH_NEWS_SOURCES + BUSINESS_NEWS_SOURCES + ENTREPRENEURSHIP_NEWS_SOURCES + LIFESTYLE_NEWS_SOURCES

# =============================================================================
# TELEGRAM CONFIGURATION (unchanged)
# =============================================================================

TELEGRAM_BOT_TOKENS = {
}

TELEGRAM_CHANNELS = {
}

BOT_CHANNEL_MAPPING = {
}

# =============================================================================
# LLM CONFIGURATION (unchanged)
# =============================================================================

LLM_API_KEY = os.environ.get("LLM_API_KEY", "your_api_key_here")
LLM_API_URL = "https://api.openai.com/v1/completions"