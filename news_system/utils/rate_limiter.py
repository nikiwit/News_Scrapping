#!/usr/bin/env python3
# utils/rate_limiter.py - Enhanced adaptive rate limiting with anti-detection features

import time
import random
import logging
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from collections import defaultdict, deque

logger = logging.getLogger("NewsSystem.RateLimiter")

class RateLimiter:
    """
    Advanced rate limiter with adaptive delays, exponential backoff,
    and intelligent response to server behavior.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the enhanced rate limiter.
        
        Args:
            config: Configuration dictionary or float for backward compatibility
        """
        # Handle backward compatibility
        if isinstance(config, (int, float)):
            config = {'default_delay': config}
        
        self.config = config
        
        # Basic configuration
        self.default_delay = config.get('default_delay', 2.0)
        self.max_delay = config.get('max_delay', 60.0)
        self.min_delay = config.get('min_delay', 0.5)
        
        # Adaptive configuration
        self.adaptive_enabled = config.get('adaptive_enabled', True)
        self.response_time_threshold = config.get('response_time_threshold', 5.0)
        self.block_penalty_multiplier = config.get('block_penalty_multiplier', 3.0)
        self.success_reward_factor = config.get('success_reward_factor', 0.9)
        
        # Jitter configuration
        self.jitter_enabled = config.get('jitter_enabled', True)
        self.jitter_range = config.get('jitter_range', 0.3)  # +/- 30%
        
        # Burst allowance
        self.burst_size = config.get('burst_size', 3)
        self.burst_window = config.get('burst_window', 60)  # seconds
        
        # Domain-specific tracking
        self.last_request_time: Dict[str, float] = {}
        self.current_delays: Dict[str, float] = {}
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.block_counts: Dict[str, int] = defaultdict(int)
        self.burst_requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.burst_size))
        
        # Statistics
        self.stats = defaultdict(int)
        
        logger.info("Enhanced RateLimiter initialized with adaptive features")
    
    def wait(self, url: str) -> float:
        """
        Wait if necessary to maintain rate limiting for the domain.
        
        Args:
            url: The URL that will be requested
            
        Returns:
            The actual time waited in seconds
        """
        domain = urlparse(url).netloc
        now = time.time()
        
        # Get current delay for this domain
        current_delay = self._get_current_delay(domain)
        
        # Check burst allowance
        if self._can_burst(domain, now):
            logger.debug(f"Burst allowed for {domain}")
            self.stats['burst_requests'] += 1
            self._record_burst_request(domain, now)
            return 0
        
        # Calculate wait time
        if domain in self.last_request_time:
            elapsed = now - self.last_request_time[domain]
            
            if elapsed < current_delay:
                wait_time = current_delay - elapsed
                
                # Add jitter to prevent synchronization
                if self.jitter_enabled:
                    jitter = wait_time * self.jitter_range * (random.random() * 2 - 1)
                    wait_time = max(0, wait_time + jitter)
                
                time.sleep(wait_time)
                waited = wait_time
                self.stats['total_wait_time'] += waited
                self.stats['wait_events'] += 1
            else:
                waited = 0
        else:
            waited = 0
        
        # Update last request time
        self.last_request_time[domain] = time.time()
        self.stats['total_requests'] += 1
        
        return waited
    
    def _get_current_delay(self, domain: str) -> float:
        """
        Get the current delay for a domain based on its performance history.
        
        Args:
            domain: Domain to get delay for
            
        Returns:
            Current delay in seconds
        """
        if domain not in self.current_delays:
            self.current_delays[domain] = self.default_delay
        
        if not self.adaptive_enabled:
            return self.current_delays[domain]
        
        # Calculate adaptive delay based on response times and failures
        base_delay = self.current_delays[domain]
        
        # Adjust based on recent response times
        if domain in self.response_times and self.response_times[domain]:
            avg_response_time = sum(self.response_times[domain]) / len(self.response_times[domain])
            
            if avg_response_time > self.response_time_threshold:
                # Slow responses - increase delay
                adjustment = min(2.0, avg_response_time / self.response_time_threshold)
                base_delay *= adjustment
                logger.debug(f"Increased delay for {domain} due to slow responses: {base_delay:.2f}s")
        
        # Adjust based on failure rate
        total_requests = self.success_counts[domain] + self.failure_counts[domain]
        if total_requests > 5:  # Only adjust after some history
            failure_rate = self.failure_counts[domain] / total_requests
            
            if failure_rate > 0.2:  # More than 20% failures
                base_delay *= (1 + failure_rate * 2)
                logger.debug(f"Increased delay for {domain} due to failures: {base_delay:.2f}s")
        
        # Apply block penalty
        if self.block_counts[domain] > 0:
            penalty = self.block_penalty_multiplier ** self.block_counts[domain]
            base_delay *= penalty
            logger.debug(f"Applied block penalty for {domain}: {base_delay:.2f}s")
        
        # Ensure delay is within bounds
        base_delay = max(self.min_delay, min(self.max_delay, base_delay))
        
        return base_delay
    
    def _can_burst(self, domain: str, current_time: float) -> bool:
        """
        Check if a burst request is allowed for this domain.
        
        Args:
            domain: Domain to check
            current_time: Current timestamp
            
        Returns:
            True if burst is allowed
        """
        # Clean old burst requests
        while (self.burst_requests[domain] and 
               current_time - self.burst_requests[domain][0] > self.burst_window):
            self.burst_requests[domain].popleft()
        
        # Check if we have burst capacity
        return len(self.burst_requests[domain]) < self.burst_size
    
    def _record_burst_request(self, domain: str, timestamp: float) -> None:
        """Record a burst request for tracking."""
        self.burst_requests[domain].append(timestamp)
    
    def record_success(self, url: str, response_time: float) -> None:
        """
        Record a successful request to adjust future delays.
        
        Args:
            url: URL that was successfully requested
            response_time: Response time in seconds
        """
        domain = urlparse(url).netloc
        
        # Record response time
        self.response_times[domain].append(response_time)
        
        # Increment success count
        self.success_counts[domain] += 1
        
        # Reduce delay for consistent successes
        if self.adaptive_enabled and self.success_counts[domain] % 5 == 0:
            if domain in self.current_delays:
                old_delay = self.current_delays[domain]
                self.current_delays[domain] *= self.success_reward_factor
                self.current_delays[domain] = max(self.min_delay, self.current_delays[domain])
                
                if self.current_delays[domain] < old_delay:
                    logger.debug(f"Reduced delay for {domain}: {self.current_delays[domain]:.2f}s")
        
        self.stats['successful_requests'] += 1
    
    def record_failure(self, url: str) -> None:
        """
        Record a failed request to adjust future delays.
        
        Args:
            url: URL that failed
        """
        domain = urlparse(url).netloc
        
        # Increment failure count
        self.failure_counts[domain] += 1
        
        # Increase delay after failures
        if self.adaptive_enabled:
            if domain not in self.current_delays:
                self.current_delays[domain] = self.default_delay
            
            # Exponential backoff on repeated failures
            failure_multiplier = min(3.0, 1.5 ** min(self.failure_counts[domain], 5))
            self.current_delays[domain] = min(
                self.max_delay,
                self.current_delays[domain] * failure_multiplier
            )
            
            logger.debug(f"Increased delay for {domain} after failure: {self.current_delays[domain]:.2f}s")
        
        self.stats['failed_requests'] += 1
    
    def record_block(self, url: str) -> None:
        """
        Record that a request was blocked (403, 429, etc.).
        
        Args:
            url: URL that was blocked
        """
        domain = urlparse(url).netloc
        
        # Increment block count
        self.block_counts[domain] += 1
        
        # Significantly increase delay after being blocked
        if domain not in self.current_delays:
            self.current_delays[domain] = self.default_delay
        
        old_delay = self.current_delays[domain]
        self.current_delays[domain] = min(
            self.max_delay,
            old_delay * self.block_penalty_multiplier
        )
        
        logger.warning(f"Blocked request for {domain}, increased delay: {self.current_delays[domain]:.2f}s")
        self.stats['blocked_requests'] += 1
    
    def reset_domain(self, url: str) -> None:
        """
        Reset rate limiting data for a domain.
        
        Args:
            url: URL whose domain should be reset
        """
        domain = urlparse(url).netloc
        
        # Reset all tracking for this domain
        self.current_delays.pop(domain, None)
        self.last_request_time.pop(domain, None)
        self.response_times.pop(domain, None)
        self.failure_counts.pop(domain, None)
        self.success_counts.pop(domain, None)
        self.block_counts.pop(domain, None)
        self.burst_requests.pop(domain, None)
        
        logger.info(f"Reset rate limiting data for domain: {domain}")
        self.stats['domain_resets'] += 1
    
    def get_domain_info(self, url: str) -> Dict[str, Any]:
        """
        Get rate limiting information for a domain.
        
        Args:
            url: URL to get domain info for
            
        Returns:
            Dictionary with domain rate limiting info
        """
        domain = urlparse(url).netloc
        
        return {
            'domain': domain,
            'current_delay': self.current_delays.get(domain, self.default_delay),
            'success_count': self.success_counts[domain],
            'failure_count': self.failure_counts[domain],
            'block_count': self.block_counts[domain],
            'avg_response_time': (
                sum(self.response_times[domain]) / len(self.response_times[domain])
                if self.response_times[domain] else 0
            ),
            'burst_capacity': self.burst_size - len(self.burst_requests[domain])
        }
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration."""
        self.config.update(config)
        
        # Update settings
        self.default_delay = config.get('default_delay', self.default_delay)
        self.max_delay = config.get('max_delay', self.max_delay)
        self.min_delay = config.get('min_delay', self.min_delay)
        self.adaptive_enabled = config.get('adaptive_enabled', self.adaptive_enabled)
        
        logger.info("RateLimiter configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'blocked_requests': self.stats['blocked_requests'],
            'burst_requests': self.stats['burst_requests'],
            'wait_events': self.stats['wait_events'],
            'total_wait_time': round(self.stats['total_wait_time'], 2),
            'domain_resets': self.stats['domain_resets'],
            'tracked_domains': len(self.current_delays),
            'avg_delay': (
                sum(self.current_delays.values()) / len(self.current_delays)
                if self.current_delays else self.default_delay
            )
        }