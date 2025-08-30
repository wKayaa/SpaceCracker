#!/usr/bin/env python3
"""
JavaScript Scanner Module
Scans for JavaScript files and extracts sensitive information
"""

import asyncio
import aiohttp
import logging
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class JSScanner:
    """JavaScript file scanner and analyzer"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # JavaScript file extensions and paths
        self.js_paths = [
            '/js/',
            '/javascript/',
            '/scripts/',
            '/static/js/',
            '/assets/js/',
            '/assets/javascript/',
            '/public/js/',
            '/dist/js/',
            '/build/js/',
            '/src/js/',
            '/app.js',
            '/main.js',
            '/bundle.js',
            '/vendor.js',
            '/config.js',
            '/settings.js',
            '/env.js',
            '/api.js'
        ]
        
        # Sensitive patterns in JavaScript
        self.js_patterns = {
            'api_keys': [
                r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'apikey["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'access[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'secret[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']'
            ],
            'aws_keys': [
                r'AKIA[0-9A-Z]{16}',
                r'aws[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'aws[_-]?secret[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            ],
            'database_urls': [
                r'mongodb://[^"\'\s]+',
                r'mysql://[^"\'\s]+',
                r'postgresql://[^"\'\s]+',
                r'redis://[^"\'\s]+',
                r'sqlite://[^"\'\s]+'
            ],
            'endpoints': [
                r'https?://[^"\'\s]+/api[^"\'\s]*',
                r'/api/v[0-9]+[^"\'\s]*',
                r'/graphql[^"\'\s]*',
                r'/webhook[^"\'\s]*'
            ],
            'tokens': [
                r'token["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'bearer["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'jwt["\']?\s*[:=]\s*["\']([^"\']{30,})["\']'
            ],
            'emails': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ],
            'phone_numbers': [
                r'\+?[1-9]\d{1,14}',
                r'\(\d{3}\)\s*\d{3}-\d{4}'
            ],
            'internal_ips': [
                r'192\.168\.\d{1,3}\.\d{1,3}',
                r'10\.\d{1,3}\.\d{1,3}\.\d{1,3}',
                r'172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}'
            ],
            'comments': [
                r'//.*(?:TODO|FIXME|HACK|BUG|NOTE).*',
                r'/\*.*?(?:TODO|FIXME|HACK|BUG|NOTE).*?\*/'
            ]
        }
        
    async def scan(self, session, target):
        """Main scanning function for JavaScript"""
        results = []
        
        try:
            # Get main page and extract JS references
            js_files = await self._extract_js_files(session, target)
            
            # Test common JS paths
            for js_path in self.js_paths:
                js_url = urljoin(target, js_path)
                js_files.add(js_url)
                
            # Analyze each JS file
            for js_file in js_files:
                result = await self._analyze_js_file(session, js_file, target)
                if result:
                    results.append(result)
                    
        except Exception as e:
            self.logger.error(f"JS Scanner error for {target}: {e}")
            
        return results
        
    async def _extract_js_files(self, session, target):
        """Extract JavaScript file URLs from HTML"""
        js_files = set()
        
        try:
            async with session.get(target) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find script tags with src
                    for script in soup.find_all('script', src=True):
                        src = script['src']
                        if src:
                            # Convert relative URLs to absolute
                            abs_url = urljoin(target, src)
                            js_files.add(abs_url)
                            
                    # Find inline script references
                    inline_js_pattern = r'["\']([^"\']*\.js(?:\?[^"\']*)?)["\']'
                    matches = re.findall(inline_js_pattern, content)
                    for match in matches:
                        abs_url = urljoin(target, match)
                        js_files.add(abs_url)
                        
        except Exception as e:
            self.logger.debug(f"Error extracting JS files from {target}: {e}")
            
        return js_files
        
    async def _analyze_js_file(self, session, js_url, base_target):
        """Analyze a single JavaScript file"""
        try:
            async with session.get(js_url) as response:
                if response.status == 200:
                    content = await response.text()
                    content_length = len(content)
                    
                    # Skip if file is too large (> 5MB)
                    if content_length > 5 * 1024 * 1024:
                        return None
                        
                    # Extract sensitive information
                    findings = {}
                    total_findings = 0
                    
                    for category, patterns in self.js_patterns.items():
                        category_findings = []
                        for pattern in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                            for match in matches:
                                if match.groups():
                                    category_findings.append(match.group(1))
                                else:
                                    category_findings.append(match.group(0))
                                    
                        if category_findings:
                            # Remove duplicates and limit results
                            unique_findings = list(set(category_findings))[:20]
                            findings[category] = unique_findings
                            total_findings += len(unique_findings)
                            
                    if total_findings > 0:
                        # Calculate severity based on findings
                        severity = 'low'
                        if any(key in findings for key in ['api_keys', 'aws_keys', 'database_urls', 'tokens']):
                            severity = 'high'
                        elif any(key in findings for key in ['endpoints', 'emails']):
                            severity = 'medium'
                            
                        result = {
                            'module': 'js_scanner',
                            'type': 'js_secrets_found',
                            'url': js_url,
                            'base_target': base_target,
                            'status': response.status,
                            'content_length': content_length,
                            'findings': findings,
                            'total_findings': total_findings,
                            'severity': severity,
                            'headers': dict(response.headers)
                        }
                        
                        # Add file analysis
                        file_info = self._analyze_js_structure(content)
                        if file_info:
                            result.update(file_info)
                            
                        return result
                        
        except Exception as e:
            self.logger.debug(f"Error analyzing JS file {js_url}: {e}")
            
        return None
        
    def _analyze_js_structure(self, content):
        """Analyze JavaScript file structure"""
        analysis = {}
        
        try:
            # Check for common frameworks/libraries
            frameworks = {
                'React': ['React', 'ReactDOM', 'useState', 'useEffect'],
                'Vue': ['Vue', 'createApp', 'ref', 'computed'],
                'Angular': ['angular', '@angular', 'NgModule', 'Component'],
                'jQuery': ['jQuery', '$', 'jquery'],
                'Express': ['express', 'app.get', 'app.post'],
                'Node.js': ['require', 'module.exports', 'process.env'],
                'Webpack': ['__webpack_require__', 'webpackJsonp'],
                'Babel': ['_babel', '_interopRequireDefault']
            }
            
            detected_frameworks = []
            content_lower = content.lower()
            
            for framework, indicators in frameworks.items():
                if any(indicator.lower() in content_lower for indicator in indicators):
                    detected_frameworks.append(framework)
                    
            if detected_frameworks:
                analysis['frameworks'] = detected_frameworks
                
            # Check for minification
            lines = content.split('\n')
            avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
            
            if avg_line_length > 200 or len(lines) < 10:
                analysis['minified'] = True
            else:
                analysis['minified'] = False
                
            # Count functions and variables
            function_count = len(re.findall(r'function\s+\w+', content, re.IGNORECASE))
            var_count = len(re.findall(r'(?:var|let|const)\s+\w+', content, re.IGNORECASE))
            
            analysis['function_count'] = function_count
            analysis['variable_count'] = var_count
            
            # Check for source maps
            if 'sourceMappingURL' in content:
                analysis['has_source_map'] = True
                
            # Check for development indicators
            dev_indicators = ['console.log', 'debugger', 'console.debug', 'alert(']
            dev_count = sum(content.lower().count(indicator) for indicator in dev_indicators)
            if dev_count > 0:
                analysis['development_code'] = True
                analysis['debug_statements'] = dev_count
                
        except Exception as e:
            self.logger.debug(f"Error analyzing JS structure: {e}")
            
        return analysis