#!/usr/bin/env python3
"""
SpaceCracker V2 - Enhanced JavaScript Analyzer
Advanced JavaScript file analysis with beautification, credential extraction, and API endpoint discovery
"""

import re
import json
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from .base import BaseModule


class JSScanner(BaseModule):
    """Enhanced JavaScript analyzer with comprehensive credential and endpoint detection"""
    
    module_id = "js_scanner" 
    name = "JavaScript Analyzer"
    description = "Advanced JavaScript file analysis for credentials, APIs, and configuration objects"
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        
        # Enhanced pattern collection matching problem statement
        self.patterns = {
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret': r'[0-9a-zA-Z/+=]{40}',
            'api_key': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            'firebase': r'firebaseConfig\s*=\s*\{([^}]+)\}',
            'stripe': r'(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}',
            'google_api': r'AIza[0-9A-Za-z_\-]{35}',
            'slack_token': r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24,32}',
            'github_token': r'ghp_[0-9a-zA-Z]{36}',
            'jwt_token': r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+',
            'sendgrid_key': r'SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}',
            'mailgun_key': r'key-[0-9a-zA-Z]{32}',
            'twilio_sid': r'AC[0-9a-fA-F]{32}',
            'discord_webhook': r'https://discord(?:app)?\.com/api/webhooks/[0-9]{18}/[a-zA-Z0-9_\-]{68}',
            'database_url': r'(mysql|postgres|mongodb)://[^\s"\']+',
            'secret_key': r'secret[_-]?key["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            'password': r'password["\']?\s*[:=]\s*["\']([^"\']{4,})["\']',
            'private_key': r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
            'oauth_token': r'oauth[_-]?token["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
            'access_token': r'access[_-]?token["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
        }
        
        # Common JavaScript file extensions and paths
        self.js_extensions = ['.js', '.min.js', '.jsx', '.ts', '.tsx', '.mjs']
        self.common_js_paths = [
            '/js/', '/javascript/', '/assets/', '/static/', '/build/',
            '/dist/', '/public/', '/scripts/', '/app/', '/src/',
            '/vendor/', '/libs/', '/lib/', '/modules/', '/components/'
        ]
        
        # Configuration object patterns
        self.config_patterns = {
            'firebase_config': r'firebaseConfig\s*[:=]\s*\{([^}]+)\}',
            'api_config': r'(?:api|API)Config\s*[:=]\s*\{([^}]+)\}',
            'auth_config': r'(?:auth|Auth)Config\s*[:=]\s*\{([^}]+)\}',
            'database_config': r'(?:db|database|Database)Config\s*[:=]\s*\{([^}]+)\}',
            'aws_config': r'(?:aws|AWS)Config\s*[:=]\s*\{([^}]+)\}',
            'env_config': r'(?:env|ENV|environment)\s*[:=]\s*\{([^}]+)\}',
        }
        
        # API endpoint patterns
        self.api_patterns = [
            r'["\']https?://[^"\']+/api/[^"\']+["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.[get|post|put|delete|patch]+\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)["\']',
            r'endpoint\s*[:=]\s*["\']([^"\']+)["\']',
            r'baseURL\s*[:=]\s*["\']([^"\']+)["\']',
            r'api[_-]?url\s*[:=]\s*["\']([^"\']+)["\']',
        ]
    
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run enhanced JavaScript analyzer against target"""
        findings = []
        errors = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # 1. Discover JavaScript files
                js_files = await self._discover_js_files(session, target)
                
                # 2. Analyze each JavaScript file
                for js_url in js_files[:20]:  # Limit to 20 files for performance
                    try:
                        file_findings = await self._analyze_js_file(session, js_url)
                        findings.extend(file_findings)
                    except Exception as e:
                        errors.append(f"Error analyzing {js_url}: {str(e)}")
                        continue
                
        except Exception as e:
            errors.append(f"JavaScript scanner error: {str(e)}")
        
        return {
            "module": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    async def _discover_js_files(self, session: aiohttp.ClientSession, target: str) -> List[str]:
        """Discover JavaScript files from the target website"""
        js_files = set()
        
        try:
            # Get main page to find JavaScript references
            async with session.get(target) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Find script tags
                    script_matches = re.findall(r'<script[^>]*src\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
                    for src in script_matches:
                        if any(ext in src.lower() for ext in self.js_extensions):
                            full_url = urljoin(target, src)
                            js_files.add(full_url)
                    
                    # Find inline references to JS files
                    inline_matches = re.findall(r'["\']([^"\']*\.js(?:\?[^"\']*)?)["\']', content)
                    for match in inline_matches:
                        full_url = urljoin(target, match)
                        js_files.add(full_url)
            
            # Try common JavaScript paths
            for path in self.common_js_paths:
                try:
                    test_url = urljoin(target, path)
                    async with session.get(test_url) as response:
                        if response.status == 200:
                            # Look for directory listing or additional JS files
                            content = await response.text()
                            js_matches = re.findall(r'href\s*=\s*["\']([^"\']*\.js[^"\']*)["\']', content, re.IGNORECASE)
                            for match in js_matches:
                                full_url = urljoin(test_url, match)
                                js_files.add(full_url)
                except:
                    continue
            
            # Try common JavaScript file names
            common_files = [
                'app.js', 'main.js', 'bundle.js', 'vendor.js', 'config.js',
                'settings.js', 'env.js', 'auth.js', 'api.js', 'firebase.js',
                'aws.js', 'jquery.js', 'bootstrap.js', 'react.js', 'vue.js'
            ]
            
            for filename in common_files:
                for path in ['/', '/js/', '/assets/', '/static/']:
                    test_url = urljoin(target, f"{path}{filename}")
                    try:
                        async with session.head(test_url) as response:
                            if response.status == 200:
                                js_files.add(test_url)
                    except:
                        continue
                        
        except Exception as e:
            pass
        
        return list(js_files)
    
    async def _analyze_js_file(self, session: aiohttp.ClientSession, js_url: str) -> List[Dict[str, Any]]:
        """Comprehensive analysis of a JavaScript file"""
        findings = []
        
        try:
            async with session.get(js_url) as response:
                if response.status != 200:
                    return findings
                
                content = await response.text()
                
                # Skip if file is too large (> 5MB)
                if len(content) > 5 * 1024 * 1024:
                    return findings
                
                # 1. Beautify minified code for better analysis
                beautified_content = self._beautify_js(content)
                
                # 2. Extract hardcoded credentials
                credential_findings = self._extract_credentials(beautified_content, js_url)
                findings.extend(credential_findings)
                
                # 3. Find API endpoints
                endpoint_findings = self._extract_api_endpoints(beautified_content, js_url)
                findings.extend(endpoint_findings)
                
                # 4. Extract configuration objects
                config_findings = self._extract_configurations(beautified_content, js_url)
                findings.extend(config_findings)
                
                # 5. Find sensitive comments
                comment_findings = self._extract_sensitive_comments(beautified_content, js_url)
                findings.extend(comment_findings)
                
        except Exception as e:
            pass
        
        return findings
    
    def _beautify_js(self, content: str) -> str:
        """Basic JavaScript beautification for minified code"""
        if self._is_minified(content):
            # Simple beautification - add line breaks after common patterns
            beautified = content
            
            # Add line breaks after semicolons and braces
            beautified = re.sub(r';', ';\n', beautified)
            beautified = re.sub(r'\{', '{\n', beautified)
            beautified = re.sub(r'\}', '\n}\n', beautified)
            beautified = re.sub(r',', ',\n', beautified)
            
            # Remove excessive line breaks
            beautified = re.sub(r'\n\s*\n', '\n', beautified)
            
            return beautified
        
        return content
    
    def _is_minified(self, content: str) -> bool:
        """Check if JavaScript code appears to be minified"""
        lines = content.split('\n')
        
        # Check for long lines (typical of minified code)
        long_lines = sum(1 for line in lines if len(line) > 200)
        
        # Check for lack of whitespace and formatting
        whitespace_ratio = sum(1 for char in content if char.isspace()) / len(content) if content else 0
        
        return long_lines > len(lines) * 0.3 or whitespace_ratio < 0.05
    
    def _extract_credentials(self, content: str, js_url: str) -> List[Dict[str, Any]]:
        """Extract hardcoded credentials from JavaScript"""
        findings = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].replace('\n', ' ')
                
                # Determine severity based on credential type
                severity = self._assess_credential_severity(pattern_name)
                
                findings.append({
                    "id": f"js_credential_{pattern_name}_{hash(match.group(0)) % 10000}",
                    "title": f"Hardcoded Credential in JavaScript: {pattern_name}",
                    "severity": severity,
                    "category": "credential_exposure",
                    "confidence": 0.8,
                    "description": f"JavaScript file contains hardcoded {pattern_name.replace('_', ' ')}",
                    "evidence": {
                        "file_url": js_url,
                        "credential_type": pattern_name,
                        "credential_value": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        "context": context,
                        "line_number": content[:match.start()].count('\n') + 1
                    }
                })
        
        return findings
    
    def _extract_api_endpoints(self, content: str, js_url: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from JavaScript"""
        endpoints = set()
        findings = []
        
        for pattern in self.api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Extract URL from match (handle different capture groups)
                url = match if isinstance(match, str) else match[0] if match else ""
                
                if url and url.startswith(('http://', 'https://')):
                    endpoints.add(url)
        
        for endpoint in endpoints:
            findings.append({
                "id": f"js_api_endpoint_{hash(endpoint) % 10000}",
                "title": f"API Endpoint Discovered: {endpoint}",
                "severity": "Low",
                "category": "information_disclosure",
                "confidence": 0.7,
                "description": f"JavaScript file contains reference to API endpoint",
                "evidence": {
                    "file_url": js_url,
                    "endpoint": endpoint,
                    "endpoint_domain": urlparse(endpoint).netloc
                }
            })
        
        return findings
    
    def _extract_configurations(self, content: str, js_url: str) -> List[Dict[str, Any]]:
        """Extract configuration objects from JavaScript"""
        findings = []
        
        for config_type, pattern in self.config_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                config_content = match.group(1)
                
                # Try to parse as JSON-like object
                config_data = self._parse_js_object(config_content)
                
                # Check if configuration contains sensitive data
                sensitive_keys = ['key', 'secret', 'token', 'password', 'credential', 'auth']
                has_sensitive = any(key in config_content.lower() for key in sensitive_keys)
                
                if has_sensitive or config_data:
                    findings.append({
                        "id": f"js_config_{config_type}_{hash(config_content) % 10000}",
                        "title": f"Configuration Object Exposed: {config_type}",
                        "severity": "Medium" if has_sensitive else "Low",
                        "category": "information_disclosure",
                        "confidence": 0.8,
                        "description": f"JavaScript file contains {config_type.replace('_', ' ')} configuration",
                        "evidence": {
                            "file_url": js_url,
                            "config_type": config_type,
                            "config_content": config_content[:500] + "..." if len(config_content) > 500 else config_content,
                            "parsed_data": config_data
                        }
                    })
        
        return findings
    
    def _extract_sensitive_comments(self, content: str, js_url: str) -> List[Dict[str, Any]]:
        """Extract sensitive information from JavaScript comments"""
        findings = []
        
        # Find all comments (both // and /* */ style)
        comment_patterns = [
            r'//.*$',  # Single line comments
            r'/\*.*?\*/'  # Multi-line comments
        ]
        
        sensitive_keywords = [
            'password', 'secret', 'key', 'token', 'credential', 'auth',
            'TODO.*password', 'FIXME.*auth', 'hack', 'temp.*key'
        ]
        
        for comment_pattern in comment_patterns:
            comments = re.findall(comment_pattern, content, re.MULTILINE | re.DOTALL)
            
            for comment in comments:
                for keyword in sensitive_keywords:
                    if re.search(keyword, comment, re.IGNORECASE):
                        findings.append({
                            "id": f"js_sensitive_comment_{hash(comment) % 10000}",
                            "title": "Sensitive Information in Comment",
                            "severity": "Low",
                            "category": "information_disclosure",
                            "confidence": 0.6,
                            "description": f"JavaScript comment may contain sensitive information",
                            "evidence": {
                                "file_url": js_url,
                                "comment": comment.strip(),
                                "keyword_matched": keyword
                            }
                        })
                        break  # Only report once per comment
        
        return findings
    
    def _parse_js_object(self, obj_string: str) -> Optional[Dict]:
        """Attempt to parse JavaScript object as JSON"""
        try:
            # Clean up the object string for JSON parsing
            cleaned = obj_string.strip()
            
            # Replace single quotes with double quotes
            cleaned = re.sub(r"'([^']*)'", r'"\1"', cleaned)
            
            # Handle unquoted keys
            cleaned = re.sub(r'(\w+):', r'"\1":', cleaned)
            
            # Remove trailing commas
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            
            return json.loads('{' + cleaned + '}')
        except:
            return None
    
    def _assess_credential_severity(self, credential_type: str) -> str:
        """Assess severity based on credential type"""
        critical_types = ['aws_key', 'aws_secret', 'private_key', 'database_url']
        high_types = ['api_key', 'stripe', 'github_token', 'slack_token', 'sendgrid_key']
        
        if credential_type in critical_types:
            return 'Critical'
        elif credential_type in high_types:
            return 'High'
        else:
            return 'Medium'