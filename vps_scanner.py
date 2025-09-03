#!/usr/bin/env python3
"""
VPS-Optimized SpaceCracker Launcher
Quick launcher with VPS-optimized settings for high-bandwidth scanning
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spacecracker.cli import main

def vps_main():
    """VPS-optimized main function"""
    
    # Check if targets file is provided
    if len(sys.argv) < 2:
        print("🚀 VPS SpaceCracker - High-Bandwidth Scanner")
        print("=" * 50)
        print("Usage:")
        print(f"  {sys.argv[0]} <targets_file>")
        print(f"  {sys.argv[0]} <single_target>")
        print()
        print("Examples:")
        print(f"  {sys.argv[0]} domains.txt")
        print(f"  {sys.argv[0]} 192.168.1.1")
        print(f"  {sys.argv[0]} example.com")
        print()
        print("Features:")
        print("  • VPS-optimized (100 threads, 50 req/s)")
        print("  • Real-time progress display")
        print("  • Telegram notifications (if configured)")
        print("  • HTTP/HTTPS/IP support")
        print("  • Auto URL validation")
        print()
        sys.exit(1)
    
    # Build arguments for VPS mode
    targets_file = sys.argv[1]
    
    # Set VPS-optimized arguments
    vps_args = [
        'run', targets_file,
        '--performance-mode=vps',
        '--config=config_vps.json',
        '--language=en',
        '--telegram'  # Enable Telegram if configured
    ]
    
    # Add any additional arguments passed
    vps_args.extend(sys.argv[2:])
    
    # Override sys.argv for the main CLI function
    sys.argv = ['spacecracker'] + vps_args
    
    print("🚀 Starting VPS-Optimized SpaceCracker...")
    print("=" * 50)
    print("🔧 Configuration:")
    print("  • Performance Mode: VPS (100 threads)")
    print("  • Rate Limit: 50 requests/second")  
    print("  • Protocol: HTTP (safer for mass scanning)")
    print("  • Progress Updates: Real-time + Telegram")
    print("  • URL Validation: Enabled")
    print("=" * 50)
    
    return main()

if __name__ == "__main__":
    try:
        sys.exit(vps_main())
    except KeyboardInterrupt:
        print("\n🛑 VPS SpaceCracker interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)