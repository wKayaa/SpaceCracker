#!/usr/bin/env python3
"""
SpaceCracker Pro - Web UI Server
Launch the web interface
"""

import os
import sys
import webbrowser
from threading import Timer

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spacecracker.ui.app import create_app
from spacecracker.core.config import load_config

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://127.0.0.1:8080')

if __name__ == '__main__':
    # Load configuration
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    config = load_config(config_file)
    
    # Create Flask app
    app = create_app(config_file)
    
    print("🚀 SpaceCracker Pro Web UI Starting...")
    print(f"📊 Dashboard: http://{config.webui.host}:{config.webui.port}")
    print(f"🎨 Theme: {config.webui.theme}")
    print("Press Ctrl+C to stop")
    
    # Open browser automatically if enabled
    if not config.webui.debug:
        Timer(1.5, open_browser).start()
    
    # Run the Flask development server
    try:
        app.run(
            host=config.webui.host,
            port=config.webui.port,
            debug=config.webui.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 SpaceCracker Pro Web UI stopped")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        sys.exit(1)