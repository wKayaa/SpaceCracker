#!/usr/bin/env python3
"""
Rate Limiter Module
Token bucket rate limiting implementation
"""

import asyncio
import time
import logging

class RateLimiter:
    """Token bucket rate limiter for async operations"""
    
    def __init__(self, rate=2.0, max_tokens=10):
        """
        Initialize rate limiter
        
        Args:
            rate (float): Tokens per second
            max_tokens (int): Maximum tokens in bucket
        """
        self.rate = rate
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        
    async def acquire(self, tokens=1):
        """
        Acquire tokens from the bucket
        
        Args:
            tokens (int): Number of tokens to acquire
        """
        async with self.lock:
            now = time.time()
            
            # Add tokens based on elapsed time
            time_passed = now - self.last_update
            self.tokens = min(self.max_tokens, self.tokens + time_passed * self.rate)
            self.last_update = now
            
            # If not enough tokens, wait
            if self.tokens < tokens:
                sleep_time = (tokens - self.tokens) / self.rate
                self.logger.debug(f"Rate limit hit, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                self.tokens = 0
            else:
                self.tokens -= tokens
                
    def get_status(self):
        """Get current rate limiter status"""
        return {
            'available_tokens': self.tokens,
            'max_tokens': self.max_tokens,
            'rate': self.rate,
            'last_update': self.last_update
        }