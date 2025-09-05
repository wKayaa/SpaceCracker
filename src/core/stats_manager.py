import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import random
import string
from .crack_manager import CrackManager

class StatsManager:
    def __init__(self):
        self.crack_manager = CrackManager()
        self.start_time = time.time()
        self.stats = {
            'hits': 0,
            'checked_paths': 0,
            'checked_urls': 0,
            'invalid_urls': 0,
            'total_urls': 0,
            'max_urls': 250000,
            'threads': 5000,
            'timeout': 20,
            'status': 'running',
            'docker_infected': 0,
            'k8s_infected': 0,
            'credentials_found': {},
            'current_target': '',
            'current_file': ''
        }
    
    def get_crack_id(self) -> str:
        """Generate new crack ID for a finding"""
        return self.crack_manager.generate_crack_id()
    
    def update_stats(self, **kwargs):
        """Update statistics with new values"""
        for key, value in kwargs.items():
            if key in self.stats:
                if key in ['hits', 'checked_paths', 'checked_urls', 'invalid_urls', 'docker_infected', 'k8s_infected']:
                    # Increment counters
                    self.stats[key] += value
                else:
                    self.stats[key] = value
    
    def get_formatted_output(self) -> str:
        """Return formatted statistics"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = time.time() - self.start_time
        progress = (self.stats['checked_urls'] / self.stats['max_urls']) * 100 if self.stats['max_urls'] > 0 else 0
        
        # Calculate ETA
        if progress > 0:
            total_time_estimate = elapsed / (progress / 100)
            remaining = total_time_estimate - elapsed
            eta = str(timedelta(seconds=int(remaining)))
        else:
            eta = "Calculating..."
        
        # Calculate averages
        avg_checks = self.stats['checked_paths'] / elapsed if elapsed > 0 else 0
        avg_urls = self.stats['checked_urls'] / elapsed if elapsed > 0 else 0
        
        crack_id = self.crack_manager.get_current_id()
        
        output = f"""
Crack (#{crack_id}) stats:
⚙️ Last Update: {current_time}
⚙️ Timeout: {self.stats['timeout']}
⚙️ Threads: {self.stats['threads']}
⚙️ Status: {self.stats['status']}

ℹ️ Hits: {self.stats['hits']}
ℹ️ Checked Paths: {self.stats['checked_paths']:,}
ℹ️ Checked URLs: {self.stats['checked_urls']:,}
ℹ️ Invalid URLs: {self.stats['invalid_urls']:,}
ℹ️ Total URLs: {self.stats['checked_urls'] + self.stats['invalid_urls']:,}/{self.stats['max_urls']:,}

🐳 Docker Infected: {self.stats['docker_infected']}
☸️ K8s Pods Infected: {self.stats['k8s_infected']}

⏱️ Progression: {progress:.2f}%
⏱️ ETA: {eta}

📊 AVG Checks/sec: {avg_checks:.0f}
📊 AVG URL/sec: {avg_urls:.0f}
        """
        
        if self.stats['current_target']:
            output += f"\n🎯 Current Target: {self.stats['current_target']}"
        if self.stats['current_file']:
            output += f"\n📄 Current File: {self.stats['current_file']}"
        
        return output