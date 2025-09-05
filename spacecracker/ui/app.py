#!/usr/bin/env python3
"""
SpaceCracker Pro - Flask Application
Main Flask app with configuration and error handling
"""

import os
import secrets
from flask import Flask, render_template, jsonify
from werkzeug.exceptions import HTTPException
from ..core.config import load_config

def create_app(config_file: str = None) -> Flask:
    """Create Flask application with configuration"""
    app = Flask(__name__)
    
    # Load SpaceCracker configuration
    sc_config = load_config(config_file)
    
    # Flask configuration
    app.config.update({
        'SECRET_KEY': os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32)),
        'DEBUG': sc_config.webui.debug,
        'SPACECRACKER_CONFIG': sc_config,
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file upload
        'UPLOAD_FOLDER': 'uploads',
        'JSON_SORT_KEYS': False
    })
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from .routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Page not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(HTTPException)
    def handle_exception(error):
        response = jsonify({
            'error': error.description,
            'code': error.code
        })
        response.status_code = error.code
        return response
    
    # Template filters
    @app.template_filter('datetime')
    def datetime_filter(timestamp):
        from datetime import datetime
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    @app.template_filter('severity_class')
    def severity_class_filter(severity):
        severity_map = {
            'Critical': 'danger',
            'High': 'warning', 
            'Medium': 'info',
            'Low': 'secondary'
        }
        return severity_map.get(severity, 'secondary')
    
    return app

# Create default app instance
app = create_app()