#!/usr/bin/env python3
"""
Performance Management Module
Smart performance optimization and system resource management
"""

import psutil
import threading
import time
import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class PerformanceProfile:
    """Performance profile configuration"""
    threads: int
    rate_limit: int
    burst: int
    memory_limit_mb: int
    cpu_threshold: float
    name: str

class PerformanceManager:
    """Manages performance optimization and system resources"""
    
    def __init__(self):
        self.current_profile = None
        self._monitoring_thread = None
        self._monitoring_active = False
        self._stats = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'memory_available': 0.0,
            'thread_count': 0,
            'http_requests_per_sec': 0,
            'urls_processed': 0,
            'start_time': time.time()
        }
        self._stats_lock = threading.Lock()
        
        # Define performance profiles
        self.profiles = {
            'low': PerformanceProfile(
                threads=10,
                rate_limit=2,
                burst=5,
                memory_limit_mb=256,
                cpu_threshold=30.0,
                name='Low Performance'
            ),
            'normal': PerformanceProfile(
                threads=25,
                rate_limit=5,
                burst=10,
                memory_limit_mb=512,
                cpu_threshold=60.0,
                name='Normal Performance'
            ),
            'high': PerformanceProfile(
                threads=50,
                rate_limit=15,
                burst=30,
                memory_limit_mb=1024,
                cpu_threshold=80.0,
                name='High Performance'
            ),
            'vps': PerformanceProfile(
                threads=100,
                rate_limit=50,
                burst=100,
                memory_limit_mb=2048,
                cpu_threshold=85.0,
                name='VPS High-Bandwidth'
            ),
            'ultra': PerformanceProfile(
                threads=200,
                rate_limit=100,
                burst=200,
                memory_limit_mb=4096,
                cpu_threshold=90.0,
                name='Ultra Performance'
            ),
            'auto': None  # Will be determined automatically
        }
    
    def auto_detect_profile(self) -> PerformanceProfile:
        """Auto-detect optimal performance profile based on system resources"""
        try:
            # Get system information
            cpu_count = psutil.cpu_count(logical=True)
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            # Determine profile based on resources
            if cpu_count >= 16 and memory_gb >= 16:
                # Very high-end system (VPS/Dedicated)
                return PerformanceProfile(
                    threads=min(200, cpu_count * 16),
                    rate_limit=100,
                    burst=200,
                    memory_limit_mb=min(4096, int(memory_gb * 1024 * 0.4)),
                    cpu_threshold=85.0,
                    name='Auto-Detected Ultra Performance'
                )
            elif cpu_count >= 8 and memory_gb >= 8:
                # High-end system (Good VPS)
                return PerformanceProfile(
                    threads=min(100, cpu_count * 12),
                    rate_limit=50,
                    burst=100,
                    memory_limit_mb=min(2048, int(memory_gb * 1024 * 0.35)),
                    cpu_threshold=80.0,
                    name='Auto-Detected VPS Performance'
                )
            elif cpu_count >= 4 and memory_gb >= 4:
                # Mid-range system
                return PerformanceProfile(
                    threads=min(50, cpu_count * 8),
                    rate_limit=10,
                    burst=20,
                    memory_limit_mb=min(1024, int(memory_gb * 1024 * 0.25)),
                    cpu_threshold=65.0,
                    name='Auto-Detected Normal Performance'
                )
            else:
                # Low-end system
                return PerformanceProfile(
                    threads=min(25, cpu_count * 4),
                    rate_limit=5,
                    burst=10,
                    memory_limit_mb=min(512, int(memory_gb * 1024 * 0.2)),
                    cpu_threshold=50.0,
                    name='Auto-Detected Low Performance'
                )
                
        except Exception:
            # Fallback to normal profile
            return self.profiles['normal']
    
    def set_performance_mode(self, mode: str) -> PerformanceProfile:
        """Set performance mode and return the profile"""
        if mode == 'auto':
            self.current_profile = self.auto_detect_profile()
        elif mode in self.profiles:
            self.current_profile = self.profiles[mode]
        else:
            raise ValueError(f"Unknown performance mode: {mode}")
        
        return self.current_profile
    
    def get_current_profile(self) -> PerformanceProfile:
        """Get current performance profile"""
        if self.current_profile is None:
            self.current_profile = self.auto_detect_profile()
        return self.current_profile
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self._monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2)
    
    def _monitor_resources(self):
        """Monitor system resources in background"""
        while self._monitoring_active:
            try:
                with self._stats_lock:
                    # Update CPU usage
                    self._stats['cpu_usage'] = psutil.cpu_percent(interval=1)
                    
                    # Update memory usage
                    memory = psutil.virtual_memory()
                    self._stats['memory_usage'] = memory.used / (1024**2)  # MB
                    self._stats['memory_available'] = memory.available / (1024**2)  # MB
                    
                    # Update thread count
                    current_process = psutil.Process()
                    self._stats['thread_count'] = current_process.num_threads()
                    
            except Exception:
                pass
            
            time.sleep(2)  # Update every 2 seconds
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        with self._stats_lock:
            stats = self._stats.copy()
            
        # Add calculated fields
        elapsed = time.time() - stats['start_time']
        stats['elapsed_seconds'] = elapsed
        stats['elapsed_formatted'] = self._format_elapsed_time(elapsed)
        
        # Calculate rates
        if elapsed > 0:
            stats['urls_per_second'] = stats['urls_processed'] / elapsed
        else:
            stats['urls_per_second'] = 0
        
        return stats
    
    def update_stats(self, **kwargs):
        """Update performance statistics"""
        with self._stats_lock:
            for key, value in kwargs.items():
                if key in self._stats:
                    if key == 'urls_processed':
                        self._stats[key] += value  # Increment processed count
                    else:
                        self._stats[key] = value
    
    def _format_elapsed_time(self, seconds: float) -> str:
        """Format elapsed time as human readable string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def should_throttle(self) -> bool:
        """Check if scanning should be throttled due to resource constraints"""
        stats = self.get_stats()
        profile = self.get_current_profile()
        
        # Check CPU usage
        if stats['cpu_usage'] > profile.cpu_threshold:
            return True
        
        # Check memory usage
        if stats['memory_usage'] > profile.memory_limit_mb:
            return True
        
        return False
    
    def get_throttle_delay(self) -> float:
        """Get recommended delay for throttling"""
        stats = self.get_stats()
        profile = self.get_current_profile()
        
        # Calculate delay based on resource usage
        cpu_ratio = stats['cpu_usage'] / profile.cpu_threshold
        memory_ratio = stats['memory_usage'] / profile.memory_limit_mb
        
        max_ratio = max(cpu_ratio, memory_ratio)
        
        if max_ratio > 1.5:
            return 1.0  # 1 second delay for high resource usage
        elif max_ratio > 1.2:
            return 0.5  # 0.5 second delay for medium resource usage
        elif max_ratio > 1.0:
            return 0.1  # 0.1 second delay for slight resource usage
        
        return 0.0  # No delay needed
    
    def optimize_for_target_count(self, target_count: int) -> PerformanceProfile:
        """Optimize performance profile based on target count"""
        current = self.get_current_profile()
        
        # Adjust threads based on target count
        if target_count > 10000:
            # Large scan - use more threads but lower rate
            optimized = PerformanceProfile(
                threads=min(current.threads * 2, 100),
                rate_limit=max(current.rate_limit // 2, 2),
                burst=current.burst,
                memory_limit_mb=current.memory_limit_mb * 2,
                cpu_threshold=current.cpu_threshold,
                name=f"{current.name} (Large Scan Optimized)"
            )
        elif target_count > 1000:
            # Medium scan - balanced approach
            optimized = PerformanceProfile(
                threads=current.threads,
                rate_limit=current.rate_limit,
                burst=current.burst,
                memory_limit_mb=current.memory_limit_mb,
                cpu_threshold=current.cpu_threshold,
                name=f"{current.name} (Medium Scan Optimized)"
            )
        else:
            # Small scan - higher rate, fewer threads
            optimized = PerformanceProfile(
                threads=min(current.threads, 25),
                rate_limit=current.rate_limit * 2,
                burst=current.burst,
                memory_limit_mb=current.memory_limit_mb,
                cpu_threshold=current.cpu_threshold,
                name=f"{current.name} (Small Scan Optimized)"
            )
        
        self.current_profile = optimized
        return optimized
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024**2)
        except Exception:
            return 0.0
    
    def cleanup_memory(self):
        """Perform memory cleanup operations"""
        try:
            import gc
            gc.collect()  # Force garbage collection
        except Exception:
            pass

# Global instance
_performance_manager = None

def get_performance_manager() -> PerformanceManager:
    """Get global performance manager instance"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = PerformanceManager()
    return _performance_manager