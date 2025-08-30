#!/usr/bin/env python3
"""
Laravel Scanner Module
Advanced Laravel application security assessment module
"""

import re
import requests
import asyncio
import aiohttp
from typing import Dict, Any, List
from .base import BaseModule


class LaravelScanner(BaseModule):
    module_id = "laravel_scanner"
    name = "Laravel Security Scanner" 
    description = "Complete security assessment for Laravel applications including .env files, debug interfaces, and configuration exposure"
    supports_batch = True

    def __init__(self, config: Any = None):
        super().__init__(config)
        self.laravel_patterns = {
            'env_keys': [
                r'APP_KEY\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'DB_PASSWORD\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'DB_USERNAME\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'DB_HOST\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'DB_DATABASE\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_PASSWORD\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_USERNAME\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_HOST\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'AWS_ACCESS_KEY_ID\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'AWS_SECRET_ACCESS_KEY\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'REDIS_PASSWORD\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'SESSION_DRIVER\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'CACHE_DRIVER\s*=\s*["\']?([^"\'\\s]+)["\']?',
            ],
            'sensitive_config': [
                r'(APP_DEBUG\s*=\s*true)',
                r'(LOG_LEVEL\s*=\s*debug)',
                r'(APP_ENV\s*=\s*local)',
            ]
        }
        
        self.laravel_endpoints = [
            '.env',
            '.env.example', 
            '.env.local',
            '.env.production',
            '.env.staging',
            'config/app.php',
            'config/database.php',
            'config/mail.php',
            'config/services.php',
            'storage/logs/laravel.log',
            'bootstrap/cache/config.php',
            'artisan',
            '_debugbar/assets/stylesheets',
            'horizon/dashboard',
            'telescope/requests',
            'debug-bar'
        ]
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run Laravel scanner against target"""
        findings = []
        errors = []
        
        try:
            # Test Laravel-specific endpoints
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                for endpoint in self.laravel_endpoints:
                    try:
                        test_url = f"{target.rstrip('/')}/{endpoint}"
                        async with session.get(test_url) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Check for Laravel-specific patterns
                                laravel_finding = self._analyze_laravel_content(content, test_url, endpoint)
                                if laravel_finding:
                                    findings.append(laravel_finding)
                                    
                    except Exception as e:
                        errors.append(f"Error testing {endpoint}: {str(e)}")
                        
                # Test for debug mode indicators
                debug_findings = await self._check_debug_mode(session, target)
                findings.extend(debug_findings)
                
                # Test for framework detection
                framework_finding = await self._detect_laravel_framework(session, target)
                if framework_finding:
                    findings.append(framework_finding)
                    
        except Exception as e:
            errors.append(f"Laravel scanner error: {str(e)}")
        
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _analyze_laravel_content(self, content: str, url: str, endpoint: str) -> Dict[str, Any]:
        """Analyze content for Laravel-specific secrets and configurations"""
        secrets_found = {}
        
        # Check for environment variable patterns
        for category, patterns in self.laravel_patterns.items():
            secrets_found[category] = []
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.group(1):  # Has captured group
                        secrets_found[category].append({
                            'key': match.group(0).split('=')[0].strip(),
                            'value': match.group(1),
                            'line': content[:match.start()].count('\n') + 1
                        })
        
        # Only create finding if secrets were found
        if any(secrets_found.values()):
            severity = self._calculate_severity(secrets_found, endpoint)
            
            return {
                "id": f"laravel_{endpoint.replace('/', '_').replace('.', '_')}",
                "title": f"Laravel Configuration Exposure - {endpoint}",
                "severity": severity,
                "category": "config",
                "confidence": 0.9,
                "description": f"Exposed Laravel configuration file containing sensitive information",
                "evidence": {
                    "url": url,
                    "endpoint": endpoint,
                    "secrets": secrets_found,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                },
                "recommendation": "Secure Laravel configuration files and disable debug mode in production"
            }
        
        return None
    
    def _calculate_severity(self, secrets_found: Dict, endpoint: str) -> str:
        """Calculate severity based on types of secrets found"""
        if any(key in secrets_found.get('env_keys', []) for key in ['DB_PASSWORD', 'AWS_SECRET_ACCESS_KEY', 'MAIL_PASSWORD']):
            return "Critical"
        elif endpoint == '.env' or 'env_keys' in secrets_found:
            return "High"
        elif 'sensitive_config' in secrets_found:
            return "Medium"
        else:
            return "Low"
    
    async def _check_debug_mode(self, session: aiohttp.ClientSession, target: str) -> List[Dict[str, Any]]:
        """Check for Laravel debug mode indicators"""
        findings = []
        
        debug_indicators = [
            '/non-existent-route-12345',  # Trigger 404 to check for debug info
            '/?debug=1',
            '/debug'
        ]
        
        for indicator in debug_indicators:
            try:
                test_url = f"{target.rstrip('/')}{indicator}"
                async with session.get(test_url) as response:
                    content = await response.text()
                    
                    # Check for Laravel debug patterns
                    debug_patterns = [
                        r'Illuminate\\',
                        r'Laravel Framework',
                        r'Whoops\\',
                        r'DebugBar',
                        r'APP_DEBUG.*true',
                        r'Stack trace:'
                    ]
                    
                    for pattern in debug_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            findings.append({
                                "id": "laravel_debug_mode",
                                "title": "Laravel Debug Mode Enabled",
                                "severity": "High",
                                "category": "config",
                                "confidence": 0.8,
                                "description": "Laravel application running in debug mode, potentially exposing sensitive information",
                                "evidence": {
                                    "url": test_url,
                                    "debug_indicator": pattern,
                                    "response_status": response.status
                                },
                                "recommendation": "Disable debug mode by setting APP_DEBUG=false in production environment"
                            })
                            break
                            
            except Exception:
                continue  # Skip failed requests
                
        return findings
    
    async def _detect_laravel_framework(self, session: aiohttp.ClientSession, target: str) -> Dict[str, Any]:
        """Detect Laravel framework and version"""
        try:
            async with session.get(target) as response:
                headers = response.headers
                content = await response.text()
                
                # Check headers for Laravel indicators
                laravel_indicators = []
                
                if 'X-Powered-By' in headers and 'Laravel' in headers['X-Powered-By']:
                    laravel_indicators.append(f"X-Powered-By: {headers['X-Powered-By']}")
                
                # Check content for Laravel indicators
                content_patterns = [
                    r'Laravel v(\d+\.\d+)',
                    r'Laravel Framework (\d+\.\d+)',
                    r'Illuminate\\',
                    r'csrf-token.*content.*[a-zA-Z0-9]{40,}'
                ]
                
                for pattern in content_patterns:
                    match = re.search(pattern, content)
                    if match:
                        laravel_indicators.append(f"Content pattern: {pattern}")
                        
                if laravel_indicators:
                    return {
                        "id": "laravel_framework_detected",
                        "title": "Laravel Framework Detection",
                        "severity": "Low",
                        "category": "exposure",
                        "confidence": 0.7,
                        "description": "Laravel framework detected on target application",
                        "evidence": {
                            "url": target,
                            "indicators": laravel_indicators,
                            "headers": dict(headers)
                        },
                        "recommendation": "Ensure proper security hardening for Laravel applications"
                    }
                    
        except Exception:
            pass
            
        return None