#!/usr/bin/env python3
# utils/request_manager.py - Advanced request manager with anti-detection features

import requests
import logging
import time
import random
from urllib.parse import urlparse, urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, Tuple

from .session_manager import SessionManager
from .browser_mimicry import BrowserMimicry
from .rate_limiter import RateLimiter
from .robots_checker import RobotsChecker

logger = logging.getLogger("NewsSystem.RequestManager")

class RequestManager:
    """
    Advanced request manager that handles anti-detection, rate limiting,
    robots.txt checking, and session management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the request manager.
        
        Args:
            config: Configuration dictionary with settings
        """
        self.config = config
        
        # Initialize components
        self.session_manager = SessionManager(config.get('session_config', {}))
        self.browser_mimicry = BrowserMimicry(config.get('browser_config', {}))
        self.rate_limiter = RateLimiter(config.get('rate_limit_config', {}))
        self.robots_checker = RobotsChecker(
            user_agent=self.browser_mimicry.get_user_agent(),
            config=config.get('robots_config', {})
        )
        
        # Request configuration
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.backoff_factor = config.get('backoff_factor', 0.3)
        self.bypass_robots = config.get('bypass_robots', False)
        
        logger.info("RequestManager initialized with advanced anti-detection features")
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Enhanced GET request with all anti-detection features.
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object or None if failed
        """
        return self._make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Enhanced POST request with all anti-detection features.
        
        Args:
            url: URL to post to
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object or None if failed
        """
        return self._make_request('POST', url, **kwargs)
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a request with all anti-detection measures.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments
            
        Returns:
            Response object or None if failed
        """
        # Check robots.txt if not bypassed
        if not self.bypass_robots and not self.robots_checker.allowed(url):
            logger.warning(f"Request blocked by robots.txt: {url}")
            return None
        
        # Apply rate limiting
        wait_time = self.rate_limiter.wait(url)
        if wait_time > 0:
            logger.debug(f"Rate limited, waited {wait_time:.2f}s for {url}")
        
        # Get session for this domain
        session = self.session_manager.get_session(url)
        
        # Prepare headers with browser mimicry
        headers = self._prepare_headers(url, kwargs.get('headers', {}))
        kwargs['headers'] = headers
        
        # Set timeout
        kwargs.setdefault('timeout', self.timeout)
        
        # Make request with retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                # Add random delay between retries
                if attempt > 0:
                    delay = self.backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    logger.debug(f"Retry delay: {delay:.2f}s")
                    time.sleep(delay)
                
                # Make the request
                response = session.request(method, url, **kwargs)
                
                # Check if we got blocked
                if self._is_blocked_response(response):
                    logger.warning(f"Blocked response detected for {url}: {response.status_code}")
                    # Update rate limiter with blocking info
                    self.rate_limiter.record_block(url)
                    # Rotate browser profile for next attempt
                    self.browser_mimicry.rotate_profile()
                    continue
                
                # Record successful request for adaptive rate limiting
                self.rate_limiter.record_success(url, response.elapsed.total_seconds())
                
                logger.debug(f"Successful {method} request to {url}: {response.status_code}")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {url} - {e}")
                # Record failure for adaptive rate limiting
                self.rate_limiter.record_failure(url)
                
                if attempt < self.max_retries:
                    continue
                else:
                    logger.error(f"All retry attempts failed for {url}")
                    return None
        
        return None
    
    def _prepare_headers(self, url: str, custom_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Prepare headers with browser mimicry and custom headers.
        
        Args:
            url: Target URL
            custom_headers: Custom headers to include
            
        Returns:
            Complete headers dictionary
        """
        # Get base browser headers
        headers = self.browser_mimicry.get_headers(url)
        
        # Add custom headers (they override browser headers)
        headers.update(custom_headers)
        
        return headers
    
    def _is_blocked_response(self, response: requests.Response) -> bool:
        """
        Detect if response indicates blocking or bot detection.
        
        Args:
            response: Response object to analyze
            
        Returns:
            True if response indicates blocking
        """
        # Common blocking status codes
        blocking_codes = [403, 429, 503, 520, 521, 522, 524]
        if response.status_code in blocking_codes:
            return True
        
        # Check for common blocking indicators in content
        if response.status_code == 200:
            content = response.text.lower()
            blocking_indicators = [
                'access denied',
                'blocked',
                'captcha',
                'cloudflare',
                'bot detected',
                'rate limit',
                'too many requests',
                'suspicious activity'
            ]
            
            for indicator in blocking_indicators:
                if indicator in content:
                    logger.debug(f"Blocking indicator found: {indicator}")
                    return True
        
        return False
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration for all components.
        
        Args:
            config: New configuration dictionary
        """
        self.config.update(config)
        
        # Update individual components
        if 'session_config' in config:
            self.session_manager.update_config(config['session_config'])
        
        if 'browser_config' in config:
            self.browser_mimicry.update_config(config['browser_config'])
        
        if 'rate_limit_config' in config:
            self.rate_limiter.update_config(config['rate_limit_config'])
        
        if 'robots_config' in config:
            self.robots_checker.update_config(config['robots_config'])
        
        logger.info("RequestManager configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from all components.
        
        Returns:
            Dictionary with component statistics
        """
        return {
            'rate_limiter': self.rate_limiter.get_stats(),
            'session_manager': self.session_manager.get_stats(),
            'browser_mimicry': self.browser_mimicry.get_stats(),
            'robots_checker': self.robots_checker.get_stats()
        }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.session_manager.cleanup()
        logger.info("RequestManager cleanup completed")