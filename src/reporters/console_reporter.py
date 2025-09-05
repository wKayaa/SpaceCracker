from typing import Dict, List
import json
from datetime import datetime

class ConsoleReporter:
    """Console output reporter with beautiful formatting"""
    
    def __init__(self):
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def print_hit(self, hit_data: Dict):
        """Print formatted hit to console"""
        service = hit_data.get('service', 'Unknown')
        
        if service == 'aws':
            self.print_aws_hit(hit_data)
        elif service == 'sendgrid':
            self.print_sendgrid_hit(hit_data)
        elif service == 'smtp':
            self.print_smtp_hit(hit_data)
        else:
            self.print_generic_hit(hit_data)
    
    def print_aws_hit(self, data: Dict):
        """Print AWS hit with formatted output"""
        validation = data.get('validation', {})
        credentials = data.get('credentials', {})
        
        print(f"\n{self.colors['green']}{self.colors['bold']}✨ New AWS Hit (#{data.get('crack_id', 'N/A')}){self.colors['end']}")
        print(f"")
        print(f"👉 {self.colors['cyan']}USER:{self.colors['end']} {credentials.get('access_key', 'N/A')}")
        print(f"👉 {self.colors['cyan']}PASS:{self.colors['end']} {credentials.get('secret_key', 'N/A')}")
        print(f"🔐 {self.colors['yellow']}ACCESS LEVEL:{self.colors['end']} {validation.get('access_level', 'Unknown')}")
        print(f"")
        print(f"📊 {self.colors['purple']}{len(validation.get('regions', {}))} regions with access{self.colors['end']}")
        
        for region, region_data in validation.get('regions', {}).items():
            print(f"")
            print(f"🌍 {self.colors['bold']}{region.upper()}:{self.colors['end']}")
            print(f"🤞 STATUS - {region_data.get('status', 'Unknown')}")
            print(f"📈 QUOTA - ({region_data.get('quota_max', 0)} per day - {region_data.get('quota_used', 0)} sent today - {region_data.get('send_rate', 0)} mail/s)")
            print(f"✅ VERIFIED EMAILS: {', '.join(region_data.get('verified_emails', [])[:3])}")
            print(f"📧 VERIFIED DOMAINS: {', '.join(region_data.get('verified_domains', []))}")
        
        print(f"")
        print(f"🚀 {self.colors['green']}HIT WORKS:{self.colors['end']} {'Yes' if validation.get('valid') else 'No'}")
        print(f"ℹ️ {self.colors['blue']}URL{self.colors['end']} - {data.get('url', 'N/A')}")
        print(f"🆔 {self.colors['yellow']}Crack ID{self.colors['end']} - #{data.get('crack_id', 'N/A')}")
        print(f"")
        print(f"✨ {self.colors['cyan']}SpaceCracker.co - @SpaceCracker{self.colors['end']}")
        print("=" * 80)
    
    def print_sendgrid_hit(self, data: Dict):
        """Print SendGrid hit"""
        credentials = data.get('credentials', {})
        
        print(f"\n{self.colors['green']}{self.colors['bold']}✨ New SendGrid Hit (#{data.get('crack_id', 'N/A')}){self.colors['end']}")
        print(f"")
        print(f"🔑 {self.colors['cyan']}API KEY:{self.colors['end']} {credentials.get('api_key', 'N/A')}")
        print(f"🚀 {self.colors['green']}HIT WORKS:{self.colors['end']} {'Yes' if data.get('validation', {}).get('valid') else 'No'}")
        print(f"ℹ️ {self.colors['blue']}URL{self.colors['end']} - {data.get('url', 'N/A')}")
        print(f"")
        print(f"✨ {self.colors['cyan']}SpaceCracker.co - @SpaceCracker{self.colors['end']}")
        print("=" * 80)
    
    def print_smtp_hit(self, data: Dict):
        """Print SMTP hit"""
        credentials = data.get('credentials', {})
        
        print(f"\n{self.colors['green']}{self.colors['bold']}✨ New SMTP Hit (#{data.get('crack_id', 'N/A')}){self.colors['end']}")
        print(f"")
        print(f"📧 {self.colors['cyan']}EMAIL:{self.colors['end']} {credentials.get('email', 'N/A')}")
        print(f"🔐 {self.colors['cyan']}PASSWORD:{self.colors['end']} {credentials.get('password', 'N/A')}")
        print(f"🌐 {self.colors['cyan']}HOST:{self.colors['end']} {credentials.get('host', 'N/A')}")
        print(f"🔌 {self.colors['cyan']}PORT:{self.colors['end']} {credentials.get('port', 'N/A')}")
        print(f"🚀 {self.colors['green']}HIT WORKS:{self.colors['end']} {'Yes' if data.get('validation', {}).get('valid') else 'No'}")
        print(f"ℹ️ {self.colors['blue']}URL{self.colors['end']} - {data.get('url', 'N/A')}")
        print(f"")
        print(f"✨ {self.colors['cyan']}SpaceCracker.co - @SpaceCracker{self.colors['end']}")
        print("=" * 80)
    
    def print_generic_hit(self, data: Dict):
        """Print generic hit"""
        print(f"\n{self.colors['green']}{self.colors['bold']}✨ New Hit (#{data.get('crack_id', 'N/A')}){self.colors['end']}")
        print(f"{json.dumps(data, indent=2)}")
        print("=" * 80)