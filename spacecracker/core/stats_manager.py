#!/usr/bin/env python3
"""
SpaceCracker V2 - Real-time Statistics Manager
Advanced statistics tracking with real-time display and crack ID generation
"""

import time
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ScanStats:
    """Comprehensive scan statistics"""
    hits: int = 0
    checked_paths: int = 0
    checked_urls: int = 0
    invalid_urls: int = 0
    total_urls: int = 0
    max_urls: int = 250000
    start_time: float = field(default_factory=time.time)
    current_target: str = ""
    current_file: str = ""
    findings_by_service: Dict[str, int] = field(default_factory=dict)
    threads: int = 5000
    timeout: int = 20
    status: str = "running"


class CrackManager:
    """Generates unique crack IDs for tracking findings"""
    
    def __init__(self):
        self._counter = 1
        self._lock = threading.Lock()
        
    def generate_crack_id(self) -> str:
        """Generate unique crack ID in format #2025090501"""
        with self._lock:
            now = datetime.now()
            # Format: #YYYYMMDDHH + incremental counter (2 digits)
            date_part = now.strftime("%Y%m%d%H")
            crack_id = f"#{date_part}{self._counter:02d}"
            self._counter += 1
            if self._counter > 99:
                self._counter = 1
            return crack_id


class StatsManager:
    """Real-time statistics manager with live display"""
    
    def __init__(self, total_targets: int = 0, language: str = 'en'):
        self.stats = ScanStats(total_urls=total_targets)
        self.crack_manager = CrackManager()
        self.language = language
        self._display_active = False
        self._display_thread: Optional[threading.Thread] = None
        self._stats_lock = threading.Lock()
        self._refresh_rate = 2.0  # 2 seconds refresh rate
        
    def start_display(self):
        """Start real-time statistics display"""
        if not self._display_active:
            self._display_active = True
            self._display_thread = threading.Thread(target=self._display_loop, daemon=True)
            self._display_thread.start()
    
    def stop_display(self):
        """Stop real-time statistics display"""
        self._display_active = False
        if self._display_thread:
            self._display_thread.join(timeout=3)
    
    def update_stats(self, **kwargs):
        """Update statistics with new values"""
        with self._stats_lock:
            for key, value in kwargs.items():
                if hasattr(self.stats, key):
                    if key in ['hits', 'checked_paths', 'checked_urls', 'invalid_urls']:
                        # Increment counters
                        current_value = getattr(self.stats, key)
                        setattr(self.stats, key, current_value + value)
                    elif key == 'findings_by_service':
                        # Merge findings by service
                        for service, count in value.items():
                            current_count = self.stats.findings_by_service.get(service, 0)
                            self.stats.findings_by_service[service] = current_count + count
                    else:
                        setattr(self.stats, key, value)
    
    def get_crack_id(self) -> str:
        """Generate new crack ID for a finding"""
        return self.crack_manager.generate_crack_id()
    
    def get_stats_copy(self) -> ScanStats:
        """Get thread-safe copy of current statistics"""
        with self._stats_lock:
            # Create a deep copy of the stats
            stats_copy = ScanStats(
                hits=self.stats.hits,
                checked_paths=self.stats.checked_paths,
                checked_urls=self.stats.checked_urls,
                invalid_urls=self.stats.invalid_urls,
                total_urls=self.stats.total_urls,
                max_urls=self.stats.max_urls,
                start_time=self.stats.start_time,
                current_target=self.stats.current_target,
                current_file=self.stats.current_file,
                findings_by_service=self.stats.findings_by_service.copy(),
                threads=self.stats.threads,
                timeout=self.stats.timeout,
                status=self.stats.status
            )
            return stats_copy
    
    def _display_loop(self):
        """Main display loop for real-time statistics"""
        while self._display_active:
            try:
                self._print_stats()
                time.sleep(self._refresh_rate)
            except Exception as e:
                # Don't let display errors crash the scan
                continue
    
    def _print_stats(self):
        """Print formatted statistics to console"""
        stats = self.get_stats_copy()
        elapsed = time.time() - stats.start_time
        
        # Calculate rates
        paths_per_sec = int(stats.checked_paths / elapsed) if elapsed > 0 else 0
        urls_per_sec = int(stats.checked_urls / elapsed) if elapsed > 0 else 0
        total_urls_per_sec = int((stats.checked_urls + stats.invalid_urls) / elapsed) if elapsed > 0 else 0
        
        # Calculate progress and ETA
        progress_percent = (stats.checked_urls / stats.max_urls * 100) if stats.max_urls > 0 else 0
        remaining_urls = max(0, stats.max_urls - stats.checked_urls)
        eta_seconds = (remaining_urls / urls_per_sec) if urls_per_sec > 0 else 0
        eta = str(timedelta(seconds=int(eta_seconds)))
        
        # Get current crack ID for display
        current_crack = self.crack_manager.generate_crack_id()
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Clear screen and print stats
        print("\033[2J\033[H", end="")  # Clear screen and move cursor to top
        
        print(f"Crack ({current_crack}) stats:")
        print(f"⚙️ Last Update: {last_update}")
        print(f"⚙️ Timeout: {stats.timeout}")
        print(f"⚙️ Threads: {stats.threads}")
        print(f"⚙️ Status: {stats.status}")
        print()
        print(f"ℹ️ Hits: {stats.hits}")
        print(f"ℹ️ Checked Paths: {stats.checked_paths:,}")
        print(f"ℹ️ Checked URLs: {stats.checked_urls:,}")
        print(f"ℹ️ Invalid URLs: {stats.invalid_urls:,}")
        print(f"ℹ️ Total URLs: {stats.checked_urls + stats.invalid_urls:,}/{stats.max_urls:,}")
        print()
        print(f"⏱️ Progression: {progress_percent:.2f}%")
        print(f"⏱️ ETA: {eta}")
        print()
        print(f"📊 AVG Checks/sec: {paths_per_sec:,}")
        print(f"📊 AVG URL/sec: {urls_per_sec}")
        print(f"📊 AVG Total URL/sec: {total_urls_per_sec}")
        
        if stats.current_target:
            print(f"\n🎯 Current Target: {stats.current_target}")
        if stats.current_file:
            print(f"📄 Current File: {stats.current_file}")
        
        if stats.findings_by_service:
            print(f"\n🔍 Findings by Service:")
            for service, count in stats.findings_by_service.items():
                print(f"   {service}: {count}")
    
    def format_hit_report(self, finding: Dict[str, Any]) -> str:
        """Format a detailed hit report with the requested format"""
        crack_id = self.get_crack_id()
        
        if finding.get('service') == 'aws_ses':
            return self._format_aws_ses_hit(finding, crack_id)
        elif finding.get('service') == 'sendgrid':
            return self._format_sendgrid_hit(finding, crack_id)
        elif finding.get('service') == 'mailjet':
            return self._format_mailjet_hit(finding, crack_id)
        else:
            return self._format_generic_hit(finding, crack_id)
    
    def _format_aws_ses_hit(self, finding: Dict[str, Any], crack_id: str) -> str:
        """Format AWS SES hit with full quota access details"""
        validation = finding.get('validation', {})
        
        report = f"""✨ New Hit ({crack_id})

👉 USER: {finding.get('access_key', 'N/A')}
👉 PASS: {finding.get('secret_key', 'N/A')}
🔐 ACCESS LEVEL: {validation.get('access_level', 'Unknown')}

📊 VALIDATION METHOD:
- boto3.client('ses').get_send_quota()
- boto3.client('ses').list_verified_email_addresses()
- boto3.client('sns').list_topics()

📊 {len(validation.get('regions', []))} regions with production quota"""

        for region in validation.get('regions', []):
            report += f"""

🌍 {region.get('name', 'UNKNOWN')}:
🤞 STATUS - {region.get('status', 'UNKNOWN')}
📈 QUOTA - ({region.get('daily_quota', 0)} per day - {region.get('sent_today', 0)} sent today - {region.get('max_send_rate', 0)} mail/s)"""
            
            if region.get('verified_emails'):
                report += f"\n✅ VERIFIED EMAILS: {', '.join(region.get('verified_emails', []))}"
            if region.get('verified_domains'):
                report += f"\n📧 VERIFIED DOMAINS: {', '.join(region.get('verified_domains', []))}"
            if region.get('sns_topics', 0) > 0:
                report += f"\n🔔 SNS TOPICS: {region.get('sns_topics', 0)} active"

        report += f"""

🚀 HIT WORKS: {validation.get('valid', 'Unknown')}
ℹ️ URL - {finding.get('url', 'N/A')}
⏱️ Response Time: {finding.get('response_time', 0):.3f}s
🆔 Crack ID - {crack_id}

✨ SpaceCracker.co - @SpaceCracker"""
        
        return report
    
    def _format_sendgrid_hit(self, finding: Dict[str, Any], crack_id: str) -> str:
        """Format SendGrid hit with account details"""
        validation = finding.get('validation', {})
        
        report = f"""✨ New Hit ({crack_id})

🔑 KEY: {finding.get('api_key', 'N/A')}
📊 PLAN: {validation.get('plan', 'Unknown')}
💳 Credits: {validation.get('credits', 'Unknown')} remaining
📈 Rate Limit: {validation.get('rate_limit', 'Unknown')}/hour
📊 Reputation: {validation.get('reputation', 'Unknown')}%
✅ Verified Senders: {', '.join(validation.get('verified_senders', []))}
📧 Templates: {validation.get('templates', 0)} active
🔥 Webhooks: {validation.get('webhooks', 0)} configured
📅 Monthly Sends: {validation.get('monthly_sends', 0)}/{validation.get('monthly_limit', 0)}

🚀 HIT WORKS: {validation.get('valid', 'Unknown')}
ℹ️ URL - {finding.get('url', 'N/A')}
⏱️ Response Time: {finding.get('response_time', 0):.3f}s
🆔 Crack ID - {crack_id}

✨ SpaceCracker.co - @SpaceCracker"""
        
        return report
    
    def _format_mailjet_hit(self, finding: Dict[str, Any], crack_id: str) -> str:
        """Format Mailjet hit with quota details"""
        validation = finding.get('validation', {})
        
        report = f"""✨ New Hit ({crack_id})

🔑 API KEY: {finding.get('api_key', 'N/A')}
🔒 SECRET: {finding.get('api_secret', 'N/A')}
📊 QUOTA LEVEL: {validation.get('quota', 'Unknown')}
📈 SENT TODAY: {validation.get('sent_today', 0)}
📧 VERIFIED DOMAINS: {', '.join(validation.get('domains', []))}

🚀 HIT WORKS: {validation.get('valid', 'Unknown')}
ℹ️ URL - {finding.get('url', 'N/A')}
⏱️ Response Time: {finding.get('response_time', 0):.3f}s
🆔 Crack ID - {crack_id}

✨ SpaceCracker.co - @SpaceCracker"""
        
        return report
    
    def _format_generic_hit(self, finding: Dict[str, Any], crack_id: str) -> str:
        """Format generic hit report"""
        report = f"""✨ New Hit ({crack_id})

🔑 TYPE: {finding.get('type', 'Unknown')}
💰 VALUE: {finding.get('value', 'N/A')}
📊 SERVICE: {finding.get('service', 'Generic')}

🚀 HIT WORKS: {finding.get('validation', {}).get('valid', 'Unknown')}
ℹ️ URL - {finding.get('url', 'N/A')}
⏱️ Response Time: {finding.get('response_time', 0):.3f}s
🆔 Crack ID - {crack_id}

✨ SpaceCracker.co - @SpaceCracker"""
        
        return report