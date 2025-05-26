#!/usr/bin/env python3
# utils/browser_mimicry.py - Browser fingerprint mimicry and header rotation

import random
import logging
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger("NewsSystem.BrowserMimicry")

class BrowserMimicry:
    """
    Handles browser fingerprint mimicry including user agents, headers,
    and other browser-specific characteristics to avoid detection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser mimicry system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.current_profile = None
        self.rotation_count = 0
        
        # Statistics
        self.stats = defaultdict(int)
        
        # Browser profiles with realistic headers
        self.browser_profiles = self._load_browser_profiles()
        
        # Select initial profile
        self.rotate_profile()
        
        logger.info("BrowserMimicry initialized with {} profiles".format(len(self.browser_profiles)))
    
    def _load_browser_profiles(self) -> List[Dict[str, Any]]:
        """
        Load browser profiles with realistic user agents and headers.
        
        Returns:
            List of browser profile dictionaries
        """
        profiles = [
            # Chrome profiles
            {
                'name': 'Chrome_Windows_Latest',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': '"Windows"',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'dnt': '1',
                'upgrade_insecure_requests': '1',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1'
            },
            {
                'name': 'Chrome_MacOS_Latest',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'sec_ch_ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': '"macOS"',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'dnt': '1',
                'upgrade_insecure_requests': '1',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1'
            },
            # Firefox profiles
            {
                'name': 'Firefox_Windows_Latest',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.5',
                'accept_encoding': 'gzip, deflate, br',
                'dnt': '1',
                'upgrade_insecure_requests': '1',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1'
            },
            {
                'name': 'Firefox_MacOS_Latest',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.5',
                'accept_encoding': 'gzip, deflate, br',
                'dnt': '1',
                'upgrade_insecure_requests': '1',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1'
            },
            # Safari profiles
            {
                'name': 'Safari_MacOS_Latest',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'dnt': '1',
                'upgrade_insecure_requests': '1'
            },
            # Edge profiles
            {
                'name': 'Edge_Windows_Latest',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
                'sec_ch_ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': '"Windows"',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'dnt': '1',
                'upgrade_insecure_requests': '1',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1'
            }
        ]
        
        return profiles
    
    def rotate_profile(self) -> None:
        """Rotate to a new browser profile."""
        self.current_profile = random.choice(self.browser_profiles)
        self.rotation_count += 1
        self.stats['profile_rotations'] += 1
        
        logger.debug(f"Rotated to profile: {self.current_profile['name']}")
    
    def get_user_agent(self) -> str:
        """
        Get current user agent string.
        
        Returns:
            User agent string
        """
        if not self.current_profile:
            self.rotate_profile()
        
        return self.current_profile['user_agent']
    
    def get_headers(self, url: str, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get complete header set for a request.
        
        Args:
            url: Target URL
            custom_headers: Additional custom headers
            
        Returns:
            Complete headers dictionary
        """
        if not self.current_profile:
            self.rotate_profile()
        
        # Start with profile headers
        headers = {}
        
        # Add user agent
        headers['User-Agent'] = self.current_profile['user_agent']
        
        # Add other profile headers (skip user_agent and name)
        for key, value in self.current_profile.items():
            if key not in ['user_agent', 'name']:
                # Convert underscore headers to proper format
                header_key = key.replace('_', '-').title()
                if header_key.startswith('Sec-Ch-'):
                    header_key = 'Sec-CH-' + header_key[7:]
                elif header_key == 'Dnt':
                    header_key = 'DNT'
                elif header_key.startswith('Sec-'):
                    header_key = 'Sec-' + header_key[4:].replace('-', '-')
                
                headers[header_key] = value
        
        # Add contextual headers based on URL
        headers.update(self._get_contextual_headers(url))
        
        # Add custom headers (these override everything else)
        if custom_headers:
            headers.update(custom_headers)
        
        self.stats['headers_generated'] += 1
        return headers
    
    def _get_contextual_headers(self, url: str) -> Dict[str, str]:
        """
        Get headers that are contextual to the specific URL/site.
        
        Args:
            url: Target URL
            
        Returns:
            Contextual headers dictionary
        """
        headers = {}
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Add referer for non-direct navigation simulation
        if random.random() < 0.3:  # 30% chance of having a referer
            referers = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                f'https://{domain}/',  # Same site referer
            ]
            headers['Referer'] = random.choice(referers)
        
        # Add site-specific headers for known sites
        if 'twitter.com' in domain or 'x.com' in domain:
            headers['X-Twitter-Active-User'] = 'yes'
        elif 'linkedin.com' in domain:
            headers['X-Requested-With'] = 'XMLHttpRequest'
        elif 'facebook.com' in domain:
            headers['Sec-Fetch-Site'] = 'same-origin'
        
        # Add random realistic headers occasionally
        if random.random() < 0.2:  # 20% chance
            optional_headers = {
                'Cache-Control': 'max-age=0',
                'Pragma': 'no-cache',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            for key, value in optional_headers.items():
                if random.random() < 0.5:
                    headers[key] = value
        
        return headers
    
    def should_rotate(self, requests_count: int = 0) -> bool:
        """
        Determine if profile should be rotated based on usage.
        
        Args:
            requests_count: Number of requests made with current profile
            
        Returns:
            True if profile should be rotated
        """
        # Rotate after random number of requests (10-50)
        rotation_threshold = random.randint(10, 50)
        
        return requests_count >= rotation_threshold
    
    def get_profile_info(self) -> Dict[str, Any]:
        """
        Get information about current profile.
        
        Returns:
            Dictionary with profile information
        """
        if not self.current_profile:
            return {}
        
        return {
            'name': self.current_profile['name'],
            'user_agent': self.current_profile['user_agent'],
            'rotation_count': self.rotation_count
        }
    
    def add_custom_profile(self, profile: Dict[str, Any]) -> None:
        """
        Add a custom browser profile.
        
        Args:
            profile: Profile dictionary with headers and user agent
        """
        if 'name' not in profile or 'user_agent' not in profile:
            raise ValueError("Profile must have 'name' and 'user_agent' fields")
        
        self.browser_profiles.append(profile)
        logger.info(f"Added custom profile: {profile['name']}")
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration."""
        self.config.update(config)
        logger.info("BrowserMimicry configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get browser mimicry statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'current_profile': self.current_profile['name'] if self.current_profile else None,
            'total_profiles': len(self.browser_profiles),
            'rotation_count': self.rotation_count,
            'headers_generated': self.stats['headers_generated'],
            'profile_rotations': self.stats['profile_rotations']
        }