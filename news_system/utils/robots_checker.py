#!/usr/bin/env python3
# utils/robots_checker.py - Robots.txt compliance checker

import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger("robots_checker")

class RobotsChecker:
    """
    Checks robots.txt files to ensure compliance with website scraping policies.
    """
    
    def __init__(self, user_agent):
        """
        Initialize the robots checker with a user agent.
        
        Args:
            user_agent (str): The user agent string to check permissions for.
        """
        self.user_agent = user_agent
        self.parsers = {}  # Cache for RobotFileParser objects
        
    def allowed(self, url):
        """
        Check if the URL is allowed by the website's robots.txt file.
        
        Args:
            url (str): The URL to check.
            
        Returns:
            bool: True if scraping is allowed, False otherwise.
        """
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        
        # Return cached result if available
        if base in self.parsers:
            return self.parsers[base].can_fetch(self.user_agent, url)
        
        # Create and read the robots.txt file
        rp = RobotFileParser()
        rp.set_url(f"{base}/robots.txt")
        
        try:
            rp.read()
            self.parsers[base] = rp
            allowed = rp.can_fetch(self.user_agent, url)
            
            if not allowed:
                logger.warning(f"Robots.txt disallows: {url}")
                
            return allowed
        except Exception as e:
            logger.error(f"Error reading robots.txt for {base}: {e}")
            return False  # Default to disallowed if we can't read the robots.txt