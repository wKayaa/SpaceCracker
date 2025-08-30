import argparse
import sys
import os
from typing import List
from .version import __version__
from .core import config as cfg
from .core.registry import ModuleRegistry
from .core.runner import ScanRunner
from .core.reporting import ReportWriter
from .utils.language import init_language, _
from .utils.performance import get_performance_manager

def interactive_wizard() -> tuple:
    """Run interactive wizard to collect scan parameters"""
    lang = init_language()  # Initialize with default language
    
    print(f"\n{_('wizard_title')}")
    print("=" * 50)
    
    # Authorization check
    print(f"\n{_('authorization_disclaimer')}")
    print(_('authorization_warning'))
    consent = input(_('authorization_prompt')).lower()
    
    if consent not in ['y', 'o']:  # Support both English 'y' and French 'o' (oui)
        print(_('authorization_required'))
        sys.exit(1)
    
    # Collect targets
    print(f"\n{_('step_target_config')}")
    target_input = input(_('target_input_prompt')).strip()
    
    if os.path.isfile(target_input):
        with open(target_input, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(_('targets_loaded', len(targets)))
    else:
        targets = [target_input]
        print(_('single_target', target_input))
    
    # Select modules
    print(f"\n{_('step_module_selection')}")
    registry = ModuleRegistry()
    available_modules = registry.list_modules()
    
    print(f"{_('available_modules')}:")
    for i, (module_id, info) in enumerate(available_modules.items(), 1):
        module_name = _(module_id, info['name'])  # Try to get translated name
        print(f"  {i}. {module_name} - {info['description']}")
    
    print(f"\n{_('module_selection_prompt')}")
    module_choice = input(_('choice_prompt')).strip().lower()
    
    if module_choice == 'all':
        selected_modules = list(available_modules.keys())
    else:
        try:
            indices = [int(x.strip()) - 1 for x in module_choice.split(',')]
            module_list = list(available_modules.keys())
            selected_modules = [module_list[i] for i in indices if 0 <= i < len(module_list)]
        except:
            print(_('invalid_selection'))
            selected_modules = list(available_modules.keys())
    
    print(_('selected_modules', ', '.join(selected_modules)))
    
    # Performance settings
    print(f"\n{_('step_performance')}")
    threads = input(_('threads_prompt')).strip() or "50"
    rate_limit = input(_('rate_limit_prompt')).strip() or "10"
    
    try:
        threads = int(threads)
        rate_limit = int(rate_limit)
    except:
        threads = 50
        rate_limit = 10
    
    # Telegram settings
    print(f"\n{_('step_telegram')}")
    telegram_enabled = input(_('telegram_prompt')).lower() in ['y', 'o']  # Support both languages
    
    # Confirm plan
    print(f"\n{_('scan_plan_summary')}")
    print("-" * 30)
    print(_('plan_targets', len(targets)))
    print(_('plan_modules', len(selected_modules)))
    print(_('plan_threads', threads))
    print(_('plan_rate_limit', rate_limit))
    print(_('plan_telegram', _('telegram_enabled') if telegram_enabled else _('telegram_disabled')))
    
    confirm = input(f"\n{_('proceed_prompt')}").lower()
    if confirm == 'n':
        print(_('scan_cancelled'))
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
        print(_('error_loading_targets', filename, e))
        sys.exit(1)
    
    return targets

def evyl_run_command(args):
    """Handle 'evyl run' style command for quick launching"""
    if len(args) < 1:
        print("Usage: evyl run <targets_file> [--options]")
        return 1
    
    targets_file = args[0]
    
    # Parse additional options
    language = 'en'
    performance_mode = 'auto'
    threads = None
    telegram = False
    dry_run = False
    
    i = 1
    while i < len(args):
        if args[i] == '--language' and i + 1 < len(args):
            language = args[i + 1]
            i += 2
        elif args[i] == '--performance-mode' and i + 1 < len(args):
            performance_mode = args[i + 1]
            i += 2
        elif args[i] == '--threads' and i + 1 < len(args):
            threads = int(args[i + 1])
            i += 2
        elif args[i] == '--telegram':
            telegram = True
            i += 1
        elif args[i] == '--dry-run':
            dry_run = True
            i += 1
        else:
            i += 1
    
    # Initialize language
    init_language(language)
    
    # Initialize performance manager
    perf_manager = get_performance_manager()
    profile = perf_manager.set_performance_mode(performance_mode)
    
    # Load targets
    if os.path.isfile(targets_file):
        targets = load_targets_from_file(targets_file)
    else:
        targets = [targets_file]
    
    # Optimize for target count
    perf_manager.optimize_for_target_count(len(targets))
    profile = perf_manager.get_current_profile()
    
    # Load default config
    config = cfg.load_config()
    
    # Apply performance profile and settings
    config.modules = ["laravel_scanner", "smtp_scanner", "ggb_scanner", "js_scanner", "git_scanner"]
    config.threads = threads if threads else profile.threads
    config.rate_limit.requests_per_second = profile.rate_limit
    config.rate_limit.burst = profile.burst
    config.telegram.enabled = telegram
    
    # Handle dry run
    if dry_run:
        print(f"\n📋 {_('scan_plan_summary')} (EVYL DRY RUN)")
        print("-" * 40)
        print(f"{_('plan_targets')} ({len(targets)}):")
        for target in targets[:5]:  # Show first 5
            print(f"  - {target}")
        if len(targets) > 5:
            print(f"  ... and {len(targets) - 5} more")
        print(f"{_('plan_modules')}: {', '.join(config.modules)}")
        print(f"Performance: {profile.name}")
        print(f"{_('plan_threads')}: {config.threads}")
        print(f"{_('plan_rate_limit')}: {profile.rate_limit} req/s")
        print(f"Language: {language.upper()}")
        print(f"Command: evyl run {targets_file}")
        return 0
    
    print(f"\n{_('scan_starting')}")
    print(f"{_('plan_targets')}: {len(targets)}")
    print(f"Performance: {profile.name}")
    print(f"{_('plan_threads')}: {config.threads}")
    print(f"Language: {language.upper()}")
    
    try:
        # Start performance monitoring
        perf_manager.start_monitoring()
        
        # Initialize components
        runner = ScanRunner(config)
        reporter = ReportWriter(config)
        
        # Execute scan
        results = runner.run_scan(targets)
        
        # Generate reports
        reporter.write_reports(results)
        
        # Summary
        summary = results.get("summary", {})
        print(f"\n{_('scan_completed')}")
        print(_('findings', summary.get('total_findings', 0)))
        print(_('errors', summary.get('errors', 0)))
        print(_('reports_saved', config.outputs.directory))
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{_('scan_interrupted')}")
        return 1
    except Exception as e:
        print(_('scan_failed', e))
        return 1
    finally:
        perf_manager.stop_monitoring()

def main():
    """Main CLI entry point"""
    # Check for 'evyl run' style command
    if len(sys.argv) >= 3 and sys.argv[1] == 'run':
        return evyl_run_command(sys.argv[2:])
    
    parser = argparse.ArgumentParser(
        description='SpaceCracker v3.1 - Advanced Laravel & Email Security Framework (Evyl-Compatible)'
    )
    
    # Add subcommand for 'run' to support both styles
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # 'run' subcommand
    run_parser = subparsers.add_parser('run', help='Quick launch scan with auto-configuration')
    run_parser.add_argument('targets', help='Target file or single target URL')
    run_parser.add_argument('--language', choices=['en', 'fr'], default='en', help='UI language')
    run_parser.add_argument('--performance-mode', choices=['low', 'normal', 'high', 'auto'], default='auto', help='Performance profile')
    run_parser.add_argument('--threads', type=int, help='Override thread count')
    run_parser.add_argument('--telegram', action='store_true', help='Enable Telegram notifications')
    run_parser.add_argument('--dry-run', action='store_true', help='Show scan plan without executing')
    
    # Standard arguments
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
    parser.add_argument('--language', choices=['en', 'fr'], default='en', help='UI language (English/French)')
    parser.add_argument('--performance-mode', choices=['low', 'normal', 'high', 'auto'], default='auto', help='Performance profile')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--list-modules', action='store_true', help='List available modules')
    parser.add_argument('--dry-run', action='store_true', help='Show scan plan without executing')
    parser.add_argument('--interactive', action='store_true', help='Force interactive wizard')
    parser.add_argument('--version', action='version', version=f'SpaceCracker v{__version__} (Evyl-Compatible)')
    
    args = parser.parse_args()
    
    # Initialize language early
    init_language(args.language)
    
    # Initialize performance manager
    perf_manager = get_performance_manager()
    
    # Handle 'run' subcommand
    if args.command == 'run':
        return evyl_run_command([args.targets] + [f'--{k.replace("_", "-")}' if v is True else f'--{k.replace("_", "-")}={v}' for k, v in vars(args).items() if k not in ['command', 'targets'] and v not in [None, False]])
    
    # List modules and exit
    if args.list_modules:
        registry = ModuleRegistry()
        modules = registry.list_modules()
        print(f"\n{_('available_modules')}:")
        for module_id, info in modules.items():
            module_name = _(module_id) if _(module_id) != module_id else info['name']
            print(f"  {module_id}: {module_name} - {info['description']}")
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
            print(_('error_targets_required'))
            return 1
            
        # Load targets
        if os.path.isfile(args.targets):
            targets = load_targets_from_file(args.targets)
        else:
            targets = [args.targets]
        
        # Parse modules - include new Laravel and SMTP scanners by default
        if args.modules == 'all':
            registry = ModuleRegistry()
            selected_modules = registry.list_module_ids()
        elif args.modules:
            selected_modules = [m.strip() for m in args.modules.split(',')]
        else:
            selected_modules = ["laravel_scanner", "smtp_scanner", "ggb_scanner", "js_scanner", "git_scanner"]
        
        threads = args.threads
        rate_limit = args.rate_limit
        telegram_enabled = args.telegram
    
    # Set performance mode and optimize for target count
    profile = perf_manager.set_performance_mode(args.performance_mode)
    perf_manager.optimize_for_target_count(len(targets))
    profile = perf_manager.get_current_profile()
    
    # Load config
    config = cfg.load_config(args.config)
    
    # Override config with CLI parameters and performance profile
    config.modules = selected_modules
    config.threads = threads if threads else profile.threads
    config.rate_limit.requests_per_second = rate_limit if rate_limit != 10 else profile.rate_limit
    config.rate_limit.burst = args.burst if args.burst != 20 else profile.burst
    config.telegram.enabled = telegram_enabled
    config.outputs.directory = args.output_dir
    config.outputs.formats = [f.strip() for f in args.formats.split(',')]
    
    # Dry run - show plan and exit
    if args.dry_run:
        print(f"\n📋 {_('scan_plan_summary')} (DRY RUN)")
        print("-" * 30)
        print(f"{_('plan_targets')} ({len(targets)}):")
        for target in targets[:5]:  # Show first 5
            print(f"  - {target}")
        if len(targets) > 5:
            print(f"  ... and {len(targets) - 5} more")
        print(f"{_('plan_modules')}: {', '.join(selected_modules)}")
        print(f"Performance: {profile.name}")
        print(f"{_('plan_threads')}: {config.threads}")
        print(f"{_('plan_rate_limit')}: {config.rate_limit.requests_per_second}")
        print(f"Output: {args.output_dir}")
        print(f"Formats: {', '.join(config.outputs.formats)}")
        print(f"Language: {args.language.upper()}")
        return 0
    
    # Run the scan
    print(f"\n{_('scan_starting')}")
    print(_('plan_targets', len(targets)))
    print(_('plan_modules', len(selected_modules)))
    print(f"Performance: {profile.name}")
    print(_('plan_threads', config.threads))
    
    try:
        # Start performance monitoring
        perf_manager.start_monitoring()
        
        # Initialize components
        runner = ScanRunner(config)
        reporter = ReportWriter(config)
        
        # Execute scan
        results = runner.run_scan(targets)
        
        # Generate reports
        reporter.write_reports(results)
        
        # Summary
        summary = results.get("summary", {})
        print(f"\n{_('scan_completed')}")
        print(_('findings', summary.get('total_findings', 0)))
        print(_('errors', summary.get('errors', 0)))
        print(_('reports_saved', config.outputs.directory))
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{_('scan_interrupted')}")
        return 1
    except Exception as e:
        print(_('scan_failed', e))
        return 1
    finally:
        perf_manager.stop_monitoring()

if __name__ == "__main__":
    sys.exit(main())