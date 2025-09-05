#!/usr/bin/env python3
"""
SpaceCracker V2 - Web Panel Launcher
Launch the web panel with authentication and SSL support
"""

import argparse
import uvicorn
import sys
from pathlib import Path

# Add the project root to the path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from src.web.app import app


def main():
    parser = argparse.ArgumentParser(description='SpaceCracker V2 Web Panel')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on (default: 8080)')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--auth', choices=['enabled', 'disabled'], default='disabled', 
                       help='Enable authentication (default: disabled)')
    parser.add_argument('--ssl-cert', help='SSL certificate file')
    parser.add_argument('--ssl-key', help='SSL private key file')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    # Configure SSL if certificates provided
    ssl_config = None
    if args.ssl_cert and args.ssl_key:
        ssl_config = {
            'ssl_certfile': args.ssl_cert,
            'ssl_keyfile': args.ssl_key
        }
        protocol = 'https'
    else:
        protocol = 'http'
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                SpaceCracker V2 Web Panel                 ║
╠══════════════════════════════════════════════════════════╣
║  URL: {protocol}://{args.host}:{args.port}                      ║
║  Authentication: {args.auth.capitalize():<20}                  ║
║  SSL: {'Enabled' if ssl_config else 'Disabled':<20}                         ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Start the server
    uvicorn_config = {
        'app': app,
        'host': args.host,
        'port': args.port,
        'reload': args.reload
    }
    
    if ssl_config:
        uvicorn_config.update(ssl_config)
    
    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()