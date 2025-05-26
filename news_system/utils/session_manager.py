#!/usr/bin/env python3
# utils/session_manager.py - Session and cookie management for persistent connections

import requests
import logging
import time
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger("NewsSystem.SessionManager")

class SessionManager:
    """
    Manages HTTP sessions with connection pooling, cookie persistence,
    and automatic session rotation for better stealth.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the session manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Session storage (domain -> session)
        self.sessions: Dict[str, requests.Session] = {}
        self.session_creation_time: Dict[str, float] = {}
        
        # Configuration
        self.session_lifetime = config.get('session_lifetime', 3600)  # 1 hour
        self.max_sessions = config.get('max_sessions', 50)
        self.connection_pool_size = config.get('connection_pool_size', 10)
        self.connection_pool_maxsize = config.get('connection_pool_maxsize', 20)
        
        # Retry configuration
        self.retry_config = {
            'total': config.get('retry_total', 3),
            'backoff_factor': config.get('retry_backoff_factor', 0.3),
            'status_forcelist': config.get('retry_status_codes', [500, 502, 503, 504])
        }
        
        # Statistics
        self.stats = defaultdict(int)
        
        logger.info("SessionManager initialized")
    
    def get_session(self, url: str) -> requests.Session:
        """
        Get or create a session for the given URL's domain.
        
        Args:
            url: URL to get session for
            
        Returns:
            Configured requests session
        """
        domain = urlparse(url).netloc
        current_time = time.time()
        
        # Check if we need to create a new session
        if (domain not in self.sessions or 
            current_time - self.session_creation_time.get(domain, 0) > self.session_lifetime):
            
            # Clean up old session if it exists
            if domain in self.sessions:
                self.sessions[domain].close()
                self.stats['sessions_rotated'] += 1
            
            # Create new session
            self.sessions[domain] = self._create_session()
            self.session_creation_time[domain] = current_time
            self.stats['sessions_created'] += 1
            
            logger.debug(f"Created new session for domain: {domain}")
        
        # Clean up old sessions if we have too many
        self._cleanup_old_sessions()
        
        self.stats['session_requests'] += 1
        return self.sessions[domain]
    
    def _create_session(self) -> requests.Session:
        """
        Create a new configured session.
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.retry_config['total'],
            backoff_factor=self.retry_config['backoff_factor'],
            status_forcelist=self.retry_config['status_forcelist']
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=self.connection_pool_size,
            pool_maxsize=self.connection_pool_maxsize,
            max_retries=retry_strategy
        )
        
        # Mount adapters for both HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Configure session defaults
        session.headers.update({
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old or excess sessions."""
        current_time = time.time()
        
        # Remove expired sessions
        expired_domains = []
        for domain, creation_time in self.session_creation_time.items():
            if current_time - creation_time > self.session_lifetime:
                expired_domains.append(domain)
        
        for domain in expired_domains:
            if domain in self.sessions:
                self.sessions[domain].close()
                del self.sessions[domain]
                del self.session_creation_time[domain]
                self.stats['sessions_expired'] += 1
                logger.debug(f"Expired session for domain: {domain}")
        
        # If we still have too many sessions, remove oldest ones
        if len(self.sessions) > self.max_sessions:
            # Sort by creation time and remove oldest
            sorted_domains = sorted(
                self.session_creation_time.items(),
                key=lambda x: x[1]
            )
            
            domains_to_remove = len(self.sessions) - self.max_sessions
            for domain, _ in sorted_domains[:domains_to_remove]:
                if domain in self.sessions:
                    self.sessions[domain].close()
                    del self.sessions[domain]
                    del self.session_creation_time[domain]
                    self.stats['sessions_cleaned'] += 1
                    logger.debug(f"Cleaned up excess session for domain: {domain}")
    
    def invalidate_session(self, url: str) -> None:
        """
        Invalidate and recreate session for a domain (useful when blocked).
        
        Args:
            url: URL whose domain session should be invalidated
        """
        domain = urlparse(url).netloc
        
        if domain in self.sessions:
            self.sessions[domain].close()
            del self.sessions[domain]
            del self.session_creation_time[domain]
            self.stats['sessions_invalidated'] += 1
            logger.info(f"Invalidated session for domain: {domain}")
    
    def get_session_cookies(self, url: str) -> Dict[str, str]:
        """
        Get cookies for a specific domain.
        
        Args:
            url: URL to get cookies for
            
        Returns:
            Dictionary of cookies
        """
        domain = urlparse(url).netloc
        if domain in self.sessions:
            session = self.sessions[domain]
            return {cookie.name: cookie.value for cookie in session.cookies}
        return {}
    
    def set_session_cookies(self, url: str, cookies: Dict[str, str]) -> None:
        """
        Set cookies for a specific domain session.
        
        Args:
            url: URL to set cookies for
            cookies: Dictionary of cookie name-value pairs
        """
        session = self.get_session(url)
        
        for name, value in cookies.items():
            session.cookies.set(name, value, domain=urlparse(url).netloc)
        
        logger.debug(f"Set {len(cookies)} cookies for domain: {urlparse(url).netloc}")
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration."""
        self.config.update(config)
        
        # Update settings
        self.session_lifetime = config.get('session_lifetime', self.session_lifetime)
        self.max_sessions = config.get('max_sessions', self.max_sessions)
        
        logger.info("SessionManager configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get session manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'active_sessions': len(self.sessions),
            'total_created': self.stats['sessions_created'],
            'total_requests': self.stats['session_requests'],
            'rotated': self.stats['sessions_rotated'],
            'expired': self.stats['sessions_expired'],
            'cleaned': self.stats['sessions_cleaned'],
            'invalidated': self.stats['sessions_invalidated']
        }
    
    def cleanup(self) -> None:
        """Close all sessions and clean up resources."""
        for session in self.sessions.values():
            session.close()
        
        self.sessions.clear()
        self.session_creation_time.clear()
        
        logger.info(f"Closed {len(self.sessions)} sessions during cleanup")