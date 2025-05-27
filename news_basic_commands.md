# Enhanced News Scraper - Complete Command Reference 📚

## Table of Contents
- [Individual Scraper Commands](#individual-scraper-commands)
- [Testing & Diagnostics](#testing--diagnostics)
- [Main System Commands](#main-system-commands)
- [File & Data Management](#file--data-management)
- [Logging Commands](#logging-commands)
- [Configuration & Setup](#configuration--setup)
- [Development & Debug](#development--debug)
- [System Status](#system-status)
- [Batch Operations](#batch-operations)
- [Utility Commands](#utility-commands)
- [Monitoring & Analytics](#monitoring--analytics)
- [Common Usage Patterns](#common-usage-patterns)

---

## 🚀 Individual Scraper Commands

### Basic Scraping Commands
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
python -m scrapers.it_news --past_hours 12   # Last 12 hours  
python -m scrapers.it_news --past_hours 24   # Last 24 hours (default)
python -m scrapers.it_news --past_hours 48   # Last 48 hours
python -m scrapers.it_news --past_hours 72   # Last 72 hours
python -m scrapers.it_news --past_hours 168  # Last week

# For testing new sources or after downtime
python -m scrapers.it_news --past_hours 240  # Last 10 days
```

### All Scrapers with Variations
```bash
# IT News
python -m scrapers.it_news --past_hours 24
python -m scrapers.it_news --past_hours 48
python -m scrapers.it_news --past_hours 72

# Business News  
python -m scrapers.business_news --past_hours 24
python -m scrapers.business_news --past_hours 48
python -m scrapers.business_news --past_hours 72

# Entrepreneurship News
python -m scrapers.entrepreneurship_news --past_hours 24
python -m scrapers.entrepreneurship_news --past_hours 48  
python -m scrapers.entrepreneurship_news --past_hours 72

# Lifestyle News
python -m scrapers.lifestyle_news --past_hours 24
python -m scrapers.lifestyle_news --past_hours 48
python -m scrapers.lifestyle_news --past_hours 72
```

---

## 🧪 Testing & Diagnostics

### Quick Single-Source Tests
```bash
# Create and run quick tests for specific sources
python -c "
from scrapers.it_news import ITNewsScraper
scraper = ITNewsScraper()
articles = scraper.scrape(past_hours=48)
print(f'Found {len(articles)} articles')
"

# Test specific scraper classes
python -c "
from scrapers.business_news import BusinessNewsScraper
scraper = BusinessNewsScraper()
articles = scraper.scrape(past_hours=24)
print(f'Business: {len(articles)} articles')
"
```

### Component Testing
```bash
# Test request manager
python -c "
from utils.request_manager import RequestManager
import config
rm = RequestManager(config.REQUEST_MANAGER_CONFIG)
resp = rm.get('https://httpbin.org/get')
print(f'Status: {resp.status_code if resp else \"Failed\"}')
print(rm.get_stats())
"

# Test rate limiter
python -c "
from utils.rate_limiter import RateLimiter
rl = RateLimiter({'default_delay': 1.0})
import time
start = time.time()
rl.wait('https://example.com')
rl.wait('https://example.com')  
print(f'Two requests took: {time.time() - start:.2f}s')
"
```

---

## 📊 Main System Commands

### Using main.py (if available)
```bash
# Full system operations
python main.py --scrape --hours 24                       # Scrape all categories
python main.py --scrape --hours 48 --category it_news    # Specific category
python main.py --post --count 1                          # Post latest articles
python main.py --setup                                   # Setup Telegram channels
python main.py --schedule --hours 3                      # Run on schedule

# Combined operations
python main.py --scrape --post --hours 24                # Scrape and post
python main.py --scrape --hours 48 --post --count 2      # Scrape 48h, post 2 articles
```

### Direct Main System Calls
```bash
# If main.py is configured for your system
python main.py --scrape --category it_news --hours 24
python main.py --scrape --category business_news --hours 48
python main.py --scrape --category entrepreneurship_news --hours 72
```

---

## 📁 File & Data Management

### Check Results
```bash
# List generated data files
ls -la data/*/*/*/*/extracted_*.json          # All article files
ls -la data/*/*/*/*/batch.json               # Batch files

# Check today's data  
ls -la data/$(date +%d_%m_%Y)/*/              # Today's scrapes

# Count articles found
find data -name "extracted_*.json" | wc -l    # Total articles
find data -name "extracted_*.json" -mtime -1 | wc -l  # Last 24 hours

# Check specific categories
find data -path "*/it_news/extracted_*.json" | wc -l
find data -path "*/business_news/extracted_*.json" | wc -l
find data -path "*/entrepreneurship_news/extracted_*.json" | wc -l
```

### View Article Content
```bash
# View specific articles
cat data/*/*/*/*/extracted_1.json | head -20         # First article preview
cat data/*/*/*/*/extracted_1.json | jq '.title'      # Just title (if jq installed)
cat data/*/*/*/*/batch.json | jq '.[0].title'        # First title from batch

# View article summaries
grep -h "\"title\"" data/*/*/*/*/extracted_*.json | head -10

# Show article sources
grep -h "\"source\"" data/*/*/*/*/extracted_*.json | sort | uniq -c

# View articles by category
find data -path "*/it_news/extracted_*.json" -exec grep "\"title\"" {} \; | head -5
find data -path "*/business_news/extracted_*.json" -exec grep "\"title\"" {} \; | head -5
```

### Data Organization
```bash
# Show data structure
tree data/ | head -20                                # Directory structure
du -sh data/*                                       # Data usage by date
du -sh data/*/*                                     # Data usage by date/time
du -sh data/*/*/*                                   # Data usage by category

# Find latest articles
find data -name "extracted_*.json" -mtime -1 -exec ls -la {} \; | head -10

# Articles by time period
find data -name "extracted_*.json" -mtime -1 | wc -l     # Last 24 hours
find data -name "extracted_*.json" -mtime -7 | wc -l     # Last week
find data -name "extracted_*.json" -mtime -30 | wc -l    # Last month
```

### Clean Up Old Data
```bash
# Remove old data (be careful!)
find data -name "*.json" -mtime +30 -delete           # Delete files older than 30 days
find data -type d -empty -delete                      # Remove empty directories

# Archive old data
tar -czf data_archive_$(date +%Y%m%d).tar.gz data/

# Clean up specific categories
find data -path "*/it_news/*.json" -mtime +30 -delete
find data -path "*/business_news/*.json" -mtime +30 -delete
```

---

## 📜 Logging Commands

### View Logs
```bash
# View today's logs
ls -la logs/$(date +%Y%m%d)/                          # Today's log files
tail -f logs/$(date +%Y%m%d)/*.log                    # Follow latest log

# View specific scraper logs
tail -f logs/*/it_*.log                               # IT scraper logs
tail -f logs/*/business_*.log                         # Business scraper logs
tail -f logs/*/entrepreneurship_*.log                 # Entrepreneurship scraper logs

# View recent logs
find logs -name "*.log" -mtime -1 -exec tail -20 {} \;
```

### Log Analysis
```bash
# Search logs for important events
grep -r "SUCCESS\|Found.*articles" logs/              # Success messages
grep -r "ERROR\|Failed" logs/                         # Error messages
grep -r "Blocked" logs/                               # Blocking detection
grep -r "Enhanced" logs/                              # Enhanced features

# Count articles found per scraper
grep -r "Found.*articles" logs/ | grep -o "[0-9]* articles" | sort | uniq -c

# Check for common errors
grep -r "Error" logs/ | cut -d: -f3 | sort | uniq -c

# Monitor success rates
grep -r "Success\|Failed" logs/ | tail -20

# Source-specific analysis
grep -r "articles from" logs/ | grep -o "[0-9]* articles from [^\"]*" | sort | uniq -c | sort -nr
```

### Real-time Log Monitoring
```bash
# Monitor all logs in real-time
tail -f logs/*/*.log

# Monitor specific scraper
tail -f logs/*/$(date +%H%M%S).log

# Monitor for errors
tail -f logs/*/*.log | grep -i error

# Monitor for success
tail -f logs/*/*.log | grep -i "found.*articles"
```

---

## ⚙️ Configuration & Setup

### Test Configuration
```bash
# Test config syntax
python -c "import config; print('✅ Config OK')"

# List configured sources
python -c "
import config
print(f'IT sources: {len(config.TECH_NEWS_SOURCES)}')
print(f'Business sources: {len(config.BUSINESS_NEWS_SOURCES)}')
print(f'Entrepreneurship sources: {len(config.ENTREPRENEURSHIP_NEWS_SOURCES)}')
print(f'Total sources: {len(config.ALL_NEWS_SOURCES)}')
"

# Show config details
python -c "
import config
print('Enhanced Features:')
print(f'- Request Manager: {\"✅\" if hasattr(config, \"REQUEST_MANAGER_CONFIG\") else \"❌\"}')
print(f'- Rate Limiting: {\"✅\" if hasattr(config, \"RATE_LIMIT_SECONDS\") else \"❌\"}')
print(f'- Telegram Config: {\"✅\" if hasattr(config, \"TELEGRAM_BOT_TOKENS\") else \"❌\"}')
"
```

### Validate Sources
```bash
# Test RSS feeds
python -c "
import requests
import config
print('Testing IT News Sources:')
for src in config.TECH_NEWS_SOURCES[:5]:
    if src.get('rss_url'):
        try:
            r = requests.get(src['rss_url'], timeout=10)
            print(f'  {src[\"name\"]}: {r.status_code}')
        except Exception as e:
            print(f'  {src[\"name\"]}: ERROR - {e}')
"

# Test source URLs
python -c "
import requests
import config
print('Testing Business News Sources:')
for src in config.BUSINESS_NEWS_SOURCES[:3]:
    try:
        r = requests.get(src['url'], timeout=10)
        print(f'  {src[\"name\"]}: {r.status_code}')
    except Exception as e:
        print(f'  {src[\"name\"]}: ERROR - {e}')
"
```

### Configuration Management
```bash
# Backup configuration
cp config.py config_backup_$(date +%Y%m%d).py

# Show current settings
python -c "
import config
print(f'Rate limit: {config.RATE_LIMIT_SECONDS}s')
print(f'Scrape interval: {config.DEFAULT_SCRAPE_INTERVAL_HOURS}h')
print(f'Categories: {config.CATEGORIES}')
"

# Validate new sources before adding
python -c "
import requests
test_url = 'https://example.com/rss'
r = requests.get(test_url, timeout=10)
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get(\"content-type\", \"Unknown\")}')
"
```

---

## 🔧 Development & Debug

### System Health Check
```bash
# Check if all components import correctly
python -c "
try:
    from scrapers.it_news import ITNewsScraper
    from scrapers.business_news import BusinessNewsScraper
    from utils.request_manager import RequestManager
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
"

# Test individual components
python -c "
from utils.request_manager import RequestManager
from utils.rate_limiter import RateLimiter
import config
rm = RequestManager(config.REQUEST_MANAGER_CONFIG)
print('✅ Components loaded successfully')
print(f'Request Manager Stats: {rm.get_stats()}')
"
```

### Debug Individual Scrapers
```bash
# Debug IT news scraper
python -c "
from scrapers.it_news import ITNewsScraper
import logging
logging.basicConfig(level=logging.DEBUG)
scraper = ITNewsScraper()
print(f'Sources: {len(scraper.news_sources)}')
print(f'Category: {scraper.category}')
"

# Test scraper initialization
python -c "
from scrapers.business_news import BusinessNewsScraper
scraper = BusinessNewsScraper()
print(f'✅ {scraper.__class__.__name__} initialized')
print(f'Data dir: {scraper.data_dir}')
print(f'Sources: {len(scraper.news_sources)}')
"
```

### Memory & Performance Monitoring
```bash
# Monitor memory usage during scraping
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory before: {process.memory_info().rss / 1024 / 1024:.1f} MB')
" && python -m scrapers.it_news --past_hours 24 && python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory after: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# Time scraping operations
time python -m scrapers.it_news --past_hours 24
time python -m scrapers.business_news --past_hours 24
time python test_all_enhanced_scrapers.py
```

### Debug Enhanced Features
```bash
# Test request manager with verbose output
python -c "
from utils.request_manager import RequestManager
import config
import logging
logging.basicConfig(level=logging.DEBUG)
rm = RequestManager(config.REQUEST_MANAGER_CONFIG)
resp = rm.get('https://httpbin.org/get')
print(f'Response: {resp.status_code if resp else \"Failed\"}')
print(f'Stats: {rm.get_stats()}')
"
```

---

## 🚦 System Status

### Quick Health Check
```bash
# One-liner system status
echo "📊 System Status:" && \
echo "IT sources: $(python -c 'import config; print(len(config.TECH_NEWS_SOURCES))')" && \
echo "Business sources: $(python -c 'import config; print(len(config.BUSINESS_NEWS_SOURCES))')" && \
echo "Data files: $(find data -name '*.json' | wc -l)" && \
echo "Log files: $(find logs -name '*.log' | wc -l)" && \
echo "Disk usage: $(du -sh data logs state)"
```

### Detailed Status Report
```bash
# Comprehensive status check
echo "🔍 Enhanced News Scraper Status Report"
echo "====================================="
echo "Configuration:"
python -c "
import config
print(f'  Categories: {len(config.CATEGORIES)}')
print(f'  IT News Sources: {len(config.TECH_NEWS_SOURCES)}') 
print(f'  Business Sources: {len(config.BUSINESS_NEWS_SOURCES)}')
print(f'  Entrepreneurship Sources: {len(config.ENTREPRENEURSHIP_NEWS_SOURCES)}')
print(f'  Total Sources: {len(config.ALL_NEWS_SOURCES)}')
"

echo -e "\nData Status:"
echo "  Total articles: $(find data -name 'extracted_*.json' | wc -l)"
echo "  Last 24h: $(find data -name 'extracted_*.json' -mtime -1 | wc -l)"
echo "  Last week: $(find data -name 'extracted_*.json' -mtime -7 | wc -l)"

echo -e "\nDisk Usage:"
du -sh data logs state

echo -e "\nRecent Activity:"
find logs -name "*.log" -mtime -1 -exec echo "  {}" \; | head -5
```

### Service Status
```bash
# Check if scrapers are running
ps aux | grep -i "scrapers\|python.*news" | grep -v grep

# Check recent scraper activity
find data -name "extracted_*.json" -mtime -1 -exec stat -c "%Y %n" {} \; | \
sort -n | tail -5 | while read timestamp file; do
    date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S $file"
done

# Last successful scrapes
echo "📈 Last Successful Scrapes:"
for category in it_news business_news entrepreneurship_news; do
    latest=$(find data -path "*/$category/extracted_*.json" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    if [ -n "$latest" ]; then
        timestamp=$(stat -c %Y "$latest")
        echo "  $category: $(date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S')"
    fi
done
```

---

## 📋 Batch Operations

### Sequential Scraping (Safer)
```bash
# Run all scrapers one by one
echo "🚀 Starting sequential scraping..."
python -m scrapers.it_news --past_hours 24 && \
python -m scrapers.business_news --past_hours 24 && \
python -m scrapers.entrepreneurship_news --past_hours 24 && \
python -m scrapers.lifestyle_news --past_hours 24 && \
echo "✅ All scrapers completed"

# With different time intervals
python -m scrapers.it_news --past_hours 12 && \
python -m scrapers.business_news --past_hours 24 && \
python -m scrapers.entrepreneurship_news --past_hours 48
```

### Parallel Scraping (Faster)
```bash
# Run multiple scrapers in parallel
echo "🚀 Starting parallel scraping..."
python -m scrapers.it_news --past_hours 24 &
python -m scrapers.business_news --past_hours 24 &
python -m scrapers.entrepreneurship_news --past_hours 24 &
wait  # Wait for all to complete
echo "✅ All parallel scrapers completed"

# Parallel with different time intervals
python -m scrapers.it_news --past_hours 48 &
python -m scrapers.business_news --past_hours 24 &
python -m scrapers.entrepreneurship_news --past_hours 72 &
wait
```

### Batch Testing
```bash
# Test all scrapers with comprehensive time ranges
echo "🧪 Comprehensive Scraper Testing"
for hours in 24 48 72; do
    echo "Testing with $hours hours lookback..."
    python -m scrapers.it_news --past_hours $hours
    echo "IT News ($hours h): $(find data -path "*/it_news/extracted_*.json" -mtime -1 | wc -l) articles"
done
```

### Scheduled Operations
```bash
# Add to crontab for automation
# Edit with: crontab -e

# Run every 3 hours
0 */3 * * * cd /path/to/project && python -m scrapers.it_news --past_hours 3 >> /tmp/scraper.log 2>&1

# Run business news twice daily  
0 9,21 * * * cd /path/to/project && python -m scrapers.business_news --past_hours 12

# Daily comprehensive scrape
0 6 * * * cd /path/to/project && python test_all_enhanced_scrapers.py

# Different schedules for different categories
0 */2 * * * cd /path/to/project && python -m scrapers.it_news --past_hours 2         # Every 2 hours
0 */6 * * * cd /path/to/project && python -m scrapers.business_news --past_hours 6   # Every 6 hours
0 8,20 * * * cd /path/to/project && python -m scrapers.entrepreneurship_news --past_hours 12  # Twice daily
```

---

## 🛠️ Utility Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install enhanced dependencies
pip install playwright asyncio-throttle aiofiles

# Install browser for JS rendering (if enabled)
playwright install chromium

# Set up environment variables
export PYTHONPATH=$(pwd):$PYTHONPATH

# Verify installation
python -c "
import requests, feedparser, beautifulsoup4, newspaper
print('✅ Core dependencies installed')
"
```

### Backup & Recovery
```bash
# Create full system backup
echo "📦 Creating full backup..."
tar -czf scraper_backup_$(date +%Y%m%d_%H%M).tar.gz \
  data/ logs/ state/ config.py scrapers/ utils/ \
  --exclude="*.pyc" --exclude="__pycache__"

# Create configuration backup
cp config.py config_backup_$(date +%Y%m%d).py
echo "✅ Configuration backed up"

# Backup just recent data
find data -mtime -7 -type f | tar -czf recent_data_$(date +%Y%m%d).tar.gz -T -

# Restore from backup
tar -xzf scraper_backup_YYYYMMDD_HHMM.tar.gz
echo "✅ System restored from backup"

# Selective restore
tar -xzf scraper_backup_YYYYMMDD_HHMM.tar.gz data/ state/
echo "✅ Data and state restored"
```

### Database Operations
```bash
# Export articles to CSV (if needed)
python -c "
import json, csv, glob
articles = []
for file in glob.glob('data/*/*/*/*/extracted_*.json'):
    with open(file) as f:
        articles.append(json.load(f))

with open('articles_export.csv', 'w', newline='') as f:
    if articles:
        writer = csv.DictWriter(f, fieldnames=articles[0].keys())
        writer.writeheader()
        writer.writerows(articles)
print(f'✅ Exported {len(articles)} articles to articles_export.csv')
"

# Count articles by source
python -c "
import json, glob
from collections import Counter
sources = []
for file in glob.glob('data/*/*/*/*/extracted_*.json'):
    with open(file) as f:
        article = json.load(f)
        sources.append(article.get('source', 'Unknown'))

counter = Counter(sources)
print('📊 Articles by Source:')
for source, count in counter.most_common():
    print(f'  {source}: {count}')
"
```

---

## 📈 Monitoring & Analytics

### Performance Monitoring
```bash
# Monitor scraping in real-time
watch -n 10 'echo "📊 Real-time Stats:"; find data -name "*.json" -mtime -1 | wc -l | xargs echo "Articles today:"; find logs -name "*.log" -mtime -1 | wc -l | xargs echo "Log files:"; du -sh data | cut -f1 | xargs echo "Data size:"'

# Check scraping frequency
echo "📈 Scraping Frequency Analysis:"
find data -name "extracted_*.json" -mtime -7 -exec stat -c "%Y %n" {} \; | \
sort -n | tail -20 | while read timestamp file; do
    date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S - $(basename $(dirname $file))"
done

# Source performance analysis  
echo "🎯 Source Performance:"
grep -r "articles from" logs/ | grep -o "[0-9]* articles from [^\"]*" | \
sort | uniq -c | sort -nr | head -10
```

### Success Rate Tracking
```bash
# Count successful vs failed scrapes
echo "📊 Success Rate Analysis:"
echo "Successes: $(grep -r "Success\|Found.*articles" logs/ | wc -l)"
echo "Failures: $(grep -r "failed:\|ERROR" logs/ | wc -l)"

# Articles per day for last week
echo "📅 Daily Article Counts:"
for i in {0..6}; do
    date_str=$(date -d "$i days ago" +%d_%m_%Y)
    count=$(find data -path "*/$date_str/*/extracted_*.json" | wc -l)
    echo "  $(date -d "$i days ago" +%Y-%m-%d): $count articles"
done

# Category performance
echo "📈 Category Performance:"
for category in it_news business_news entrepreneurship_news lifestyle_news; do
    count=$(find data -path "*/$category/extracted_*.json" -mtime -7 | wc -l)
    echo "  $category: $count articles (last 7 days)"
done
```

### Analytics Reports
```bash
# Generate weekly report
echo "📋 Weekly Scraping Report - $(date +%Y-%m-%d)"
echo "=================================================="

# Total stats
total_articles=$(find data -name "extracted_*.json" | wc -l)
week_articles=$(find data -name "extracted_*.json" -mtime -7 | wc -l)
today_articles=$(find data -name "extracted_*.json" -mtime -1 | wc -l)

echo "📊 Article Statistics:"
echo "  Total articles: $total_articles"
echo "  This week: $week_articles"
echo "  Today: $today_articles"

# Top sources
echo -e "\n🏆 Top Sources (This Week):"
python -c "
import json, glob
from collections import Counter
sources = []
for file in glob.glob('data/*/*/*/*/extracted_*.json'):
    try:
        with open(file) as f:
            article = json.load(f)
            sources.append(article.get('source', 'Unknown'))
    except: pass

counter = Counter(sources)
for source, count in counter.most_common(10):
    print(f'  {source}: {count}')
"

# System health
echo -e "\n🔧 System Health:"
echo "  Config status: $(python -c 'import config; print(\"✅ OK\")' 2>/dev/null || echo '❌ Error')"
echo "  Disk usage: $(du -sh data | cut -f1)"
echo "  Log files: $(find logs -name '*.log' | wc -l)"
```

---

## 🎯 Common Usage Patterns

### Daily Workflow
```bash
# Morning comprehensive scrape
echo "🌅 Morning News Scrape"
python test_all_enhanced_scrapers.py

# Quick IT update check
echo "💻 Quick IT News Update"
python -m scrapers.it_news --past_hours 12

# Check results
echo "📊 Today's Results:"
ls -la data/$(date +%d_%m_%Y)/*/
find data/$(date +%d_%m_%Y) -name "extracted_*.json" | wc -l | xargs echo "Total articles:"
```

### New Source Testing
```bash
# After adding new sources to config
echo "🧪 Testing New Sources"

# Test with longer lookback period
python -m scrapers.it_news --past_hours 168

# Validate configuration
python -c "import config; print('✅ Config validated')"

# Monitor first run
echo "📡 Monitoring scrape progress..."
tail -f logs/$(date +%Y%m%d)/*.log &
TAIL_PID=$!
python -m scrapers.business_news --past_hours 72
kill $TAIL_PID
```

### Troubleshooting Workflow
```bash
# When scrapers aren't working
echo "🔍 Troubleshooting Workflow"

# 1. Check for errors
echo "Step 1: Checking for errors..."
grep -r "ERROR\|Failed" logs/ | tail -10

# 2. Test individual components
echo "Step 2: Testing components..."
python -c "
try:
    from utils.request_manager import RequestManager
    import config
    rm = RequestManager(config.REQUEST_MANAGER_CONFIG)
    print('✅ Request Manager OK')
except Exception as e:
    print(f'❌ Request Manager: {e}')
"

# 3. Test basic scraper
echo "Step 3: Testing basic scraper..."
python backward_compatible_scraper.py

# 4. Clean restart if needed
echo "Step 4: Clean restart (if previous steps failed)..."
read -p "Clean restart? (y/N): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf state/*.json
    echo -e "\n🔄 Cleaned state, running fresh scrape..."
    python -m scrapers.it_news --past_hours 48
fi
```

### Maintenance Tasks
```bash
# Weekly maintenance
echo "🧹 Weekly Maintenance Tasks"

# 1. Clean old data
echo "Cleaning old data (30+ days)..."
find data -name "*.json" -mtime +30 -delete
find data -type d -empty -delete

# 2. Archive logs
echo "Archiving old logs..."
find logs -name "*.log" -mtime +7 -exec gzip {} \;

# 3. Backup configuration
echo "Backing up configuration..."
cp config.py config_backup_$(date +%Y%m%d).py

# 4. System health check
echo "System health check..."
python test_all_enhanced_scrapers.py > /tmp/health_check.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ System healthy"
else
    echo "⚠️  Issues detected, check /tmp/health_check.log"
fi

# 5. Update statistics
echo "📊 Current Statistics:"
echo "  Total articles: $(find data -name 'extracted_*.json' | wc -l)"
echo "  Data size: $(du -sh data | cut -f1)"
echo "  Active sources: $(python -c 'import config; print(len(config.ALL_NEWS_SOURCES))')"
```

### Performance Optimization
```bash
# Optimize scraping performance
echo "⚡ Performance Optimization"

# 1. Monitor memory usage
echo "Memory monitoring during scrape:"
python -c "
import psutil, os
print(f'Before: {psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.1f} MB')
" && \
python -m scrapers.it_news --past_hours 24 && \
python -c "
import psutil, os  
print(f'After: {psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.1f} MB')
"

# 2. Time different approaches
echo "Timing comparison:"
echo "Sequential scraping:"
time (python -m scrapers.it_news --past_hours 24 && python -m scrapers.business_news --past_hours 24)

echo "Parallel scraping:"
time (python -m scrapers.it_news --past_hours 24 & python -m scrapers.business_news --past_hours 24 & wait)

# 3. Optimize configuration
echo "Configuration optimization suggestions:"
python -c "
import config
rate_limit = getattr(config, 'RATE_LIMIT_SECONDS', 2)
print(f'Current rate limit: {rate_limit}s')
if rate_limit > 3:
    print('💡 Consider reducing rate limit for faster scraping')
elif rate_limit < 1:
    print('⚠️  Rate limit might be too aggressive')
else:
    print('✅ Rate limit looks optimal')
"
```

---

## 🚨 Emergency Procedures

### Emergency Stop
```bash
# Stop all running scrapers
pkill -f "python.*scrapers"
echo "🛑 All scrapers stopped"
```

### Emergency Backup
```bash
# Quick emergency backup
tar -czf emergency_backup_$(date +%Y%m%d_%H%M).tar.gz data/ state/ config.py
echo "💾 Emergency backup created"
```

### System Recovery
```bash
# Recover from backup
tar -xzf emergency_backup_*.tar.gz
echo "🔄 System recovered from emergency backup"
```

---

## 📞 Quick Help

```bash
# Show available scrapers
ls -la scrapers/*.py | grep -v __pycache__ | grep -v base_scraper

# Show configuration summary
python -c "
import config
print('📋 Quick Config Summary:')
print(f'Categories: {config.CATEGORIES}')
print(f'Total Sources: {len(config.ALL_NEWS_SOURCES)}')
print(f'Rate Limit: {config.RATE_LIMIT_SECONDS}s')
"

# Show recent activity
echo "📈 Recent Activity:"
find data -name "extracted_*.json" -mtime -1 | wc -l | xargs echo "Articles today:"
find logs -name "*.log" -mtime -1 | wc -l | xargs echo "Log files today:"
```

---

## 🎯 Most Used Commands Summary

```bash
# Daily essentials
python test_all_enhanced_scrapers.py                    # Test all scrapers
python -m scrapers.it_news --past_hours 24             # IT news update
python -m scrapers.business_news --past_hours 24       # Business news update

# Check results
find data -name "extracted_*.json" -mtime -1 | wc -l   # Count today's articles
ls -la data/$(date +%d_%m_%Y)/*/                       # Show today's data

# Monitor and troubleshoot
tail -f logs/$(date +%Y%m%d)/*.log                     # Monitor logs
grep -r "ERROR" logs/ | tail -5                        # Check recent errors
python -c "import config; print('Config OK')"          # Validate config
```