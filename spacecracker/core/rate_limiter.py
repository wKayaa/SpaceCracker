import threading
import time

class RateLimiter:
    """Thread-safe token bucket rate limiter"""
    
    def __init__(self, rate_per_sec: int, burst: int):
        self.rate = rate_per_sec
        self.tokens = burst
        self.max_tokens = burst
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens, blocking if necessary"""
        with self.lock:
            now = time.time()
            
            # Add tokens based on elapsed time
            time_passed = now - self.last_update
            self.tokens = min(self.max_tokens, self.tokens + time_passed * self.rate)
            self.last_update = now
            
            # If not enough tokens, calculate wait time
            if self.tokens < tokens:
                sleep_time = (tokens - self.tokens) / self.rate
                time.sleep(sleep_time)
                self.tokens = max(0, self.tokens - tokens)
            else:
                self.tokens -= tokens
            
            return True
    
    def get_status(self) -> dict:
        """Get current rate limiter status"""
        with self.lock:
            return {
                'available_tokens': self.tokens,
                'max_tokens': self.max_tokens,
                'rate': self.rate,
                'last_update': self.last_update
            }