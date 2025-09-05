#!/usr/bin/env python3
"""
SpaceCracker V2 - Enhanced CLI Interface
Advanced command-line interface with comprehensive scanning capabilities
"""

import argparse
import asyncio
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from spacecracker.core.runner import ScanRunner
from spacecracker.core.config import Config, load_config
from spacecracker.core.stats_manager import StatsManager
from spacecracker.validators.sendgrid_validator import SendGridValidator
from spacecracker.validators.aws_ses_validator import SESValidator


def create_parser():
    """Create the argument parser with all V2 features"""
    parser = argparse.ArgumentParser(
        description='SpaceCracker V2 - Ultimate Multi-Service Credential Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full scan with all exploits
  %(prog)s scan --targets urls.txt --threads 5000 --timeout 20 --exploits all --output results.json --telegram-notify

  # Scan specific service
  %(prog)s scan-service --service aws --input aws_targets.txt --check-quota --regions all

  # Test single credential
  %(prog)s test --type sendgrid --key "SG.xxxxx" --verbose

  # Run specific exploit
  %(prog)s exploit --type ggb --target "https://github.com/target/repo" --depth 5

  # Start web panel with authentication
  %(prog)s panel --port 8080 --host 0.0.0.0 --auth enabled --ssl-cert cert.pem
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Main scan command
    scan_parser = subparsers.add_parser('scan', help='Start comprehensive scan')
    scan_parser.add_argument('--targets', required=True, help='File containing target URLs/IPs')
    scan_parser.add_argument('--threads', type=int, default=5000, help='Number of threads (default: 5000)')
    scan_parser.add_argument('--timeout', type=int, default=20, help='Request timeout in seconds (default: 20)')
    scan_parser.add_argument('--exploits', choices=['all', 'ggb', 'git', 'js', 'cve', 'paths'], 
                           default='all', help='Exploits to run (default: all)')
    scan_parser.add_argument('--output', help='Output file (JSON format)')
    scan_parser.add_argument('--telegram-notify', action='store_true', help='Enable Telegram notifications')
    scan_parser.add_argument('--validate-secrets', action='store_true', default=True, help='Validate found secrets')
    scan_parser.add_argument('--show-stats', action='store_true', default=True, help='Show real-time statistics')
    
    # Service-specific scan
    service_parser = subparsers.add_parser('scan-service', help='Scan for specific service credentials')
    service_parser.add_argument('--service', required=True, 
                               choices=['aws', 'sendgrid', 'mailgun', 'mailjet', 'stripe', 'github'],
                               help='Service to scan for')
    service_parser.add_argument('--input', required=True, help='Input file with targets')
    service_parser.add_argument('--check-quota', action='store_true', help='Check service quotas and limits')
    service_parser.add_argument('--regions', choices=['all', 'us', 'eu', 'ap'], default='all', 
                               help='Regions to check for cloud services')
    
    # Test single credential
    test_parser = subparsers.add_parser('test', help='Test a single credential')
    test_parser.add_argument('--type', required=True, 
                            choices=['sendgrid', 'aws_ses', 'mailgun', 'mailjet', 'stripe', 'github'],
                            help='Credential type')
    test_parser.add_argument('--key', required=True, help='API key or access key')
    test_parser.add_argument('--secret', help='Secret key (for AWS, Mailjet, etc.)')
    test_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # Exploit-specific command
    exploit_parser = subparsers.add_parser('exploit', help='Run specific exploit')
    exploit_parser.add_argument('--type', required=True, 
                               choices=['ggb', 'git', 'js', 'cve', 'k8s'],
                               help='Exploit type')
    exploit_parser.add_argument('--target', required=True, help='Target URL or repository')
    exploit_parser.add_argument('--depth', type=int, default=5, help='Scanning depth (default: 5)')
    exploit_parser.add_argument('--output', help='Output file for results')
    
    # Web panel command
    panel_parser = subparsers.add_parser('panel', help='Start web panel')
    panel_parser.add_argument('--port', type=int, default=8080, help='Port to run on (default: 8080)')
    panel_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    panel_parser.add_argument('--auth', choices=['enabled', 'disabled'], default='disabled',
                             help='Enable authentication (default: disabled)')
    panel_parser.add_argument('--ssl-cert', help='SSL certificate file')
    panel_parser.add_argument('--ssl-key', help='SSL private key file')
    
    # Stats display command
    stats_parser = subparsers.add_parser('stats', help='Show real-time statistics demo')
    stats_parser.add_argument('--demo', action='store_true', help='Run statistics demo')
    
    return parser


async def cmd_scan(args):
    """Execute scan command"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              SpaceCracker V2 - Starting Scan             ║
╠══════════════════════════════════════════════════════════╣
║  Targets: {args.targets:<45} ║
║  Threads: {args.threads:<45} ║
║  Timeout: {args.timeout:<45} ║
║  Exploits: {args.exploits:<44} ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Load targets
    if not os.path.exists(args.targets):
        print(f"❌ Target file not found: {args.targets}")
        return
    
    with open(args.targets, 'r') as f:
        targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not targets:
        print("❌ No valid targets found in file")
        return
    
    print(f"📂 Loaded {len(targets)} targets")
    
    # Load configuration
    config = load_config()
    config.threads = args.threads
    
    # Initialize and run scanner
    runner = ScanRunner(config)
    results = runner.run_scan(targets, show_stats=args.show_stats)
    
    # Save results if output specified
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to {args.output}")
    
    # Print summary
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                    Scan Complete                         ║
╠══════════════════════════════════════════════════════════╣
║  Total Findings: {len(results.get('findings', [])):<40} ║
║  Errors: {len(results.get('errors', [])):<47} ║
║  Duration: {results.get('metadata', {}).get('finished_at', 'Unknown'):<44} ║
╚══════════════════════════════════════════════════════════╝
    """)


async def cmd_test(args):
    """Execute test command"""
    print(f"🔬 Testing {args.type} credential...")
    
    if args.type == 'sendgrid':
        validator = SendGridValidator()
        result = await validator.validate(args.key)
    elif args.type == 'aws_ses':
        if not args.secret:
            print("❌ AWS SES requires both --key and --secret")
            return
        validator = SESValidator()
        result = await validator.validate(args.key, args.secret)
    else:
        print(f"❌ Validator for {args.type} not implemented yet")
        return
    
    if result.get('valid'):
        print("✅ Credential is VALID!")
        if args.verbose:
            print(f"📊 Service: {result.get('service', 'Unknown')}")
            if args.type == 'sendgrid':
                print(f"📊 Plan: {result.get('plan', 'Unknown')}")
                print(f"💳 Credits: {result.get('credits', 'Unknown')}")
                print(f"📈 Rate Limit: {result.get('rate_limit', 'Unknown')}")
                print(f"📊 Reputation: {result.get('reputation', 'Unknown')}")
            elif args.type == 'aws_ses':
                print(f"🔐 Access Level: {result.get('access_level', 'Unknown')}")
                print(f"🌍 Regions: {result.get('total_regions', 0)}")
                print(f"🚀 Production Ready: {result.get('production_ready', False)}")
    else:
        print("❌ Credential is INVALID")
        if args.verbose and result.get('error'):
            print(f"❌ Error: {result['error']}")


async def cmd_stats(args):
    """Execute stats command"""
    if args.demo:
        print("📊 Starting SpaceCracker V2 Statistics Demo...")
        stats = StatsManager(total_targets=250000)
        stats.start_display()
        
        try:
            # Simulate scan progress
            for i in range(20):
                stats.update_stats(
                    checked_urls=100 + i * 50,
                    checked_paths=500 + i * 200,
                    invalid_urls=5 + i * 2,
                    current_target=f"https://target-{i+1}.example.com"
                )
                
                if i % 5 == 0 and i > 0:
                    stats.update_stats(hits=1)
                    service = ['sendgrid', 'aws_ses', 'mailgun'][i // 5 % 3]
                    stats.update_stats(findings_by_service={service: 1})
                
                await asyncio.sleep(2)
        finally:
            stats.stop_display()
    else:
        print("📊 Use --demo to run statistics demonstration")


async def cmd_panel(args):
    """Execute panel command"""
    import subprocess
    import sys
    
    cmd = [
        sys.executable, 'panel.py',
        '--host', args.host,
        '--port', str(args.port),
        '--auth', args.auth
    ]
    
    if args.ssl_cert:
        cmd.extend(['--ssl-cert', args.ssl_cert])
    if args.ssl_key:
        cmd.extend(['--ssl-key', args.ssl_key])
    
    print(f"🚀 Starting web panel...")
    subprocess.run(cmd)


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # ASCII art banner
    print("""
    ███████╗██████╗  █████╗  ██████╗███████╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
    ███████╗██████╗  █████╗  ██████╗███████╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
    ╚══████║██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
       ███║██████╔╝███████║██║     █████╗  ██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
      ███║ ██╔═══╝ ██╔══██║██║     ██╔══╝  ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
     ██████║██║     ██║  ██║╚██████╗███████╗╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
     ╚═════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
     
                               🚀 SpaceCracker V2 - Ultimate Credential Scanner 🚀
                                       Professional Security Framework
    """)
    
    # Execute command
    try:
        if args.command == 'scan':
            asyncio.run(cmd_scan(args))
        elif args.command == 'scan-service':
            print(f"🔍 Service-specific scanning for {args.service} not fully implemented yet")
        elif args.command == 'test':
            asyncio.run(cmd_test(args))
        elif args.command == 'exploit':
            print(f"💥 Exploit-specific scanning for {args.type} not fully implemented yet")
        elif args.command == 'panel':
            asyncio.run(cmd_panel(args))
        elif args.command == 'stats':
            asyncio.run(cmd_stats(args))
    except KeyboardInterrupt:
        print("\n🛑 Scan interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()