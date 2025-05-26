#!/usr/bin/env python3
# utils/js_renderer.py - Smart JavaScript rendering with automatic detection

import logging
import time
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse
from collections import defaultdict

from .browser_manager import BrowserManager

logger = logging.getLogger("NewsSystem.JSRenderer")

class JSRenderer:
    """
    Smart JavaScript renderer that automatically detects when JS rendering
    is needed and manages browser resources efficiently.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the JS renderer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Rendering strategy
        self.auto_detect = config.get('auto_detect', True)
        self.force_js_domains = set(config.get('force_js_domains', []))
        self.never_js_domains = set(config.get('never_js_domains', []))
        self.js_threshold = config.get('js_threshold', 0.3)  # Content difference threshold
        
        # Performance settings
        self.max_render_time = config.get('max_render_time', 30)
        self.cache_results = config.get('cache_results', True)
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour
        
        # Browser manager
        browser_config = config.get('browser_config', {})
        self.browser_manager = BrowserManager(browser_config)
        
        # Caching for JS detection results
        self.js_detection_cache: Dict[str, Dict[str, Any]] = {}
        self.render_cache: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = defaultdict(int)
        
        logger.info("JSRenderer initialized with smart detection")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.browser_manager.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.browser_manager.close()
    
    async def render_if_needed(self, url: str, basic_html: str, 
                              basic_response_time: float = 0) -> Tuple[str, Dict[str, Any]]:
        """
        Render with JavaScript if needed, otherwise return basic HTML.
        
        Args:
            url: URL to potentially render
            basic_html: HTML from basic HTTP request
            basic_response_time: Time taken for basic request
            
        Returns:
            Tuple of (final_html, metadata)
        """
        start_time = time.time()
        domain = urlparse(url).netloc.lower()
        
        # Check domain overrides first
        if domain in self.never_js_domains:
            logger.debug(f"Domain in never-JS list: {domain}")
            self.stats['skipped_never_js'] += 1
            return basic_html, {
                'js_rendered': False,
                'reason': 'domain_never_js',
                'render_time': 0,
                'content_improvement': 0
            }
        
        if domain in self.force_js_domains:
            logger.debug(f"Domain in force-JS list: {domain}")
            return await self._force_render(url, basic_html)
        
        # Auto-detection logic
        if self.auto_detect:
            needs_js = await self._detect_js_need(url, basic_html, domain)
            
            if needs_js:
                logger.debug(f"Auto-detected JS needed for: {url}")
                return await self._render_with_js(url, basic_html)
            else:
                logger.debug(f"Auto-detected JS not needed for: {url}")
                self.stats['skipped_auto_detect'] += 1
                return basic_html, {
                    'js_rendered': False,
                    'reason': 'auto_detect_no_js',
                    'render_time': 0,
                    'content_improvement': 0
                }
        
        # Default: no JS rendering
        self.stats['skipped_default'] += 1
        return basic_html, {
            'js_rendered': False,
            'reason': 'default_no_js',
            'render_time': 0,
            'content_improvement': 0
        }
    
    async def force_render(self, url: str, wait_for: Optional[str] = None,
                          wait_time: int = 2000) -> Tuple[str, Dict[str, Any]]:
        """
        Force JavaScript rendering for a URL.
        
        Args:
            url: URL to render
            wait_for: CSS selector to wait for
            wait_time: Additional wait time in milliseconds
            
        Returns:
            Tuple of (rendered_html, metadata)
        """
        return await self._render_with_js(url, "", wait_for, wait_time)
    
    async def _detect_js_need(self, url: str, basic_html: str, domain: str) -> bool:
        """
        Detect if JavaScript rendering is needed using multiple strategies.
        
        Args:
            url: URL to check
            basic_html: Basic HTML content
            domain: Domain of the URL
            
        Returns:
            True if JS rendering is recommended
        """
        # Check cache first
        cache_key = f"{domain}_{hash(url)}"
        current_time = time.time()
        
        if self.cache_results and cache_key in self.js_detection_cache:
            cache_entry = self.js_detection_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_ttl:
                self.stats['detection_cache_hits'] += 1
                return cache_entry['needs_js']
        
        # Multiple detection strategies
        strategies = [
            self._check_html_indicators,
            self._check_content_ratio,
            self._check_meta_tags,
            self._check_known_patterns
        ]
        
        js_votes = 0
        total_strategies = len(strategies)
        
        for strategy in strategies:
            try:
                if await strategy(url, basic_html, domain):
                    js_votes += 1
            except Exception as e:
                logger.warning(f"Error in JS detection strategy: {e}")
        
        # Decision based on majority vote
        needs_js = js_votes >= (total_strategies // 2 + 1)
        
        # Advanced check: actual rendering comparison (for uncertain cases)
        if not needs_js and js_votes == total_strategies // 2:
            logger.debug(f"Uncertain JS detection, doing comparison render for: {url}")
            needs_js = await self._compare_render_results(url, basic_html)
        
        # Cache the result
        if self.cache_results:
            self.js_detection_cache[cache_key] = {
                'needs_js': needs_js,
                'timestamp': current_time,
                'votes': js_votes,
                'total': total_strategies
            }
        
        self.stats['js_detections'] += 1
        if needs_js:
            self.stats['js_needed'] += 1
        
        return needs_js
    
    async def _check_html_indicators(self, url: str, html: str, domain: str) -> bool:
        """Check for HTML indicators that suggest JS is needed."""
        html_lower = html.lower()
        
        # Strong indicators
        strong_indicators = [
            'react', 'angular', 'vue.js', 'ember.js', 'svelte',
            'single page application', 'spa',
            'javascript required', 'enable javascript',
            'please enable javascript', 'noscript',
            'loading...', 'please wait', 'loading content',
            'dynamically loaded', 'ajax content'
        ]
        
        strong_count = sum(1 for indicator in strong_indicators if indicator in html_lower)
        
        # Weak indicators
        weak_indicators = [
            'document.ready', 'window.onload', '$(document)',
            'fetch(', 'axios.', 'xhr.', 'xmlhttprequest',
            'json', 'api/v', 'async', 'await'
        ]
        
        weak_count = sum(1 for indicator in weak_indicators if indicator in html_lower)
        
        # Scoring
        score = strong_count * 2 + weak_count
        threshold = 3  # Adjust based on testing
        
        logger.debug(f"HTML indicators score for {domain}: {score} (strong: {strong_count}, weak: {weak_count})")
        return score >= threshold
    
    async def _check_content_ratio(self, url: str, html: str, domain: str) -> bool:
        """Check text content ratio to detect placeholder pages."""
        import re
        
        # Remove script and style tags
        html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove other non-content tags
        html_clean = re.sub(r'<(meta|link|title|head)[^>]*>', '', html_clean, flags=re.IGNORECASE)
        
        # Extract text content
        text_content = re.sub(r'<[^>]+>', '', html_clean)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Calculate ratios
        total_length = len(html)
        text_length = len(text_content)
        text_ratio = text_length / max(total_length, 1)
        
        # Very low text ratio suggests placeholder content
        is_placeholder = text_ratio < 0.1 and text_length < 500
        
        logger.debug(f"Content ratio for {domain}: {text_ratio:.3f} (text: {text_length}, total: {total_length})")
        return is_placeholder
    
    async def _check_meta_tags(self, url: str, html: str, domain: str) -> bool:
        """Check meta tags for SPA/JS framework indicators."""
        import re
        
        # Look for framework-specific meta tags
        framework_patterns = [
            r'<meta[^>]+generator[^>]+react',
            r'<meta[^>]+framework[^>]+angular',
            r'<meta[^>]+vue',
            r'<meta[^>]+ember',
            r'data-reactroot',
            r'ng-app',
            r'v-app'
        ]
        
        for pattern in framework_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                logger.debug(f"Framework meta tag found for {domain}: {pattern}")
                return True
        
        return False
    
    async def _check_known_patterns(self, url: str, html: str, domain: str) -> bool:
        """Check for known patterns that indicate JS-heavy sites."""
        # Domain-based patterns
        js_heavy_domains = [
            'medium.com', 'notion.so', 'airtable.com',
            'trello.com', 'asana.com', 'slack.com',
            'discord.com', 'figma.com', 'canva.com',
            'spotify.com', 'netflix.com'
        ]
        
        for js_domain in js_heavy_domains:
            if js_domain in domain:
                logger.debug(f"Known JS-heavy domain: {domain}")
                return True
        
        # URL pattern checks
        js_patterns = [
            '/api/', '/graphql', '/ajax/',
            'app.', 'dashboard.', 'admin.',
            '#/', '#!/'  # Hash routing
        ]
        
        for pattern in js_patterns:
            if pattern in url.lower():
                logger.debug(f"JS URL pattern found: {pattern}")
                return True
        
        return False
    
    async def _compare_render_results(self, url: str, basic_html: str) -> bool:
        """
        Compare basic HTML with JS-rendered version to decide if JS is needed.
        
        Args:
            url: URL to compare
            basic_html: Basic HTML content
            
        Returns:
            True if JS rendering provides significantly more content
        """
        try:
            # Quick render with minimal wait time
            js_html, js_metadata = await self.browser_manager.render_page(url, wait_time=1000)
            
            # Compare content lengths
            basic_length = len(basic_html)
            js_length = len(js_html)
            length_improvement = (js_length - basic_length) / max(basic_length, 1)
            
            # Compare text content
            import re
            
            def extract_text(html):
                text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<[^>]+>', '', text)
                return re.sub(r'\s+', ' ', text).strip()
            
            basic_text = extract_text(basic_html)
            js_text = extract_text(js_html)
            
            text_improvement = (len(js_text) - len(basic_text)) / max(len(basic_text), 1)
            
            # Decision criteria
            needs_js = (length_improvement > self.js_threshold or 
                       text_improvement > self.js_threshold * 0.5)
            
            logger.debug(f"Render comparison for {url}: "
                        f"length_improvement={length_improvement:.2f}, "
                        f"text_improvement={text_improvement:.2f}, "
                        f"needs_js={needs_js}")
            
            self.stats['comparison_renders'] += 1
            return needs_js
            
        except Exception as e:
            logger.warning(f"Error in render comparison for {url}: {e}")
            return False
    
    async def _force_render(self, url: str, basic_html: str) -> Tuple[str, Dict[str, Any]]:
        """Force render a URL that's marked as always needing JS."""
        self.stats['forced_renders'] += 1
        return await self._render_with_js(url, basic_html)
    
    async def _render_with_js(self, url: str, basic_html: str, 
                             wait_for: Optional[str] = None,
                             wait_time: int = 2000) -> Tuple[str, Dict[str, Any]]:
        """
        Render a URL with JavaScript and return enhanced content.
        
        Args:
            url: URL to render
            basic_html: Basic HTML for comparison
            wait_for: CSS selector to wait for
            wait_time: Additional wait time in milliseconds
            
        Returns:
            Tuple of (rendered_html, metadata)
        """
        start_time = time.time()
        
        try:
            # Check render cache
            cache_key = f"render_{hash(url)}"
            current_time = time.time()
            
            if self.cache_results and cache_key in self.render_cache:
                cache_entry = self.render_cache[cache_key]
                if current_time - cache_entry['timestamp'] < self.cache_ttl:
                    self.stats['render_cache_hits'] += 1
                    cache_entry['metadata']['cached'] = True
                    return cache_entry['html'], cache_entry['metadata']
            
            # Perform JS rendering
            js_html, js_metadata = await self.browser_manager.render_page(
                url, wait_for=wait_for, wait_time=wait_time
            )
            
            # Calculate improvements
            basic_length = len(basic_html)
            js_length = len(js_html)
            content_improvement = (js_length - basic_length) / max(basic_length, 1)
            
            render_time = time.time() - start_time
            
            # Prepare final metadata
            metadata = {
                'js_rendered': True,
                'render_time': render_time,
                'content_improvement': content_improvement,
                'basic_length': basic_length,
                'js_length': js_length,
                'frameworks': js_metadata.get('frameworks', []),
                'load_time': js_metadata.get('load_time', 0),
                'cached': False
            }
            
            # Cache the result
            if self.cache_results:
                self.render_cache[cache_key] = {
                    'html': js_html,
                    'metadata': metadata.copy(),
                    'timestamp': current_time
                }
            
            self.stats['successful_renders'] += 1
            logger.debug(f"JS rendered {url} in {render_time:.2f}s, improvement: {content_improvement:.2f}")
            
            return js_html, metadata
            
        except Exception as e:
            logger.error(f"Error rendering {url} with JS: {e}")
            self.stats['failed_renders'] += 1
            
            # Fallback to basic HTML
            return basic_html, {
                'js_rendered': False,
                'render_time': time.time() - start_time,
                'content_improvement': 0,
                'error': str(e),
                'fallback': True
            }
    
    def add_force_js_domain(self, domain: str):
        """Add a domain to the force-JS list."""
        self.force_js_domains.add(domain.lower())
        logger.info(f"Added {domain} to force-JS domains")
    
    def add_never_js_domain(self, domain: str):
        """Add a domain to the never-JS list."""
        self.never_js_domains.add(domain.lower())
        logger.info(f"Added {domain} to never-JS domains")
    
    def clear_cache(self):
        """Clear all caches."""
        self.js_detection_cache.clear()
        self.render_cache.clear()
        logger.info("Cleared JS renderer caches")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get JS renderer statistics."""
        browser_stats = self.browser_manager.get_stats()
        
        return {
            'js_detections': self.stats['js_detections'],
            'js_needed': self.stats['js_needed'],
            'successful_renders': self.stats['successful_renders'],
            'failed_renders': self.stats['failed_renders'],
            'forced_renders': self.stats['forced_renders'],
            'comparison_renders': self.stats['comparison_renders'],
            'skipped_never_js': self.stats['skipped_never_js'],
            'skipped_auto_detect': self.stats['skipped_auto_detect'],
            'skipped_default': self.stats['skipped_default'],
            'detection_cache_hits': self.stats['detection_cache_hits'],
            'render_cache_hits': self.stats['render_cache_hits'],
            'detection_cache_size': len(self.js_detection_cache),
            'render_cache_size': len(self.render_cache),
            'force_js_domains': len(self.force_js_domains),
            'never_js_domains': len(self.never_js_domains),
            'browser_manager': browser_stats
        }