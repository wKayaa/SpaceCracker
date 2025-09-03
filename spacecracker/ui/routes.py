#!/usr/bin/env python3
"""
SpaceCracker Pro - Flask Routes
Main routes for the web interface
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, send_file

# Import SpaceCracker components
from ..core.registry import ModuleRegistry

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Global variables for scan state
current_scan = None
scan_results = []

@main_bp.route('/')
def dashboard():
    """Main dashboard page"""
    config = current_app.config['SPACECRACKER_CONFIG']
    
    # Get recent scan statistics
    stats = {
        'total_scans': len(scan_results),
        'critical_findings': len([r for r in scan_results if r.get('severity') == 'Critical']),
        'high_findings': len([r for r in scan_results if r.get('severity') == 'High']),
        'active_modules': len(config.modules)
    }
    
    return render_template('dashboard.html', stats=stats, recent_results=scan_results[-10:])

@main_bp.route('/scan')
def scan_page():
    """Scan launch page"""
    config = current_app.config['SPACECRACKER_CONFIG']
    registry = ModuleRegistry()
    
    return render_template('scan.html', 
                         available_modules=registry.list_modules(),
                         config=config)

@main_bp.route('/results')
def results_page():
    """Results viewing page"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    severity_filter = request.args.get('severity', '')
    module_filter = request.args.get('module', '')
    
    # Filter results
    filtered_results = scan_results.copy()
    
    if severity_filter:
        filtered_results = [r for r in filtered_results if r.get('severity') == severity_filter]
    
    if module_filter:
        filtered_results = [r for r in filtered_results if r.get('module') == module_filter]
    
    # Pagination
    total = len(filtered_results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = filtered_results[start:end]
    
    # Get unique values for filters
    severities = sorted(list(set(r.get('severity', '') for r in scan_results if r.get('severity'))))
    modules = sorted(list(set(r.get('module', '') for r in scan_results if r.get('module'))))
    
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': end < total
    }
    
    return render_template('results.html', 
                         results=paginated_results,
                         pagination=pagination_info,
                         severities=severities,
                         modules=modules,
                         current_filters={
                             'severity': severity_filter,
                             'module': module_filter
                         })

@main_bp.route('/config')
def config_page():
    """Configuration management page"""
    config = current_app.config['SPACECRACKER_CONFIG']
    registry = ModuleRegistry()
    
    return render_template('config.html', 
                         config=config,
                         available_modules=registry.list_modules())

# API Routes
@api_bp.route('/scan/start', methods=['POST'])
def start_scan():
    """Start a new scan"""
    global current_scan
    
    try:
        if current_scan and not current_scan.get('finished', True):
            return jsonify({'error': 'Scan already in progress'}), 400
        
        # Get scan parameters
        data = request.get_json() or {}
        targets = data.get('targets', [])
        modules = data.get('modules', [])
        
        if not targets:
            return jsonify({'error': 'No targets specified'}), 400
        
        # Initialize scan
        current_scan = {
            'id': datetime.now().timestamp(),
            'targets': targets,
            'modules': modules,
            'status': 'starting',
            'progress': 0,
            'results': [],
            'errors': [],
            'start_time': datetime.now().isoformat(),
            'finished': False
        }
        
        return jsonify({
            'scan_id': current_scan['id'],
            'status': 'started',
            'message': 'Scan started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scan/status')
def scan_status():
    """Get current scan status"""
    if not current_scan:
        return jsonify({'status': 'no_scan'})
    
    return jsonify(current_scan)

@api_bp.route('/stats')
def get_stats():
    """Get real-time statistics"""
    config = current_app.config['SPACECRACKER_CONFIG']
    
    stats = {
        'total_findings': len(scan_results),
        'findings_by_severity': {},
        'findings_by_module': {},
        'active_scan': current_scan is not None and not current_scan.get('finished', True),
        'scan_progress': current_scan.get('progress', 0) if current_scan else 0,
    }
    
    # Calculate severity distribution
    for result in scan_results:
        severity = result.get('severity', 'Unknown')
        stats['findings_by_severity'][severity] = stats['findings_by_severity'].get(severity, 0) + 1
    
    return jsonify(stats)