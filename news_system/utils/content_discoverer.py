#!/usr/bin/env python3
# utils/content_discoverer.py - Advanced content discovery for sites without RSS

import logging
import re
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, List, Any, Optional, Set, Tuple, Generator
from collections import defaultdict
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

logger = logging.getLogger("NewsSystem.ContentDiscoverer")

class ContentDiscoverer:
    """
    Advanced content discovery engine that finds articles through multiple strategies:
    - Sitemap.xml parsing
    - Archive page detection
    - Pagination handling
    - URL pattern recognition
    - RSS feed auto-discovery
    """
    
    def __init__(self, config: Dict[str, Any], request_manager):
        """
        Initialize the content discoverer.
        
        Args:
            config: Configuration dictionary
            request_manager: Request manager instance for HTTP requests
        """
        self.config = config
        self.request_manager = request_manager
        
        # Discovery strategies configuration
        self.max_pages_per_source = config.get('max_pages_per_source', 10)
        self.max_articles_per_source = config.get('max_articles_per_source', 50)
        self.discovery_timeout = config.get('discovery_timeout', 300)  # 5 minutes
        
        # URL pattern configuration
        self.article_url_patterns = config.get('article_url_patterns', [
            r'/article/', r'/post/', r'/news/', r'/story/',
            r'/blog/', r'/press/', r'/release/', r'/update/',
            r'/\d{4}/\d{2}/', r'/\d{4}-\d{2}-\d{2}/',
        ])
        
        # Date filtering
        self.max_article_age_days = config.get('max_article_age_days', 7)
        
        # Cache for discovered content
        self.discovery_cache: Dict[str, Dict[str, Any]] = {}
        self.sitemap_cache: Dict[str, List[str]] = {}
        
        # Statistics
        self.stats = defaultdict(int)
        
        logger.info("ContentDiscoverer initialized")
    
    async def discover_content(self, source: Dict[str, Any], 
                              cutoff_date: datetime) -> List[Dict[str, Any]]:
        """
        Discover content from a news source using multiple strategies.
        
        Args:
            source: News source configuration
            cutoff_date: Only return articles newer than this
            
        Returns:
            List of discovered article dictionaries
        """
        base_url = source['url']
        domain = urlparse(base_url).netloc
        
        logger.info(f"Starting content discovery for {source['name']}")
        
        all_articles = []
        discovered_urls = set()
        
        # Strategy 1: Try to find RSS feeds first
        rss_feeds = await self._discover_rss_feeds(base_url)
        for rss_url in rss_feeds:
            try:
                articles = await self._parse_rss_feed(rss_url, source, cutoff_date)
                for article in articles:
                    if article['url'] not in discovered_urls:
                        all_articles.append(article)
                        discovered_urls.add(article['url'])
                        self.stats['rss_articles_found'] += 1
            except Exception as e:
                logger.warning(f"Error parsing discovered RSS {rss_url}: {e}")
        
        # Strategy 2: Sitemap.xml discovery
        sitemap_urls = await self._discover_from_sitemap(base_url, cutoff_date)
        for url in sitemap_urls:
            if url not in discovered_urls and self._is_likely_article(url):
                article = await self._create_article_from_url(url, source, cutoff_date)
                if article:
                    all_articles.append(article)
                    discovered_urls.add(url)
                    self.stats['sitemap_articles_found'] += 1
        
        # Strategy 3: Archive page discovery
        archive_urls = await self._discover_from_archives(base_url, cutoff_date)
        for url in archive_urls:
            if url not in discovered_urls and self._is_likely_article(url):
                article = await self._create_article_from_url(url, source, cutoff_date)
                if article:
                    all_articles.append(article)
                    discovered_urls.add(url)
                    self.stats['archive_articles_found'] += 1
        
        # Strategy 4: Homepage and category page crawling
        homepage_urls = await self._discover_from_homepage(base_url, cutoff_date)
        for url in homepage_urls:
            if url not in discovered_urls and self._is_likely_article(url):
                article = await self._create_article_from_url(url, source, cutoff_date)
                if article:
                    all_articles.append(article)
                    discovered_urls.add(url)
                    self.stats['homepage_articles_found'] += 1
        
        # Strategy 5: URL pattern generation
        pattern_urls = await self._discover_from_patterns(base_url, cutoff_date)
        for url in pattern_urls:
            if url not in discovered_urls:
                article = await self._create_article_from_url(url, source, cutoff_date)
                if article:
                    all_articles.append(article)
                    discovered_urls.add(url)
                    self.stats['pattern_articles_found'] += 1
        
        # Sort by date and limit results
        all_articles.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        final_articles = all_articles[:self.max_articles_per_source]
        
        logger.info(f"Content discovery for {source['name']} found {len(final_articles)} articles")
        self.stats['total_articles_discovered'] += len(final_articles)
        
        return final_articles
    
    async def _discover_rss_feeds(self, base_url: str) -> List[str]:
        """Discover RSS feeds from a website."""
        rss_feeds = []
        
        try:
            # Try common RSS feed locations
            common_rss_paths = [
                '/rss', '/rss.xml', '/feed', '/feed.xml',
                '/feeds/all.atom.xml', '/atom.xml',
                '/rss/news', '/feeds/news.xml',
                '/blog/rss', '/blog/feed'
            ]
            
            for path in common_rss_paths:
                rss_url = urljoin(base_url, path)
                response = self.request_manager.get(rss_url)
                
                if response and response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if any(feed_type in content_type for feed_type in ['xml', 'rss', 'atom']):
                        rss_feeds.append(rss_url)
                        logger.debug(f"Found RSS feed: {rss_url}")
                        self.stats['rss_feeds_found'] += 1
            
            # Parse homepage for RSS feed links
            response = self.request_manager.get(base_url)
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for RSS feed links in HTML
                feed_links = soup.find_all('link', {
                    'type': lambda x: x and any(t in x.lower() for t in ['rss', 'atom', 'xml'])
                })
                
                for link in feed_links:
                    href = link.get('href')
                    if href:
                        rss_url = urljoin(base_url, href)
                        if rss_url not in rss_feeds:
                            rss_feeds.append(rss_url)
                            logger.debug(f"Found RSS feed in HTML: {rss_url}")
                            self.stats['rss_feeds_found'] += 1
                
        except Exception as e:
            logger.warning(f"Error discovering RSS feeds for {base_url}: {e}")
        
        return rss_feeds
    
    async def _parse_rss_feed(self, rss_url: str, source: Dict[str, Any], 
                             cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Parse an RSS feed and extract articles."""
        import feedparser
        
        try:
            response = self.request_manager.get(rss_url)
            if not response or response.status_code != 200:
                return []
            
            feed = feedparser.parse(response.text)
            articles = []
            
            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    # Skip if too old
                    if pub_date and pub_date < cutoff_date:
                        continue
                    
                    # Extract content
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    # Clean HTML
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        content = soup.get_text().strip()
                    
                    article = {
                        'title': entry.get('title', '').strip(),
                        'url': entry.get('link', ''),
                        'summary': content[:500] + '...' if len(content) > 500 else content,
                        'content': None,  # Will be filled later if needed
                        'source': source['name'],
                        'category': source['category'],
                        'timestamp': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                        'discovery_method': 'rss'
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error parsing RSS entry: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {e}")
            return []
    
    async def _discover_from_sitemap(self, base_url: str, cutoff_date: datetime) -> List[str]:
        """Discover article URLs from sitemap.xml."""
        domain = urlparse(base_url).netloc
        
        if domain in self.sitemap_cache:
            return self.sitemap_cache[domain]
        
        article_urls = []
        
        try:
            # Try common sitemap locations
            sitemap_urls = [
                urljoin(base_url, '/sitemap.xml'),
                urljoin(base_url, '/sitemaps.xml'),
                urljoin(base_url, '/sitemap_index.xml'),
                urljoin(base_url, '/robots.txt')  # Check robots.txt for sitemap
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    response = self.request_manager.get(sitemap_url)
                    if not response or response.status_code != 200:
                        continue
                    
                    if 'robots.txt' in sitemap_url:
                        # Parse robots.txt for sitemap URLs
                        for line in response.text.split('\n'):
                            if line.lower().startswith('sitemap:'):
                                actual_sitemap = line.split(':', 1)[1].strip()
                                sitemap_urls.append(actual_sitemap)
                        continue
                    
                    # Parse XML sitemap
                    urls = self._parse_sitemap_xml(response.text, cutoff_date)
                    article_urls.extend(urls)
                    
                    if urls:
                        logger.debug(f"Found {len(urls)} URLs in sitemap: {sitemap_url}")
                        self.stats['sitemaps_parsed'] += 1
                        break  # Found working sitemap
                        
                except Exception as e:
                    logger.debug(f"Error parsing sitemap {sitemap_url}: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Error discovering from sitemap for {base_url}: {e}")
        
        # Cache results
        self.sitemap_cache[domain] = article_urls
        return article_urls
    
    def _parse_sitemap_xml(self, xml_content: str, cutoff_date: datetime) -> List[str]:
        """Parse sitemap XML and extract recent article URLs."""
        urls = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle sitemap index (contains links to other sitemaps)
            if 'sitemapindex' in root.tag.lower():
                for sitemap in root.findall('.//{*}sitemap'):
                    loc_elem = sitemap.find('{*}loc')
                    if loc_elem is not None:
                        # Recursively parse sub-sitemaps
                        try:
                            response = self.request_manager.get(loc_elem.text)
                            if response and response.status_code == 200:
                                sub_urls = self._parse_sitemap_xml(response.text, cutoff_date)
                                urls.extend(sub_urls)
                        except:
                            continue
            
            # Handle regular sitemap (contains URLs)
            else:
                for url_elem in root.findall('.//{*}url'):
                    loc_elem = url_elem.find('{*}loc')
                    lastmod_elem = url_elem.find('{*}lastmod')
                    
                    if loc_elem is None:
                        continue
                    
                    url = loc_elem.text
                    
                    # Check last modification date
                    if lastmod_elem is not None:
                        try:
                            lastmod = datetime.fromisoformat(lastmod_elem.text.replace('Z', '+00:00'))
                            if lastmod < cutoff_date:
                                continue
                        except:
                            pass  # Continue if date parsing fails
                    
                    # Filter for likely article URLs
                    if self._is_likely_article(url):
                        urls.append(url)
        
        except ET.ParseError as e:
            logger.warning(f"XML parsing error in sitemap: {e}")
        except Exception as e:
            logger.warning(f"Error parsing sitemap XML: {e}")
        
        return urls
    
    async def _discover_from_archives(self, base_url: str, cutoff_date: datetime) -> List[str]:
        """Discover articles from archive/category pages."""
        article_urls = []
        
        try:
            # Common archive page patterns
            archive_paths = [
                '/news', '/blog', '/articles', '/posts',
                '/press-releases', '/updates', '/stories',
                '/category/news', '/category/blog',
                '/archive', '/recent', '/latest'
            ]
            
            for path in archive_paths:
                archive_url = urljoin(base_url, path)
                
                try:
                    response = self.request_manager.get(archive_url)
                    if not response or response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links that look like articles
                    links = soup.find_all('a', href=True)
                    page_urls = []
                    
                    for link in links:
                        href = link['href']
                        full_url = urljoin(archive_url, href)
                        
                        if self._is_likely_article(full_url):
                            page_urls.append(full_url)
                    
                    # Check for pagination
                    page_urls.extend(await self._follow_pagination(archive_url, soup))
                    
                    article_urls.extend(page_urls[:20])  # Limit per archive page
                    
                    if page_urls:
                        logger.debug(f"Found {len(page_urls)} URLs in archive: {archive_url}")
                        self.stats['archive_pages_parsed'] += 1
                
                except Exception as e:
                    logger.debug(f"Error parsing archive page {archive_url}: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Error discovering from archives for {base_url}: {e}")
        
        return list(set(article_urls))  # Remove duplicates
    
    async def _discover_from_homepage(self, base_url: str, cutoff_date: datetime) -> List[str]:
        """Discover articles from homepage and main category pages."""
        article_urls = []
        
        try:
            response = self.request_manager.get(base_url)
            if not response or response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                full_url = urljoin(base_url, href)
                
                if self._is_likely_article(full_url):
                    article_urls.append(full_url)
            
            # Look for category/section pages
            category_selectors = [
                'nav a', '.menu a', '.navigation a',
                '.category a', '.section a', '.topics a'
            ]
            
            category_urls = []
            for selector in category_selectors:
                try:
                    elements = soup.select(selector)
                    for elem in elements:
                        href = elem.get('href')
                        if href:
                            category_url = urljoin(base_url, href)
                            if self._is_likely_category_page(category_url):
                                category_urls.append(category_url)
                except:
                    continue
            
            # Parse category pages
            for category_url in category_urls[:5]:  # Limit category pages
                try:
                    cat_response = self.request_manager.get(category_url)
                    if cat_response and cat_response.status_code == 200:
                        cat_soup = BeautifulSoup(cat_response.text, 'html.parser')
                        cat_links = cat_soup.find_all('a', href=True)
                        
                        for link in cat_links:
                            href = link['href']
                            full_url = urljoin(category_url, href)
                            
                            if self._is_likely_article(full_url):
                                article_urls.append(full_url)
                except:
                    continue
            
            self.stats['homepage_pages_parsed'] += 1
        
        except Exception as e:
            logger.warning(f"Error discovering from homepage {base_url}: {e}")
        
        return list(set(article_urls))  # Remove duplicates
    
    async def _discover_from_patterns(self, base_url: str, cutoff_date: datetime) -> List[str]:
        """Generate URLs based on common patterns."""
        article_urls = []
        
        try:
            domain = urlparse(base_url).netloc
            
            # Date-based URL patterns
            today = datetime.now()
            
            for days_back in range(7):  # Look back 7 days
                date = today - timedelta(days=days_back)
                
                if date < cutoff_date:
                    break
                
                # Try different date formats
                date_formats = [
                    date.strftime('%Y/%m/%d'),
                    date.strftime('%Y-%m-%d'),
                    date.strftime('%Y/%m'),
                    date.strftime('%Y-%m')
                ]
                
                for date_format in date_formats:
                    pattern_urls = [
                        f"{base_url}/news/{date_format}/",
                        f"{base_url}/blog/{date_format}/",
                        f"{base_url}/articles/{date_format}/",
                        f"{base_url}/{date_format}/"
                    ]
                    
                    for pattern_url in pattern_urls:
                        try:
                            response = self.request_manager.get(pattern_url)
                            if response and response.status_code == 200:
                                soup = BeautifulSoup(response.text, 'html.parser')
                                links = soup.find_all('a', href=True)
                                
                                for link in links:
                                    href = link['href']
                                    full_url = urljoin(pattern_url, href)
                                    
                                    if self._is_likely_article(full_url):
                                        article_urls.append(full_url)
                        except:
                            continue
            
            self.stats['pattern_generations'] += 1
        
        except Exception as e:
            logger.warning(f"Error discovering from patterns for {base_url}: {e}")
        
        return list(set(article_urls))  # Remove duplicates
    
    async def _follow_pagination(self, base_url: str, soup: BeautifulSoup) -> List[str]:
        """Follow pagination links to discover more articles."""
        article_urls = []
        
        try:
            # Common pagination selectors
            pagination_selectors = [
                'a[rel="next"]', '.next a', '.pagination a',
                'a:contains("Next")', 'a:contains(">")',
                '.pager a', '.page-numbers a'
            ]
            
            next_links = []
            for selector in pagination_selectors:
                try:
                    elements = soup.select(selector)
                    for elem in elements:
                        href = elem.get('href')
                        if href:
                            next_url = urljoin(base_url, href)
                            next_links.append(next_url)
                except:
                    continue
            
            # Follow pagination (limit to prevent infinite loops)
            visited_pages = {base_url}
            pages_to_visit = list(set(next_links))[:3]  # Limit pagination depth
            
            for next_url in pages_to_visit:
                if next_url in visited_pages:
                    continue
                
                try:
                    response = self.request_manager.get(next_url)
                    if response and response.status_code == 200:
                        page_soup = BeautifulSoup(response.text, 'html.parser')
                        links = page_soup.find_all('a', href=True)
                        
                        for link in links:
                            href = link['href']
                            full_url = urljoin(next_url, href)
                            
                            if self._is_likely_article(full_url):
                                article_urls.append(full_url)
                        
                        visited_pages.add(next_url)
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Error following pagination: {e}")
        
        return article_urls
    
    def _is_likely_article(self, url: str) -> bool:
        """Determine if a URL is likely to be an article."""
        url_lower = url.lower()
        
        # Positive indicators
        for pattern in self.article_url_patterns:
            if re.search(pattern, url_lower):
                return True
        
        # Additional heuristics
        positive_keywords = [
            'article', 'post', 'story', 'news', 'blog',
            'press', 'release', 'update', 'announcement'
        ]
        
        for keyword in positive_keywords:
            if keyword in url_lower:
                return True
        
        # Negative indicators
        negative_keywords = [
            'category', 'tag', 'archive', 'page',
            'search', 'contact', 'about', 'login',
            'register', 'admin', 'api', 'feed',
            'rss', 'xml', 'json', 'css', 'js',
            'image', 'img', 'photo', 'video'
        ]
        
        for keyword in negative_keywords:
            if keyword in url_lower:
                return False
        
        return False
    
    def _is_likely_category_page(self, url: str) -> bool:
        """Determine if a URL is likely to be a category/section page."""
        url_lower = url.lower()
        
        category_keywords = [
            'category', 'section', 'topic', 'tag',
            'news', 'blog', 'articles', 'posts'
        ]
        
        for keyword in category_keywords:
            if keyword in url_lower:
                return True
        
        return False
    
    async def _create_article_from_url(self, url: str, source: Dict[str, Any], 
                                      cutoff_date: datetime) -> Optional[Dict[str, Any]]:
        """Create an article dictionary from a URL by fetching and parsing it."""
        try:
            response = self.request_manager.get(url)
            if not response or response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ""
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Try other title selectors
            if not title:
                for selector in ['h1', '.title', '.headline', '.post-title']:
                    elem = soup.select_one(selector)
                    if elem:
                        title = elem.get_text().strip()
                        break
            
            # Extract publication date
            pub_date = self._extract_date_from_html(soup)
            
            # Skip if too old
            if pub_date and pub_date < cutoff_date:
                return None
            
            # Extract summary/content preview
            summary = self._extract_summary_from_html(soup)
            
            article = {
                'title': title,
                'url': url,
                'summary': summary,
                'content': None,  # Will be filled later if needed
                'source': source['name'],
                'category': source['category'],
                'timestamp': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                'discovery_method': 'url_discovery'
            }
            
            return article
            
        except Exception as e:
            logger.debug(f"Error creating article from URL {url}: {e}")
            return None
    
    def _extract_date_from_html(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date from HTML."""
        try:
            # Try meta tags first
            date_selectors = [
                'meta[property="article:published_time"]',
                'meta[name="pubdate"]',
                'meta[name="date"]',
                'meta[property="og:updated_time"]',
                'time[datetime]',
                '.date', '.published', '.post-date'
            ]
            
            for selector in date_selectors:
                elem = soup.select_one(selector)
                if elem:
                    date_str = elem.get('content') or elem.get('datetime') or elem.get_text()
                    if date_str:
                        # Try to parse the date
                        import dateutil.parser
                        try:
                            return dateutil.parser.parse(date_str)
                        except:
                            continue
        
        except Exception as e:
            logger.debug(f"Error extracting date from HTML: {e}")
        
        return None
    
    def _extract_summary_from_html(self, soup: BeautifulSoup) -> str:
        """Extract summary/description from HTML."""
        try:
            # Try meta description first
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                content = meta_desc.get('content', '')
                if content:
                    return content.strip()
            
            # Try other meta tags
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc:
                content = og_desc.get('content', '')
                if content:
                    return content.strip()
            
            # Try to extract from article content
            content_selectors = [
                '.article-content', '.post-content', '.entry-content',
                'article', '.content', 'main'
            ]
            
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text().strip()
                    if text:
                        # Return first paragraph or first 200 characters
                        sentences = text.split('. ')
                        if len(sentences) > 0:
                            summary = sentences[0] + '.'
                            return summary[:200] + '...' if len(summary) > 200 else summary
        
        except Exception as e:
            logger.debug(f"Error extracting summary from HTML: {e}")
        
        return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get content discoverer statistics."""
        return {
            'total_articles_discovered': self.stats['total_articles_discovered'],
            'rss_feeds_found': self.stats['rss_feeds_found'],
            'rss_articles_found': self.stats['rss_articles_found'],
            'sitemap_articles_found': self.stats['sitemap_articles_found'],
            'archive_articles_found': self.stats['archive_articles_found'],
            'homepage_articles_found': self.stats['homepage_articles_found'],
            'pattern_articles_found': self.stats['pattern_articles_found'],
            'sitemaps_parsed': self.stats['sitemaps_parsed'],
            'archive_pages_parsed': self.stats['archive_pages_parsed'],
            'homepage_pages_parsed': self.stats['homepage_pages_parsed'],
            'pattern_generations': self.stats['pattern_generations'],
            'cache_size': len(self.discovery_cache),
            'sitemap_cache_size': len(self.sitemap_cache)
        }