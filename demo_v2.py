#!/usr/bin/env python3
"""
SpaceCracker V2 - Demo Script
Demonstrates the new real-time statistics and validation features
"""

import asyncio
import time
from spacecracker.core.stats_manager import StatsManager


async def demo_stats_display():
    """Demonstrate the real-time statistics display"""
    print("SpaceCracker V2 - Real-time Statistics Demo")
    print("=" * 50)
    
    # Create stats manager
    stats = StatsManager(total_targets=250000)
    
    # Start the display
    stats.start_display()
    
    try:
        # Simulate a scan
        for i in range(20):
            # Simulate processing URLs
            stats.update_stats(
                checked_urls=100 + i * 50,
                checked_paths=500 + i * 200,
                invalid_urls=5 + i * 2,
                current_target=f"https://target-{i+1}.example.com"
            )
            
            # Simulate finding hits occasionally
            if i % 5 == 0 and i > 0:
                stats.update_stats(hits=1)
                
                # Simulate different services
                service = ['sendgrid', 'aws_ses', 'mailgun'][i // 5 % 3]
                stats.update_stats(findings_by_service={service: 1})
            
            await asyncio.sleep(2)  # Wait 2 seconds between updates
    
    finally:
        # Stop the display
        stats.stop_display()


def demo_hit_reporting():
    """Demonstrate the hit reporting format"""
    print("\nSpaceCracker V2 - Hit Reporting Demo")
    print("=" * 50)
    
    stats = StatsManager()
    
    # Demo AWS SES hit
    aws_finding = {
        'service': 'aws_ses',
        'access_key': 'AKIASMHEJEMATZ34OPUM',
        'secret_key': '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',
        'url': 'http://185.229.202.85/wp-config.php.save',
        'response_time': 0.234,
        'validation': {
            'valid': True,
            'access_level': 'Full SES + SNS',
            'regions': [
                {
                    'name': 'EU-WEST-1',
                    'status': 'HEALTHY',
                    'daily_quota': 50000,
                    'sent_today': 1247,
                    'max_send_rate': 14,
                    'verified_emails': ['admin@example.com', 'noreply@test.org'],
                    'verified_domains': ['example.com', 'test.org'],
                    'sns_topics': 3
                },
                {
                    'name': 'US-EAST-1',
                    'status': 'HEALTHY',
                    'daily_quota': 100000,
                    'sent_today': 523,
                    'max_send_rate': 28,
                    'verified_emails': ['support@company.com'],
                    'verified_domains': ['company.com'],
                    'sns_topics': 0
                }
            ]
        }
    }
    
    print(stats.format_hit_report(aws_finding))
    
    # Demo SendGrid hit
    sendgrid_finding = {
        'service': 'sendgrid',
        'api_key': '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',
        'url': 'GGB:company/backend:repo:config/.env',
        'response_time': 0.456,
        'validation': {
            'valid': True,
            'plan': 'Pro Account',
            'credits': 75000,
            'rate_limit': '3000',
            'reputation': '98.5',
            'verified_senders': ['admin@example.com', 'noreply@test.org'],
            'templates': 8,
            'webhooks': 2,
            'monthly_sends': 45231,
            'monthly_limit': 100000
        }
    }
    
    print(stats.format_hit_report(sendgrid_finding))


if __name__ == "__main__":
    print("Starting SpaceCracker V2 Demo...")
    
    # Demo hit reporting first
    demo_hit_reporting()
    
    # Demo real-time stats
    try:
        asyncio.run(demo_stats_display())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    
    print("\nDemo completed!")