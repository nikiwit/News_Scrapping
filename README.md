# News Scrapping Automation

A robust news scraping and automation system that collects, processes, and posts news articles to Telegram channels. The system supports multiple news categories including IT, Business, Entrepreneurship, and Lifestyle news.

## 🌟 Features

- **Multi-Category News Scraping**
  - IT News
  - Business News
  - Entrepreneurship News
  - Lifestyle News

- **Advanced Scraping Capabilities**
  - Configurable time-based scraping (6h to 10 days)
  - JavaScript rendering support
  - Rate limiting and request management
  - Content extraction and processing
  - Duplicate detection

- **Automation Features**
  - Scheduled scraping
  - Automated posting to Telegram (possible with modification)
  - Content filtering and categorization
  - Error handling and retry mechanisms

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Playwright (for JavaScript rendering)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/nikiwit/News_Scrapping.git
cd News_Scrapping
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Set up your environment variables:
```bash
# Edit .env with your configuration
```

## 📝 Usage

### Basic Scraping

```bash
cd news_system
```

```bash
# Run individual scrapers with default settings (24 hours lookback)
python -m scrapers.it_news
python -m scrapers.business_news
python -m scrapers.entrepreneurship_news
python -m scrapers.lifestyle_news
```

### Time-Based Scraping

```bash
# Look back specific hours
python -m scrapers.it_news --past_hours 6    # Last 6 hours
python -m scrapers.it_news --past_hours 24   # Last 24 hours (default)
python -m scrapers.it_news --past_hours 168  # Last week
```

## 📁 Project Structure
```
Telegram_News_Automation/
├── news_system/                      # Main system code
│   ├── main.py                       # Entry point
│   ├── config.py                     # Base configuration settings
│   ├── logging_setup.py              # Logging configuration
│   ├── scrapers/                     # News scrapers for different categories
│   │   ├── base_scraper.py           # Base scraper class
│   │   ├── it_news.py                # IT news scraper
│   │   ├── business_news.py          # Business news scraper
│   │   ├── entrepreneurship_news.py  # Entrepreneurship news scraper
│   │   └── lifestyle_news.py         # Lifestyle news scraper
│   ├── utils/                        # Utility functions
│   │   ├── browser_manager.py        # Browser automation
│   │   ├── js_renderer.py            # JavaScript rendering
│   │   ├── content_discoverer.py     # Content discovery
│   │   ├── url_patterns.py           # URL pattern matching
│   │   ├── rate_limiter.py           # Rate limiting
│   │   ├── robots_checker.py         # Robots.txt compliance
│   │   ├── browser_mimicry.py        # Browser fingerprinting
│   │   ├── session_manager.py        # Session management
│   │   └── request_manager.py        # Request handling
│   ├── llm/                          # Language Model integration
│   │   ├── prompts.py                # LLM prompts
│   │   └── formatter.py              # Content formatting
│   ├── telegram_client/              # Telegram integration
│   │   ├── bot.py                    # Telegram bot
│   │   └── channel_manager.py        # Channel management
│   ├── data/                         # Data directory
│   ├── logs/                         # System logs
│   └── state/                        # System state
├── json_scrapping/                   # JSON processing utilities
├── requirements.txt                  # Project dependencies
├── .gitignore                        # Git ignore rules
└── news_basic_commands.md            # Command reference
└── .env                              # Your environment variables (no needed without automation for Telegram)
```

## Notes and Recommendations

You may want to consider removing or changing some of the sources from the list in config.py to include your own desired ones or to avoid collisions and issues with the sources that give timeouts or errors.