#!/usr/bin/env python3
# utils/rate_limiter.py - Rate limiting utility to prevent overloading websites

import time
from urllib.parse import urlparse

class RateLimiter:
    """
    Enforces a delay between requests to the same domain to prevent overloading
    websites and to comply with ethical scraping practices.
    """
    
    def __init__(self, delay_seconds):
        """
        Initialize the rate limiter with a specified delay.
        
        Args:
            delay_seconds (float): Minimum time in seconds to wait between 
                                   requests to the same domain.
        """
        self.delay = delay_seconds
        self.last_request_time = {}
    
    def wait(self, url):
        """
        Wait if necessary to maintain the minimum delay between requests
        to the same domain.
        
        Args:
            url (str): The URL that will be requested.
            
        Returns:
            float: The actual time waited in seconds.
        """
        domain = urlparse(url).netloc
        now = time.time()
        
        # Calculate time since last request to this domain
        if domain in self.last_request_time:
            elapsed = now - self.last_request_time[domain]
            
            # Wait if we haven't waited long enough
            if elapsed < self.delay:
                wait_time = self.delay - elapsed
                time.sleep(wait_time)
                waited = wait_time
            else:
                waited = 0
        else:
            waited = 0
            
        # Update the last request time
        self.last_request_time[domain] = time.time()
        
        return waited