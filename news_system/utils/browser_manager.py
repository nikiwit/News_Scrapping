#!/usr/bin/env python3
# utils/browser_manager.py - Headless browser pool management with stealth features

import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
from collections import defaultdict, deque

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available. Install with: pip install playwright")

logger = logging.getLogger("NewsSystem.BrowserManager")

class BrowserManager:
    """
    Manages a pool of headless browsers with stealth features for JavaScript rendering.
    Supports rotation, stealth mode, and intelligent resource management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the browser manager.
        
        Args:
            config: Configuration dictionary
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required for BrowserManager. Install with: pip install playwright")
        
        self.config = config
        
        # Pool configuration
        self.max_browsers = config.get('max_browsers', 3)
        self.max_contexts_per_browser = config.get('max_contexts_per_browser', 5)
        self.browser_lifetime = config.get('browser_lifetime', 1800)  # 30 minutes
        self.context_lifetime = config.get('context_lifetime', 600)   # 10 minutes
        
        # Browser settings
        self.headless = config.get('headless', True)
        self.browser_type = config.get('browser_type', 'chromium')  # chromium, firefox, webkit
        self.stealth_mode = config.get('stealth_mode', True)
        
        # Page settings
        self.default_timeout = config.get('default_timeout', 30000)  # 30 seconds
        self.wait_for_network = config.get('wait_for_network', True)
        self.block_resources = config.get('block_resources', ['image', 'font', 'media'])
        
        # Pool tracking
        self.playwright = None
        self.browsers: Dict[str, Dict[str, Any]] = {}  # browser_id -> {browser, contexts, created_at}
        self.contexts: Dict[str, Dict[str, Any]] = {}  # context_id -> {context, browser_id, created_at, page_count}
        self.active_pages: Dict[str, Page] = {}  # page_id -> page
        
        # Statistics
        self.stats = defaultdict(int)
        
        logger.info(f"BrowserManager initialized (max_browsers={self.max_browsers}, stealth_mode={self.stealth_mode})")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self):
        """Start the browser manager and initialize Playwright."""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            logger.info("Playwright started")
    
    async def get_page(self, url: str = None) -> Tuple[Page, str]:
        """
        Get a page from the browser pool for rendering.
        
        Args:
            url: Optional URL to prepare the page for
            
        Returns:
            Tuple of (Page object, page_id for cleanup)
        """
        await self.start()
        
        # Get or create a browser context
        context, context_id = await self._get_context()
        
        # Create new page
        page = await context.new_page()
        page_id = f"{context_id}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Configure page
        await self._configure_page(page, url)
        
        # Track page
        self.active_pages[page_id] = page
        self.contexts[context_id]['page_count'] += 1
        self.stats['pages_created'] += 1
        
        logger.debug(f"Created page {page_id} for URL: {url}")
        return page, page_id
    
    async def return_page(self, page_id: str):
        """
        Return a page to the pool (close it).
        
        Args:
            page_id: Page ID from get_page()
        """
        if page_id in self.active_pages:
            try:
                page = self.active_pages[page_id]
                await page.close()
                
                # Update context page count
                context_id = page_id.split('_')[0] + '_' + page_id.split('_')[1]
                if context_id in self.contexts:
                    self.contexts[context_id]['page_count'] -= 1
                
                del self.active_pages[page_id]
                self.stats['pages_closed'] += 1
                
                logger.debug(f"Closed page {page_id}")
                
            except Exception as e:
                logger.error(f"Error closing page {page_id}: {e}")
        
        # Cleanup old resources
        await self._cleanup_resources()
    
    async def render_page(self, url: str, wait_for: Optional[str] = None, 
                         wait_time: int = 2000) -> Tuple[str, Dict[str, Any]]:
        """
        Render a JavaScript-heavy page and return HTML content.
        
        Args:
            url: URL to render
            wait_for: CSS selector to wait for (optional)
            wait_time: Additional wait time in milliseconds
            
        Returns:
            Tuple of (HTML content, metadata dict)
        """
        page, page_id = await self.get_page(url)
        
        try:
            start_time = time.time()
            
            # Navigate to URL
            response = await page.goto(url, wait_until='domcontentloaded')
            
            # Wait for specific element if provided
            if wait_for:
                try:
                    await page.wait_for_selector(wait_for, timeout=10000)
                except Exception as e:
                    logger.warning(f"Failed to wait for selector '{wait_for}': {e}")
            
            # Wait for network to be mostly idle
            if self.wait_for_network:
                try:
                    await page.wait_for_load_state('networkidle', timeout=10000)
                except Exception as e:
                    logger.debug(f"Network idle timeout: {e}")
            
            # Additional wait time for dynamic content
            if wait_time > 0:
                await page.wait_for_timeout(wait_time)
            
            # Get page content
            html_content = await page.content()
            
            # Collect metadata
            metadata = {
                'url': page.url,
                'title': await page.title(),
                'status_code': response.status if response else None,
                'load_time': time.time() - start_time,
                'content_length': len(html_content),
                'has_javascript': 'script' in html_content.lower(),
                'viewport': await page.viewport_size(),
            }
            
            # Check for common SPA frameworks
            metadata['frameworks'] = await self._detect_frameworks(page)
            
            self.stats['pages_rendered'] += 1
            logger.debug(f"Rendered page: {url} in {metadata['load_time']:.2f}s")
            
            return html_content, metadata
            
        except Exception as e:
            logger.error(f"Error rendering page {url}: {e}")
            self.stats['render_errors'] += 1
            raise
            
        finally:
            await self.return_page(page_id)
    
    async def check_js_required(self, url: str, basic_html: str) -> bool:
        """
        Determine if JavaScript rendering is required for this URL.
        
        Args:
            url: URL to check
            basic_html: HTML content from basic request
            
        Returns:
            True if JS rendering is likely needed
        """
        # Quick heuristics first
        html_lower = basic_html.lower()
        
        # Check for obvious JS indicators
        js_indicators = [
            'react', 'angular', 'vue.js', 'ember.js',
            'single page application', 'spa',
            'javascript required', 'enable javascript',
            'document.ready', 'window.onload',
            'loading...', 'please wait',
            'dynamically loaded', 'ajax content'
        ]
        
        for indicator in js_indicators:
            if indicator in html_lower:
                logger.debug(f"JS indicator found: {indicator}")
                return True
        
        # Check content ratio - if very little text content, might be JS-heavy
        text_content = basic_html
        for tag in ['<script', '<style', '<meta', '<link', '<title']:
            parts = text_content.split(tag)
            if len(parts) > 1:
                text_content = parts[0] + ''.join(parts[1:])
        
        # Remove HTML tags for text content estimation
        import re
        text_only = re.sub(r'<[^>]+>', '', text_content)
        text_ratio = len(text_only.strip()) / max(len(basic_html), 1)
        
        if text_ratio < 0.1:  # Less than 10% actual text content
            logger.debug(f"Low text content ratio: {text_ratio:.2f}")
            return True
        
        # Advanced check: actually render and compare
        try:
            js_html, metadata = await self.render_page(url, wait_time=1000)
            
            # Compare content lengths
            length_diff = len(js_html) - len(basic_html)
            length_ratio = length_diff / max(len(basic_html), 1)
            
            if length_ratio > 0.3:  # 30% more content with JS
                logger.debug(f"Significant content difference with JS: {length_ratio:.2f}")
                return True
                
            # Check for new elements that appeared with JS
            js_lower = js_html.lower()
            new_content_indicators = [
                'article', 'main content', 'news-item',
                'post-content', 'entry-content'
            ]
            
            basic_count = sum(basic_html.lower().count(indicator) for indicator in new_content_indicators)
            js_count = sum(js_lower.count(indicator) for indicator in new_content_indicators)
            
            if js_count > basic_count * 1.5:
                logger.debug(f"More content elements with JS: {basic_count} -> {js_count}")
                return True
                
        except Exception as e:
            logger.warning(f"Error in advanced JS check for {url}: {e}")
        
        return False
    
    async def _get_context(self) -> Tuple[BrowserContext, str]:
        """Get or create a browser context."""
        # Find available context
        current_time = time.time()
        
        for context_id, context_data in list(self.contexts.items()):
            # Check if context is not too old and not overloaded
            age = current_time - context_data['created_at']
            if (age < self.context_lifetime and 
                context_data['page_count'] < self.max_contexts_per_browser):
                return context_data['context'], context_id
        
        # Need to create new context
        browser, browser_id = await self._get_browser()
        context = await browser.new_context(**self._get_context_config())
        
        context_id = f"{browser_id}_{int(current_time)}_{random.randint(100, 999)}"
        
        self.contexts[context_id] = {
            'context': context,
            'browser_id': browser_id,
            'created_at': current_time,
            'page_count': 0
        }
        
        self.stats['contexts_created'] += 1
        logger.debug(f"Created new context: {context_id}")
        
        return context, context_id
    
    async def _get_browser(self) -> Tuple[Browser, str]:
        """Get or create a browser instance."""
        current_time = time.time()
        
        # Find available browser
        for browser_id, browser_data in list(self.browsers.items()):
            age = current_time - browser_data['created_at']
            if age < self.browser_lifetime and len(browser_data['contexts']) < self.max_contexts_per_browser:
                return browser_data['browser'], browser_id
        
        # Check if we can create new browser
        if len(self.browsers) >= self.max_browsers:
            # Close oldest browser
            oldest_id = min(self.browsers.keys(), key=lambda x: self.browsers[x]['created_at'])
            await self._close_browser(oldest_id)
        
        # Create new browser
        browser_launcher = getattr(self.playwright, self.browser_type)
        browser = await browser_launcher.launch(**self._get_browser_config())
        
        browser_id = f"{self.browser_type}_{int(current_time)}_{random.randint(100, 999)}"
        
        self.browsers[browser_id] = {
            'browser': browser,
            'contexts': [],
            'created_at': current_time
        }
        
        self.stats['browsers_created'] += 1
        logger.debug(f"Created new browser: {browser_id}")
        
        return browser, browser_id
    
    def _get_browser_config(self) -> Dict[str, Any]:
        """Get browser launch configuration."""
        config = {
            'headless': self.headless,
            'args': []
        }
        
        if self.stealth_mode and self.browser_type == 'chromium':
            # Anti-detection arguments for Chromium
            config['args'].extend([
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-default-browser-check',
                '--disable-blink-features=AutomationControlled'
            ])
        
        return config
    
    def _get_context_config(self) -> Dict[str, Any]:
        """Get browser context configuration."""
        config = {
            'viewport': {'width': 1366, 'height': 768},
            'user_agent': self._get_random_user_agent(),
        }
        
        if self.stealth_mode:
            # Additional stealth settings
            config.update({
                'java_script_enabled': True,
                'ignore_https_errors': True,
                'extra_http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            })
        
        return config
    
    async def _configure_page(self, page: Page, url: Optional[str] = None):
        """Configure a page with stealth and performance settings."""
        # Set timeout
        page.set_default_timeout(self.default_timeout)
        
        # Block unnecessary resources
        if self.block_resources:
            await page.route('**/*', lambda route: (
                route.abort() if route.request.resource_type in self.block_resources
                else route.continue_()
            ))
        
        if self.stealth_mode:
            # Stealth JavaScript injection
            await page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock chrome object
                window.chrome = {
                    runtime: {},
                    app: {
                        isInstalled: false,
                    },
                };
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
    
    async def _detect_frameworks(self, page: Page) -> List[str]:
        """Detect JavaScript frameworks on the page."""
        frameworks = []
        
        try:
            # Check for common frameworks
            framework_checks = {
                'React': 'window.React || document.querySelector("[data-reactroot]")',
                'Vue': 'window.Vue || document.querySelector("[data-v-]")',
                'Angular': 'window.angular || window.ng || document.querySelector("[ng-app]")',
                'jQuery': 'window.jQuery || window.$',
                'Ember': 'window.Ember',
                'Backbone': 'window.Backbone',
                'Knockout': 'window.ko'
            }
            
            for framework, check in framework_checks.items():
                try:
                    result = await page.evaluate(f'!!({check})')
                    if result:
                        frameworks.append(framework)
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Error detecting frameworks: {e}")
        
        return frameworks
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        return random.choice(user_agents)
    
    async def _cleanup_resources(self):
        """Clean up old browsers and contexts."""
        current_time = time.time()
        
        # Clean up old contexts
        for context_id in list(self.contexts.keys()):
            context_data = self.contexts[context_id]
            age = current_time - context_data['created_at']
            
            if age > self.context_lifetime or context_data['page_count'] == 0:
                try:
                    await context_data['context'].close()
                    del self.contexts[context_id]
                    self.stats['contexts_cleaned'] += 1
                    logger.debug(f"Cleaned up old context: {context_id}")
                except Exception as e:
                    logger.error(f"Error cleaning context {context_id}: {e}")
        
        # Clean up old browsers
        for browser_id in list(self.browsers.keys()):
            browser_data = self.browsers[browser_id]
            age = current_time - browser_data['created_at']
            
            if age > self.browser_lifetime:
                await self._close_browser(browser_id)
    
    async def _close_browser(self, browser_id: str):
        """Close a specific browser and its contexts."""
        if browser_id in self.browsers:
            try:
                browser_data = self.browsers[browser_id]
                await browser_data['browser'].close()
                del self.browsers[browser_id]
                self.stats['browsers_closed'] += 1
                logger.debug(f"Closed browser: {browser_id}")
            except Exception as e:
                logger.error(f"Error closing browser {browser_id}: {e}")
    
    async def close(self):
        """Close all browsers and clean up resources."""
        try:
            # Close all active pages
            for page_id in list(self.active_pages.keys()):
                await self.return_page(page_id)
            
            # Close all contexts
            for context_data in self.contexts.values():
                try:
                    await context_data['context'].close()
                except:
                    pass
            
            # Close all browsers
            for browser_data in self.browsers.values():
                try:
                    await browser_data['browser'].close()
                except:
                    pass
            
            # Stop Playwright
            if self.playwright:
                await self.playwright.stop()
            
            self.browsers.clear()
            self.contexts.clear()
            self.active_pages.clear()
            
            logger.info("BrowserManager closed and cleaned up")
            
        except Exception as e:
            logger.error(f"Error during BrowserManager cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get browser manager statistics."""
        return {
            'active_browsers': len(self.browsers),
            'active_contexts': len(self.contexts),
            'active_pages': len(self.active_pages),
            'browsers_created': self.stats['browsers_created'],
            'browsers_closed': self.stats['browsers_closed'],
            'contexts_created': self.stats['contexts_created'],
            'contexts_cleaned': self.stats['contexts_cleaned'],
            'pages_created': self.stats['pages_created'],
            'pages_closed': self.stats['pages_closed'],
            'pages_rendered': self.stats['pages_rendered'],
            'render_errors': self.stats['render_errors']
        }