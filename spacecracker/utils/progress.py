#!/usr/bin/env python3
"""
Enhanced Progress Display Module
High-performance real-time UI with statistics for SpaceCracker v3.1
"""

import time
import threading
from typing import Dict, Any, List
from .performance import get_performance_manager
from .language import _

class ProgressDisplay:
    """Enhanced progress display with real-time statistics"""
    
    def __init__(self, total_targets: int = 0, language: str = 'en'):
        self.total_targets = total_targets
        self.language = language
        self.stats = {
            'urls_processed': 0,
            'unique_urls': 0,
            'urls_validated': 0,
            'total_findings': 0,
            'findings_by_service': {},
            'start_time': time.time(),
            'current_target': '',
            'current_file': ''
        }
        self.refresh_rate = 2.0  # 2 seconds (improved from 4fps to 0.5fps as mentioned in requirements)
        self.display_thread = None
        self.display_active = False
        self.stats_lock = threading.Lock()
        
    def start_display(self):
        """Start the enhanced progress display"""
        if self.display_active:
            return
            
        self.display_active = True
        self.stats['start_time'] = time.time()
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
    def stop_display(self):
        """Stop the progress display"""
        self.display_active = False
        if self.display_thread:
            self.display_thread.join(timeout=3)
            
    def update_stats(self, **kwargs):
        """Update progress statistics"""
        with self.stats_lock:
            for key, value in kwargs.items():
                if key in self.stats:
                    if key in ['urls_processed', 'unique_urls', 'urls_validated', 'total_findings']:
                        if isinstance(value, int):
                            self.stats[key] += value  # Increment counters
                        else:
                            self.stats[key] = value  # Direct assignment
                    elif key == 'findings_by_service':
                        # Merge findings by service
                        for service, count in value.items():
                            self.stats['findings_by_service'][service] = self.stats['findings_by_service'].get(service, 0) + count
                    else:
                        self.stats[key] = value
                        
    def _display_loop(self):
        """Main display loop"""
        while self.display_active:
            try:
                self._render_display()
                time.sleep(self.refresh_rate)
            except Exception:
                pass  # Continue displaying even if there are errors
                
    def _render_display(self):
        """Render the enhanced progress display"""
        with self.stats_lock:
            current_stats = self.stats.copy()
        
        # Get performance stats
        perf_manager = get_performance_manager()
        perf_stats = perf_manager.get_stats()
        
        # Calculate progress
        progress_pct = 0.0
        if self.total_targets > 0:
            progress_pct = (current_stats['urls_processed'] / self.total_targets) * 100
            progress_pct = min(100.0, progress_pct)
        
        # Calculate elapsed time
        elapsed = time.time() - current_stats['start_time']
        elapsed_str = self._format_time(elapsed)
        
        # Calculate success rate
        success_rate = 0.0
        if current_stats['urls_processed'] > 0:
            success_rate = (current_stats['urls_validated'] / current_stats['urls_processed']) * 100
        
        # Clear screen and render display
        print("\033[2J\033[H", end="")  # Clear screen and move cursor to top
        
        # Header
        print("🔍 EVYL SCANNER V3.1 - " + _('scan_progress').upper() + " 🔍")
        print()
        
        # Current file info
        if current_stats.get('current_file'):
            print(f"📁 File: {current_stats['current_file']}")
        
        # Progress info
        print(f"⏱️ " + _('elapsed_time') + f": {elapsed_str}")
        print(f"📊 " + _('progress') + f": {self._render_progress_bar(progress_pct)} {progress_pct:.1f}%")
        print()
        
        # Statistics
        print("📈 " + _('total_stats') + ":")
        print(f"🌐 " + _('urls_processed') + f": {current_stats['urls_processed']:,}")
        print(f"🎯 " + _('unique_urls') + f": {current_stats['unique_urls']:,}")
        print(f"✅ " + _('urls_validated') + f": {current_stats['urls_validated']:,}")
        print(f"📉 " + _('success_rate') + f": {success_rate:.1f}%")
        print()
        
        # Findings by service
        total_findings = sum(current_stats['findings_by_service'].values())
        if total_findings > 0:
            print("🏆 " + _('hits_found').format(total_findings) + ":")
            findings_display = []
            for service, count in sorted(current_stats['findings_by_service'].items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    findings_display.append(f"✅ {service.title()}: {count}")
            
            # Display findings in rows of 4
            for i in range(0, len(findings_display), 4):
                row = findings_display[i:i+4]
                print("  " + "  ".join(row))
            print()
        
        # System performance
        cpu_usage = perf_stats.get('cpu_usage', 0)
        memory_usage = perf_stats.get('memory_usage', 0)
        http_rate = self._calculate_http_rate(current_stats, elapsed)
        current_time = time.strftime("%H:%M:%S")
        
        print(f"💻 " + _('cpu_usage') + f": {cpu_usage:.1f}% | " + 
              f"🧠 " + _('ram_usage') + f": {memory_usage:.1f} MB | " + 
              f"📡 " + _('http_rate') + f": {http_rate}/s | " + 
              f"⏰ {current_time}")
        print()
        
    def _render_progress_bar(self, percentage: float, width: int = 40) -> str:
        """Render a progress bar"""
        filled_width = int((percentage / 100.0) * width)
        bar = "█" * filled_width + "░" * (width - filled_width)
        return f"[{bar}]"
        
    def _format_time(self, seconds: float) -> str:
        """Format elapsed time"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes:02d}m {secs:02d}s"
        elif minutes > 0:
            return f"{minutes:02d}m {secs:02d}s"
        else:
            return f"{secs}s"
            
    def _calculate_http_rate(self, stats: Dict, elapsed: float) -> int:
        """Calculate HTTP requests per second"""
        if elapsed > 0:
            return int(stats['urls_processed'] / elapsed)
        return 0
        
    def show_final_summary(self):
        """Show final scan summary"""
        with self.stats_lock:
            current_stats = self.stats.copy()
        
        elapsed = time.time() - current_stats['start_time']
        elapsed_str = self._format_time(elapsed)
        
        print("\n" + "="*60)
        print("🏁 " + _('scan_completed').upper())
        print("="*60)
        print(f"⏱️ " + _('elapsed_time') + f": {elapsed_str}")
        print(f"🌐 " + _('urls_processed') + f": {current_stats['urls_processed']:,}")
        print(f"🎯 Total " + _('findings') + f": {current_stats['total_findings']:,}")
        
        if current_stats['findings_by_service']:
            print(f"\n🏆 " + _('findings') + " by Service:")
            for service, count in sorted(current_stats['findings_by_service'].items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  ✅ {service.title()}: {count}")
        
        # Performance summary
        avg_rate = int(current_stats['urls_processed'] / elapsed) if elapsed > 0 else 0
        print(f"\n📊 Performance:")
        print(f"  📡 Average rate: {avg_rate} URLs/second")
        print(f"  🧠 Peak memory: {get_performance_manager().get_memory_usage_mb():.1f} MB")
        print("="*60)

class CompactProgressDisplay:
    """Compact progress display for streamlined hits visibility"""
    
    def __init__(self, total_targets: int = 0):
        self.total_targets = total_targets
        self.processed = 0
        self.findings = 0
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = 1.0  # Update every second for compact display
        
    def update(self, processed: int = 1, findings: int = 0):
        """Update compact progress"""
        self.processed += processed
        self.findings += findings
        
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._render_compact()
            self.last_update = current_time
            
    def _render_compact(self):
        """Render compact progress line"""
        elapsed = time.time() - self.start_time
        rate = int(self.processed / elapsed) if elapsed > 0 else 0
        progress = (self.processed / max(self.total_targets, 1)) * 100
        
        print(f"\r🔍 {self.processed:,}/{self.total_targets:,} ({progress:.1f}%) | " +
              f"🏆 {self.findings} hits | 📡 {rate}/s", end="", flush=True)
        
    def finish(self):
        """Finish compact display"""
        print()  # New line after final update