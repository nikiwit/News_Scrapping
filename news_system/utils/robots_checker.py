#!/usr/bin/env python3
# utils/robots_checker.py - Enhanced robots.txt compliance checker with bypass options

import logging
import time
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger("NewsSystem.RobotsChecker")

class RobotsChecker:
    """
    Enhanced robots.txt checker with configurable bypass options,
    caching with TTL, and intelligent error handling.
    """
    
    def __init__(self, user_agent: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the robots checker.
        
        Args:
            user_agent: The user agent string to check permissions for
            config: Configuration dictionary
        """
        self.user_agent = user_agent
        self.config = config or {}
        
        # Configuration options
        self.respect_robots = self.config.get('respect_robots', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        self.request_timeout = self.config.get('request_timeout', 10)
        self.max_retries = self.config.get('max_retries', 2)
        self.aggressive_mode = self.config.get('aggressive_mode', True)
        
        # Domain-specific overrides
        self.domain_overrides = self.config.get('domain_overrides', {})
        self.whitelist_domains = self.config.get('whitelist_domains', [])
        self.blacklist_domains = self.config.get('blacklist_domains', [])
        
        # Cache for RobotFileParser objects with timestamps
        self.parsers: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = defaultdict(int)
        
        logger.info(f"RobotsChecker initialized (respect_robots={self.respect_robots}, aggressive_mode={self.aggressive_mode})")
    
    def allowed(self, url: str) -> bool:
        """
        Check if the URL is allowed by robots.txt or configuration overrides.
        
        Args:
            url: The URL to check
            
        Returns:
            True if scraping is allowed, False otherwise
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        self.stats['total_checks'] += 1
        
        # Check if robots.txt respect is disabled globally
        if not self.respect_robots:
            logger.debug(f"Robots.txt checking disabled, allowing: {url}")
            self.stats['bypassed_global'] += 1
            return True
        
        # Check whitelist (always allow)
        if domain in self.whitelist_domains:
            logger.debug(f"Domain whitelisted, allowing: {domain}")
            self.stats['whitelisted'] += 1
            return True
        
        # Check blacklist (always deny)
        if domain in self.blacklist_domains:
            logger.debug(f"Domain blacklisted, denying: {domain}")
            self.stats['blacklisted'] += 1
            return False
        
        # Check domain-specific overrides
        if domain in self.domain_overrides:
            override = self.domain_overrides[domain]
            if isinstance(override, bool):
                logger.debug(f"Domain override for {domain}: {override}")
                self.stats['overridden'] += 1
                return override
        
        # Get robots.txt parser for this domain
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        parser = self._get_parser(base_url)
        
        if parser is None:
            # No robots.txt or failed to fetch
            if self.aggressive_mode:
                logger.debug(f"No robots.txt found, aggressive mode allowing: {url}")
                self.stats['no_robots_allowed'] += 1
                return True
            else:
                logger.debug(f"No robots.txt found, conservative mode denying: {url}")
                self.stats['no_robots_denied'] += 1
                return False
        
        # Check with robots.txt
        try:
            allowed = parser.can_fetch(self.user_agent, url)
            
            if allowed:
                self.stats['robots_allowed'] += 1
            else:
                self.stats['robots_denied'] += 1
                logger.info(f"Robots.txt denies access: {url}")
            
            return allowed
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            self.stats['check_errors'] += 1
            
            # Default behavior on error
            return self.aggressive_mode
    
    def _get_parser(self, base_url: str) -> Optional[RobotFileParser]:
        """
        Get or create a robots.txt parser for the base URL.
        
        Args:
            base_url: Base URL (scheme + netloc)
            
        Returns:
            RobotFileParser or None if unavailable
        """
        current_time = time.time()
        
        # Check if we have a cached parser that's still valid
        if base_url in self.parsers:
            cache_entry = self.parsers[base_url]
            if current_time - cache_entry['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                return cache_entry['parser']
            else:
                # Cache expired
                logger.debug(f"Robots.txt cache expired for {base_url}")
                self.stats['cache_expired'] += 1
        
        # Fetch new robots.txt
        parser = self._fetch_robots_txt(base_url)
        
        # Cache the result (even if None)
        self.parsers[base_url] = {
            'parser': parser,
            'timestamp': current_time
        }
        
        self.stats['cache_misses'] += 1
        return parser
    
    def _fetch_robots_txt(self, base_url: str) -> Optional[RobotFileParser]:
        """
        Fetch and parse robots.txt for a base URL.
        
        Args:
            base_url: Base URL to fetch robots.txt for
            
        Returns:
            RobotFileParser or None if failed
        """
        robots_url = f"{base_url}/robots.txt"
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Fetching robots.txt: {robots_url} (attempt {attempt + 1})")
                
                # Use requests for better control and timeout handling
                response = requests.get(
                    robots_url,
                    timeout=self.request_timeout,
                    headers={'User-Agent': self.user_agent},
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    # Successfully fetched robots.txt
                    rp = RobotFileParser()
                    rp.set_url(robots_url)
                    
                    # Parse the content directly instead of fetching again
                    robots_content = response.text
                    rp.read()  # This normally fetches, but we'll override
                    
                    # Manually set the robots content
                    import io
                    rp.fp = io.StringIO(robots_content)
                    rp.read()
                    
                    logger.debug(f"Successfully parsed robots.txt for {base_url}")
                    self.stats['robots_fetched'] += 1
                    return rp
                    
                elif response.status_code == 404:
                    # No robots.txt file
                    logger.debug(f"No robots.txt found for {base_url}")
                    self.stats['robots_not_found'] += 1
                    return None
                    
                else:
                    logger.warning(f"HTTP {response.status_code} when fetching robots.txt: {robots_url}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching robots.txt: {robots_url}")
                self.stats['fetch_timeouts'] += 1
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching robots.txt: {robots_url} - {e}")
                self.stats['fetch_errors'] += 1
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                logger.debug(f"Retrying robots.txt fetch in {wait_time}s")
                time.sleep(wait_time)
        
        # All attempts failed
        logger.error(f"Failed to fetch robots.txt after {self.max_retries + 1} attempts: {robots_url}")
        self.stats['fetch_failed'] += 1
        return None
    
    def invalidate_cache(self, url: Optional[str] = None) -> None:
        """
        Invalidate robots.txt cache for a specific domain or all domains.
        
        Args:
            url: URL to invalidate cache for, or None for all
        """
        if url:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url in self.parsers:
                del self.parsers[base_url]
                logger.info(f"Invalidated robots.txt cache for: {base_url}")
                self.stats['cache_invalidated'] += 1
        else:
            # Clear all cache
            cache_size = len(self.parsers)
            self.parsers.clear()
            logger.info(f"Cleared all robots.txt cache ({cache_size} entries)")
            self.stats['cache_cleared'] += 1
    
    def add_domain_override(self, domain: str, allowed: bool) -> None:
        """
        Add a domain-specific override.
        
        Args:
            domain: Domain to override
            allowed: Whether to allow or deny requests to this domain
        """
        self.domain_overrides[domain] = allowed
        logger.info(f"Added domain override: {domain} -> {allowed}")
    
    def whitelist_domain(self, domain: str) -> None:
        """
        Add a domain to the whitelist (always allowed).
        
        Args:
            domain: Domain to whitelist
        """
        if domain not in self.whitelist_domains:
            self.whitelist_domains.append(domain)
            logger.info(f"Whitelisted domain: {domain}")
    
    def blacklist_domain(self, domain: str) -> None:
        """
        Add a domain to the blacklist (always denied).
        
        Args:
            domain: Domain to blacklist
        """
        if domain not in self.blacklist_domains:
            self.blacklist_domains.append(domain)
            logger.info(f"Blacklisted domain: {domain}")
    
    def set_respect_robots(self, respect: bool) -> None:
        """
        Enable or disable robots.txt respect globally.
        
        Args:
            respect: Whether to respect robots.txt files
        """
        old_value = self.respect_robots
        self.respect_robots = respect
        
        if old_value != respect:
            logger.info(f"Changed robots.txt respect: {old_value} -> {respect}")
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration."""
        self.config.update(config)
        
        # Update settings
        self.respect_robots = config.get('respect_robots', self.respect_robots)
        self.cache_ttl = config.get('cache_ttl', self.cache_ttl)
        self.aggressive_mode = config.get('aggressive_mode', self.aggressive_mode)
        
        # Update domain lists
        if 'whitelist_domains' in config:
            self.whitelist_domains = config['whitelist_domains']
        if 'blacklist_domains' in config:
            self.blacklist_domains = config['blacklist_domains']
        if 'domain_overrides' in config:
            self.domain_overrides.update(config['domain_overrides'])
        
        logger.info("RobotsChecker configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get robots checker statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_checks': self.stats['total_checks'],
            'robots_allowed': self.stats['robots_allowed'],
            'robots_denied': self.stats['robots_denied'],
            'bypassed_global': self.stats['bypassed_global'],
            'whitelisted': self.stats['whitelisted'],
            'blacklisted': self.stats['blacklisted'],
            'overridden': self.stats['overridden'],
            'no_robots_allowed': self.stats['no_robots_allowed'],
            'no_robots_denied': self.stats['no_robots_denied'],
            'robots_fetched': self.stats['robots_fetched'],
            'robots_not_found': self.stats['robots_not_found'],
            'fetch_errors': self.stats['fetch_errors'],
            'fetch_timeouts': self.stats['fetch_timeouts'],
            'fetch_failed': self.stats['fetch_failed'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_expired': self.stats['cache_expired'],
            'cache_invalidated': self.stats['cache_invalidated'],
            'cache_cleared': self.stats['cache_cleared'],
            'check_errors': self.stats['check_errors'],
            'cached_domains': len(self.parsers),
            'whitelisted_domains': len(self.whitelist_domains),
            'blacklisted_domains': len(self.blacklist_domains),
            'domain_overrides': len(self.domain_overrides)
        }