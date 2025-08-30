import argparse
import sys
import os
from typing import List
from .version import __version__
from .core import config as cfg
from .core.registry import ModuleRegistry
from .core.runner import ScanRunner
from .core.reporting import ReportWriter

def interactive_wizard() -> tuple:
    """Run interactive wizard to collect scan parameters"""
    print("\n🚀 SpaceCracker - Interactive Scan Wizard")
    print("=" * 50)
    
    # Authorization check
    print("\n⚠️  AUTHORIZATION DISCLAIMER")
    print("This tool should only be used on systems you own or have explicit permission to test.")
    consent = input("Do you have authorization to scan the target systems? [y/N]: ").lower()
    
    if consent != 'y':
        print("Authorization required. Exiting.")
        sys.exit(1)
    
    # Collect targets
    print("\n📋 Step 1: Target Configuration")
    target_input = input("Enter target file path or single target URL: ").strip()
    
    if os.path.isfile(target_input):
        with open(target_input, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"Loaded {len(targets)} targets from file")
    else:
        targets = [target_input]
        print(f"Single target: {target_input}")
    
    # Select modules
    print("\n🔧 Step 2: Module Selection")
    registry = ModuleRegistry()
    available_modules = registry.list_modules()
    
    print("Available modules:")
    for i, (module_id, info) in enumerate(available_modules.items(), 1):
        print(f"  {i}. {info['name']} - {info['description']}")
    
    print("\nSelect modules (enter numbers separated by commas, or 'all' for all modules):")
    module_choice = input("Choice: ").strip().lower()
    
    if module_choice == 'all':
        selected_modules = list(available_modules.keys())
    else:
        try:
            indices = [int(x.strip()) - 1 for x in module_choice.split(',')]
            module_list = list(available_modules.keys())
            selected_modules = [module_list[i] for i in indices if 0 <= i < len(module_list)]
        except:
            print("Invalid selection, using all modules")
            selected_modules = list(available_modules.keys())
    
    print(f"Selected modules: {', '.join(selected_modules)}")
    
    # Performance settings
    print("\n⚡ Step 3: Performance Settings")
    threads = input("Number of threads [50]: ").strip() or "50"
    rate_limit = input("Requests per second [10]: ").strip() or "10"
    
    try:
        threads = int(threads)
        rate_limit = int(rate_limit)
    except:
        threads = 50
        rate_limit = 10
    
    # Telegram settings
    print("\n📱 Step 4: Telegram Notifications")
    telegram_enabled = input("Enable Telegram notifications? [y/N]: ").lower() == 'y'
    
    # Confirm plan
    print("\n📊 Scan Plan Summary")
    print("-" * 30)
    print(f"Targets: {len(targets)}")
    print(f"Modules: {len(selected_modules)}")
    print(f"Threads: {threads}")
    print(f"Rate Limit: {rate_limit} req/s")
    print(f"Telegram: {'Enabled' if telegram_enabled else 'Disabled'}")
    
    confirm = input("\nProceed with scan? [Y/n]: ").lower()
    if confirm == 'n':
        print("Scan cancelled")
        sys.exit(0)
    
    return targets, selected_modules, threads, rate_limit, telegram_enabled

def load_targets_from_file(filename: str) -> List[str]:
    """Load targets from file"""
    targets = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if not line.startswith(('http://', 'https://')):
                        line = f'http://{line}'
                    targets.append(line)
    except Exception as e:
        print(f"Error loading targets from {filename}: {e}")
        sys.exit(1)
    
    return targets

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='SpaceCracker - Advanced Modular Web Exposure & Secret Discovery Toolkit'
    )
    
    parser.add_argument('-t', '--targets', help='Target file or single target URL')
    parser.add_argument('-m', '--modules', help='Comma-separated modules or "all"')
    parser.add_argument('-c', '--config', help='Config file path')
    parser.add_argument('-o', '--output-dir', help='Output directory', default='results')
    parser.add_argument('-f', '--formats', help='Output formats (json,txt,csv)', default='json,txt,csv')
    parser.add_argument('-T', '--threads', type=int, help='Number of threads', default=50)
    parser.add_argument('-r', '--rate-limit', type=int, help='Requests per second', default=10)
    parser.add_argument('-b', '--burst', type=int, help='Rate limit burst', default=20)
    parser.add_argument('-g', '--telegram', action='store_true', help='Enable Telegram notifications')
    parser.add_argument('-s', '--severity-filter', help='Minimum severity to report')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--list-modules', action='store_true', help='List available modules')
    parser.add_argument('--dry-run', action='store_true', help='Show scan plan without executing')
    parser.add_argument('--interactive', action='store_true', help='Force interactive wizard')
    parser.add_argument('--version', action='version', version=f'SpaceCracker {__version__}')
    
    args = parser.parse_args()
    
    # List modules and exit
    if args.list_modules:
        registry = ModuleRegistry()
        modules = registry.list_modules()
        print("\nAvailable modules:")
        for module_id, info in modules.items():
            print(f"  {module_id}: {info['name']} - {info['description']}")
        return 0
    
    # Determine mode: interactive wizard or CLI
    if not args.targets and not args.interactive:
        # No arguments provided, run interactive wizard
        targets, selected_modules, threads, rate_limit, telegram_enabled = interactive_wizard()
    elif args.interactive:
        # Force interactive mode
        targets, selected_modules, threads, rate_limit, telegram_enabled = interactive_wizard()
    else:
        # CLI mode
        if not args.targets:
            print("Error: --targets is required in non-interactive mode")
            return 1
            
        # Load targets
        if os.path.isfile(args.targets):
            targets = load_targets_from_file(args.targets)
        else:
            targets = [args.targets]
        
        # Parse modules
        if args.modules == 'all':
            registry = ModuleRegistry()
            selected_modules = registry.list_module_ids()
        elif args.modules:
            selected_modules = [m.strip() for m in args.modules.split(',')]
        else:
            selected_modules = ["ggb_scanner", "js_scanner", "git_scanner"]
        
        threads = args.threads
        rate_limit = args.rate_limit
        telegram_enabled = args.telegram
    
    # Load config
    config = cfg.load_config(args.config)
    
    # Override config with CLI parameters
    config.modules = selected_modules
    config.threads = threads
    config.rate_limit.requests_per_second = rate_limit
    config.rate_limit.burst = args.burst
    config.telegram.enabled = telegram_enabled
    config.outputs.directory = args.output_dir
    config.outputs.formats = [f.strip() for f in args.formats.split(',')]
    
    # Dry run - show plan and exit
    if args.dry_run:
        print("\n📋 Scan Plan (DRY RUN)")
        print("-" * 30)
        print(f"Targets ({len(targets)}):")
        for target in targets[:5]:  # Show first 5
            print(f"  - {target}")
        if len(targets) > 5:
            print(f"  ... and {len(targets) - 5} more")
        print(f"Modules: {', '.join(selected_modules)}")
        print(f"Threads: {threads}")
        print(f"Rate Limit: {rate_limit} req/s")
        print(f"Output: {args.output_dir}")
        print(f"Formats: {', '.join(config.outputs.formats)}")
        return 0
    
    # Run the scan
    print(f"\n🚀 Starting SpaceCracker scan...")
    print(f"Targets: {len(targets)}")
    print(f"Modules: {len(selected_modules)}")
    print(f"Threads: {threads}")
    
    try:
        # Initialize components
        runner = ScanRunner(config)
        reporter = ReportWriter(config)
        
        # Execute scan
        results = runner.run_scan(targets)
        
        # Generate reports
        reporter.write_reports(results)
        
        # Summary
        summary = results.get("summary", {})
        print(f"\n✅ Scan completed!")
        print(f"Findings: {summary.get('total_findings', 0)}")
        print(f"Errors: {summary.get('errors', 0)}")
        print(f"Reports saved to: {config.outputs.directory}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())