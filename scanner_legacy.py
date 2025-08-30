#!/usr/bin/env python3
"""
SpaceCracker - Advanced Web Vulnerability Scanner
Mass scanning tool with multiple exploit modules and secret extraction capabilities
"""

import asyncio
import json
import argparse
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from modules.scanner_base import SpaceCracker
from utils.reporting import Reporter
from utils.telegram_bot import TelegramBot
import logging

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('spacecracker.log'),
            logging.StreamHandler()
        ]
    )

def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return None

def load_targets(target_file):
    """Load target URLs/IPs from file"""
    targets = []
    try:
        with open(target_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if not line.startswith(('http://', 'https://')):
                        line = f'http://{line}'
                    targets.append(line)
        return targets
    except Exception as e:
        logging.error(f"Failed to load targets from {target_file}: {e}")
        return []

async def main():
    parser = argparse.ArgumentParser(description='SpaceCracker - Advanced Web Vulnerability Scanner')
    parser.add_argument('-t', '--targets', required=True, help='File containing target URLs/IPs')
    parser.add_argument('-p', '--paths', help='File containing paths to test (optional)')
    parser.add_argument('-c', '--config', default='config.json', help='Configuration file')
    parser.add_argument('--threads', type=int, help='Number of threads')
    parser.add_argument('--rate-limit', type=float, help='Requests per second')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--modules', nargs='+', choices=['ggb', 'js', 'git', 'cve', 'paths'], 
                       help='Specific modules to run')
    parser.add_argument('--telegram', action='store_true', help='Enable Telegram notifications')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    # Override config with command line arguments
    if args.threads:
        config['scanner']['threads'] = args.threads
    if args.rate_limit:
        config['scanner']['rate_limit'] = args.rate_limit
    if args.telegram:
        config['telegram']['enabled'] = True
    if args.modules:
        # Disable all modules first
        for module in config['modules']:
            config['modules'][module] = False
        # Enable specified modules
        module_map = {
            'ggb': 'ggb_scanner',
            'js': 'js_scanner', 
            'git': 'git_scanner',
            'cve': 'cve_exploits',
            'paths': 'path_scanner'
        }
        for module in args.modules:
            if module in module_map:
                config['modules'][module_map[module]] = True
    
    # Load targets
    targets = load_targets(args.targets)
    if not targets:
        logger.error("No valid targets loaded. Exiting.")
        return
    
    logger.info(f"Loaded {len(targets)} targets")
    
    # Initialize scanner
    scanner = SpaceCracker(config)
    
    # Load custom paths if provided
    if args.paths:
        scanner.load_custom_paths(args.paths)
    
    # Setup output directory
    output_dir = args.output or "results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize reporter
    reporter = Reporter(output_dir)
    
    # Initialize Telegram bot if enabled
    telegram_bot = None
    if config['telegram']['enabled'] and config['telegram']['bot_token']:
        telegram_bot = TelegramBot(
            token=config['telegram']['bot_token'],
            chat_id=config['telegram']['chat_id']
        )
    
    logger.info("Starting SpaceCracker scan...")
    
    try:
        # Run the scan
        results = await scanner.scan_targets(targets)
        
        # Generate reports
        reporter.generate_reports(results)
        
        # Send Telegram notifications for valid results only
        if telegram_bot and results:
            valid_results = [r for r in results if r.get('validated', False)]
            if valid_results:
                await telegram_bot.send_results(valid_results)
        
        logger.info(f"Scan completed. Found {len(results)} results.")
        logger.info(f"Reports saved to {output_dir}")
        
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)