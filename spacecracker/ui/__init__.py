#!/usr/bin/env python3
"""
SpaceCracker Pro - Web UI Package
Flask-based web interface with dark pink theme
"""

from .app import create_app, app
from .routes import main_bp, api_bp

__all__ = ['create_app', 'app', 'main_bp', 'api_bp']