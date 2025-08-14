# 🚀 News Scraping & Summarizing Commands

Complete guide for scraping news and generating summaries with Llama 3.1:8B.

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Scraping Commands](#scraping-commands)
- [Summarizing Commands](#summarizing-commands)
- [Complete Workflows](#complete-workflows)
- [Popular Sources](#popular-sources)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### **All-in-One Command:**
```bash
cd news_system

# Scrape popular sources + summarize (RECOMMENDED)
python scrape_popular.py --hours 12 && python summarize_news.py
```

---

## 🔄 Scraping Commands

### **Simple Scraping (Recommended)**
```bash
cd news_system

# Scrape all categories - reliable, no Telegram issues  
python scrape_only.py --hours 12          # 12 hours, all categories
python scrape_only.py --hours 24          # 24 hours, all categories
python scrape_only.py --hours 6           # 6 hours, all categories

# Scrape specific category only
python scrape_only.py --category it_news --hours 12
python scrape_only.py --category business_news --hours 24
python scrape_only.py --category entrepreneurship_news --hours 12
python scrape_only.py --category lifestyle_news --hours 12
```

### **Popular Sources (10 Best Sources)**
```bash
cd news_system

# 🌟 BEST OPTION - Top quality sources only
python scrape_popular.py --hours 12       # 12 hours from 10 popular sources
python scrape_popular.py --hours 6        # 6 hours from 10 popular sources  
python scrape_popular.py --hours 24       # 24 hours from 10 popular sources

# List which sources are included
python scrape_popular.py --list

# Popular sources breakdown:
# - Tech: TechCrunch, The Verge, Ars Technica, Wired
# - Business: Business Insider, Forbes, Harvard Business Review
# - Entrepreneurship: Entrepreneur Magazine, Inc.
# - Lifestyle: Lifehacker
```

### **Individual Category Scrapers**
```bash
cd news_system

# Individual scrapers (module format)
python -m scrapers.it_news --past_hours 12
python -m scrapers.business_news --past_hours 24
python -m scrapers.entrepreneurship_news --past_hours 12
python -m scrapers.lifestyle_news --past_hours 24
```

### **Legacy Main System**
```bash
cd news_system

# May have Telegram import issues - use scrape_only.py instead
python main.py --scrape --hours 12        # All categories
python main.py --scrape --hours 24        # All categories
python main.py --scrape --category it_news --hours 12  # Specific category
```

---

## 🤖 Summarizing Commands

### **Setup Ollama & Llama 3.1:8B (One-time)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service (keep running)
ollama serve

# Download Llama 3.1:8B (in another terminal)
ollama pull llama3.1:8b

# Verify installation
ollama list
```

### **Automatic Summarization**
```bash
cd news_system

# Summarize latest scraped articles (finds latest data automatically)
python summarize_news.py

# Creates:
# - summaries_YYYYMMDD_HHMMSS.json (complete data)
# - summaries_YYYYMMDD_HHMMSS.md (readable format)
```

### **Advanced Summarization**
```bash
cd news_system

# Summarize specific data directory
python llm/llama_summarizer.py data/14_08_2025/0002 --output my_summaries.json

# Custom model
python llm/llama_summarizer.py data/14_08_2025/0002 --model llama3.1:8b --output results.json

# Custom Ollama URL
python llm/llama_summarizer.py data/14_08_2025/0002 --ollama-url http://localhost:11434
```

---

## 🚀 Complete Workflows

### **Daily News Update (Recommended)**
```bash
cd news_system

# Morning update - popular sources only (fast, high quality)
python scrape_popular.py --hours 12 && python summarize_news.py
```

### **Comprehensive Update**
```bash
cd news_system

# All categories + summarization
python scrape_only.py --hours 24 && python summarize_news.py
```

### **Quick Breaking News Check**
```bash
cd news_system

# Last 3 hours from popular sources
python scrape_popular.py --hours 3 && python summarize_news.py
```

### **Weekend Catch-up**
```bash
cd news_system

# 48 hours from all categories
python scrape_only.py --hours 48 && python summarize_news.py
```

### **Category-Specific Deep Dive**
```bash
cd news_system

# Focus on specific category
python scrape_only.py --category it_news --hours 24 && python summarize_news.py
```

---

## 🌟 Popular Sources Details

The `scrape_popular.py` command uses these **10 hand-picked, high-quality sources**:

### **Technology (4 sources):**
- **TechCrunch** - Leading tech startup news
- **The Verge** - Tech culture and consumer tech  
- **Ars Technica** - In-depth technical analysis
- **Wired** - Tech and digital culture

### **Business (3 sources):**
- **Business Insider** - Business news and analysis
- **Forbes** - Business and finance
- **Harvard Business Review** - Business strategy and management

### **Entrepreneurship (2 sources):**
- **Entrepreneur Magazine** - Startup and entrepreneur focus
- **Inc.** - Small business and entrepreneurship

### **Lifestyle (1 source):**
- **Lifehacker** - Productivity and life tips

**Why Popular Sources?**
- ⚡ **Faster**: Only 10 sources vs 80+ in full scrape
- 🎯 **Higher Quality**: Hand-picked reputable sources
- 📊 **Better Signal-to-Noise**: Less duplicate/low-quality content
- 🤖 **Better Summaries**: Higher quality input = better LLM output

---

## 💡 Usage Tips

### **For Regular Use:**
```bash
# Best daily workflow
python scrape_popular.py --hours 12 && python summarize_news.py
```

### **For Research/Analysis:**
```bash
# Comprehensive scraping
python scrape_only.py --hours 24 && python summarize_news.py
```

### **For Quick Updates:**
```bash
# Breaking news check
python scrape_popular.py --hours 3 && python summarize_news.py
```

---

## 📊 Output Files

### **Scraping Generates:**
- `data/DD_MM_YYYY/HHMM/category/extracted_N.json` - Individual articles
- `data/DD_MM_YYYY/HHMM/category/batch.json` - All articles in batch
- `logs/YYYYMMDD/HHMMSS.log` - Scraping logs

### **Summarizing Generates:**
- `summaries_YYYYMMDD_HHMMSS.json` - Complete summaries with metadata
- `summaries_YYYYMMDD_HHMMSS.md` - Readable markdown with links
- Each summary includes **original URL** and **source**

---

## 🔧 Troubleshooting

### **Scraping Issues:**
```bash
# If main.py has Telegram import issues:
python scrape_only.py --hours 12  # Use this instead

# If individual scrapers fail:
python scrape_popular.py --hours 12  # Use popular sources

# Check logs:
tail -f logs/$(date +%Y%m%d)/*.log
```

### **Summarizing Issues:**
```bash
# Check if Ollama is running:
curl http://localhost:11434/api/tags

# Start Ollama if needed:
ollama serve

# Check if model is available:
ollama list

# Download model if missing:
ollama pull llama3.1:8b
```

### **Path Issues:**
```bash
# Always run from news_system directory:
cd news_system
python summarize_news.py

# Check data directory structure:
ls -la data/
```

---

## 🎯 Most Used Commands Summary

```bash
# CRITICAL: Always run from news_system directory first!
cd news_system

# ⭐ RECOMMENDED DAILY WORKFLOW
python scrape_popular.py --hours 12 && python summarize_news.py

# Alternative workflows
python scrape_only.py --hours 12 && python summarize_news.py    # All categories
python scrape_popular.py --hours 6 && python summarize_news.py  # Quick update
python scrape_only.py --hours 24 && python summarize_news.py    # Comprehensive

# Setup (run once)
curl -fsSL https://ollama.com/install.sh | sh && ollama serve &
ollama pull llama3.1:8b
```

---

## 📈 Performance Expectations

### **Popular Sources (10 sources):**
- **Scraping time**: 2-5 minutes
- **Articles found**: 20-50 articles typically
- **Summarization**: 3-8 minutes
- **Total time**: 5-13 minutes

### **All Categories (80+ sources):**
- **Scraping time**: 10-20 minutes  
- **Articles found**: 100-300 articles typically
- **Summarization**: 15-45 minutes
- **Total time**: 25-65 minutes

### **Context Window Usage:**
- **Llama 3.1:8B**: 128K tokens (120K used safely)
- **Batch processing**: Up to 15 articles per batch
- **Automatic splitting**: Handles any number of articles

---

**🎉 You're all set! Start with the recommended workflow above!**