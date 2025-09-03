#!/usr/bin/env python3
"""
SpaceCracker Pro - Path Scanner Module
Intelligent path discovery with wordlist support and content detection
"""

import asyncio
import aiohttp
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urljoin, urlparse
import re
from ..utils.http import create_session
from .base import BaseModule

class PathScanner(BaseModule):
    """Advanced path scanner with intelligent content detection"""
    
    module_id = "path_scanner"
    name = "Path Scanner"
    description = "Intelligent path discovery with wordlist support"
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.wordlists = self._load_wordlists()
        self.content_patterns = self._init_content_patterns()
        self.recursive_depth = getattr(config, 'recursive_depth', 3) if config else 3
        
    def _load_wordlists(self) -> Dict[str, List[str]]:
        """Load wordlists from files"""
        wordlists = {
            'common_paths': self._load_default_paths(),
            'admin_paths': self._load_admin_paths(),
            'api_paths': self._load_api_paths(),
            'config_paths': self._load_config_paths()
        }
        
        # Try to load custom wordlists
        wordlist_dir = Path("wordlists")
        if wordlist_dir.exists():
            for wordlist_file in wordlist_dir.glob("*.txt"):
                try:
                    with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                        paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        wordlists[wordlist_file.stem] = paths
                        self.logger.info(f"Loaded {len(paths)} paths from {wordlist_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to load wordlist {wordlist_file}: {e}")
        
        return wordlists
    
    def _load_default_paths(self) -> List[str]:
        """Load default common paths"""
        return [
            # Common directories
            '/admin/', '/administrator/', '/panel/', '/dashboard/',
            '/wp-admin/', '/wp-content/', '/wp-includes/',
            '/uploads/', '/files/', '/assets/', '/static/',
            '/backup/', '/backups/', '/tmp/', '/temp/',
            '/logs/', '/log/', '/cache/',
            
            # Common files
            '/robots.txt', '/sitemap.xml', '/.htaccess', '/.htpasswd',
            '/config.php', '/config.json', '/.env', '/settings.php',
            '/readme.txt', '/README.md', '/changelog.txt',
            '/phpinfo.php', '/info.php', '/test.php',
            
            # Development/Debug
            '/debug/', '/dev/', '/test/', '/staging/',
            '/development/', '/.git/', '/.svn/', '/.hg/',
            '/server-status', '/server-info',
            
            # API endpoints
            '/api/', '/v1/', '/v2/', '/api/v1/', '/api/v2/',
            '/graphql', '/swagger/', '/docs/', '/openapi.json'
        ]
    
    def _load_admin_paths(self) -> List[str]:
        """Load admin-specific paths"""
        return [
            '/admin/', '/administrator/', '/admin.php', '/admin.html',
            '/panel/', '/cpanel/', '/control/', '/dashboard/',
            '/manage/', '/manager/', '/management/',
            '/login/', '/signin/', '/auth/', '/authentication/',
            '/wp-admin/', '/wp-login.php', '/wp-admin.php',
            '/phpmyadmin/', '/pma/', '/mysql/',
            '/mailman/', '/webmail/', '/mail/',
            '/ftp/', '/sftp/', '/ssh/',
            '/console/', '/terminal/', '/shell/'
        ]
    
    def _load_api_paths(self) -> List[str]:
        """Load API-specific paths"""
        return [
            '/api/', '/api/v1/', '/api/v2/', '/api/v3/',
            '/rest/', '/restful/', '/rest/v1/',
            '/graphql/', '/graphiql/', '/playground/',
            '/swagger/', '/swagger-ui/', '/docs/',
            '/openapi.json', '/api-docs/', '/documentation/',
            '/endpoints/', '/services/', '/rpc/',
            '/json/', '/xml/', '/soap/',
            '/webhooks/', '/callback/', '/notify/'
        ]
    
    def _load_config_paths(self) -> List[str]:
        """Load configuration file paths"""
        return [
            '/.env', '/.env.local', '/.env.production', '/.env.development',
            '/config.php', '/config.json', '/config.xml', '/config.yml',
            '/configuration.php', '/settings.php', '/app.config',
            '/web.config', '/httpd.conf', '/nginx.conf',
            '/.htaccess', '/.htpasswd', '/robots.txt',
            '/crossdomain.xml', '/clientaccesspolicy.xml',
            '/security.txt', '/.well-known/security.txt',
            '/package.json', '/composer.json', '/requirements.txt'
        ]
    
    def _init_content_patterns(self) -> Dict[str, List[str]]:
        """Initialize content detection patterns"""
        return {
            'admin_panel': [
                r'<title>.*?admin.*?</title>',
                r'<title>.*?login.*?</title>',
                r'<title>.*?dashboard.*?</title>',
                r'admin.*?panel',
                r'control.*?panel',
                r'management.*?interface'
            ],
            'database_info': [
                r'mysql.*?error',
                r'postgresql.*?error',
                r'oracle.*?error',
                r'sqlite.*?error',
                r'mongodb.*?error',
                r'database.*?connection.*?failed'
            ],
            'debug_info': [
                r'debug.*?mode',
                r'stack.*?trace',
                r'error.*?reporting',
                r'xdebug',
                r'var_dump',
                r'print_r'
            ],
            'sensitive_files': [
                r'BEGIN.*?PRIVATE.*?KEY',
                r'BEGIN.*?RSA.*?PRIVATE.*?KEY',
                r'ssh-rsa',
                r'ssh-dss',
                r'password.*?hash',
                r'api.*?key.*?[=:].*?["\'][a-zA-Z0-9]{20,}["\']'
            ],
            'version_info': [
                r'server.*?version',
                r'php.*?version',
                r'apache.*?version',
                r'nginx.*?version',
                r'powered.*?by',
                r'x-powered-by'
            ]
        }
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run path scanner against target"""
        findings = []
        errors = []
        scanned_paths = set()
        
        try:
            async with create_session() as session:
                # Start with all wordlists
                all_paths = set()
                for wordlist_name, paths in self.wordlists.items():
                    all_paths.update(paths)
                
                # Scan paths with concurrency control
                semaphore = asyncio.Semaphore(50)  # Limit concurrent requests
                
                tasks = []
                for path in all_paths:
                    if path not in scanned_paths:
                        scanned_paths.add(path)
                        task = self._scan_path(session, semaphore, target, path)
                        tasks.append(task)
                
                # Execute all scans
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        errors.append(f"Scan error: {result}")
                    elif result:
                        findings.append(result)
                
                # Recursive scanning for interesting findings
                if self.recursive_depth > 1:
                    recursive_findings = await self._recursive_scan(
                        session, target, findings, depth=self.recursive_depth-1
                    )
                    findings.extend(recursive_findings)
        
        except Exception as e:
            self.logger.error(f"Path scanner error for {target}: {e}")
            errors.append(str(e))
        
        return {
            "module": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    async def _scan_path(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, 
                        target: str, path: str) -> Optional[Dict[str, Any]]:
        """Scan a single path"""
        async with semaphore:
            try:
                url = urljoin(target.rstrip('/'), path)
                
                async with session.get(url, timeout=10, allow_redirects=False) as response:
                    content = await response.text()
                    
                    # Only report interesting responses
                    if self._is_interesting_response(response, content):
                        content_analysis = self._analyze_content(content)
                        
                        severity = self._calculate_severity(response.status, content_analysis, path)
                        
                        return {
                            'type': 'Path Discovery',
                            'severity': severity,
                            'url': url,
                            'status_code': response.status,
                            'content_length': len(content),
                            'content_type': response.headers.get('Content-Type', ''),
                            'server': response.headers.get('Server', ''),
                            'content_analysis': content_analysis,
                            'path': path,
                            'title': self._extract_title(content),
                            'description': f"Discovered accessible path: {path}"
                        }
            
            except Exception as e:
                self.logger.debug(f"Error scanning {path}: {e}")
                return None
    
    def _is_interesting_response(self, response, content: str) -> bool:
        """Determine if response is interesting enough to report"""
        # Skip common uninteresting responses
        if response.status in [404, 403, 500, 502, 503]:
            return False
        
        # Skip redirect loops
        if response.status in [301, 302, 307, 308] and len(content) < 500:
            return False
        
        # Check for interesting status codes
        if response.status in [200, 401, 500]:
            return True
        
        # Check content for interesting patterns
        if any(self._check_content_patterns(content, patterns) 
               for patterns in self.content_patterns.values()):
            return True
        
        # Check for large content (potential data exposure)
        if len(content) > 10000:
            return True
        
        return False
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for interesting patterns"""
        analysis = {
            'pattern_matches': {},
            'has_forms': bool(re.search(r'<form[^>]*>', content, re.IGNORECASE)),
            'has_inputs': bool(re.search(r'<input[^>]*>', content, re.IGNORECASE)),
            'has_scripts': bool(re.search(r'<script[^>]*>', content, re.IGNORECASE)),
            'potential_secrets': [],
            'technology_stack': []
        }
        
        # Check for pattern matches
        for category, patterns in self.content_patterns.items():
            matches = []
            for pattern in patterns:
                pattern_matches = re.findall(pattern, content, re.IGNORECASE)
                if pattern_matches:
                    matches.extend(pattern_matches)
            if matches:
                analysis['pattern_matches'][category] = matches
        
        # Extract potential secrets
        secret_patterns = [
            r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']',
            r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            r'token["\']?\s*[:=]\s*["\']([a-zA-Z0-9._-]{20,})["\']'
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis['potential_secrets'].extend(matches)
        
        # Detect technology stack
        tech_patterns = {
            'PHP': r'php',
            'ASP.NET': r'asp\.net',
            'Apache': r'apache',
            'Nginx': r'nginx',
            'WordPress': r'wp-content|wordpress',
            'Drupal': r'drupal',
            'Joomla': r'joomla'
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                analysis['technology_stack'].append(tech)
        
        return analysis
    
    def _check_content_patterns(self, content: str, patterns: List[str]) -> bool:
        """Check if content matches any of the given patterns"""
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _calculate_severity(self, status_code: int, content_analysis: Dict[str, Any], path: str) -> str:
        """Calculate finding severity"""
        # Critical conditions
        if 'sensitive_files' in content_analysis['pattern_matches']:
            return 'Critical'
        
        if content_analysis['potential_secrets']:
            return 'Critical'
        
        # High severity conditions
        if status_code == 401:
            return 'High'
        
        if 'admin_panel' in content_analysis['pattern_matches']:
            return 'High'
        
        if 'database_info' in content_analysis['pattern_matches']:
            return 'High'
        
        if any(admin_path in path for admin_path in ['/admin', '/dashboard', '/panel']):
            return 'High'
        
        # Medium severity conditions
        if 'debug_info' in content_analysis['pattern_matches']:
            return 'Medium'
        
        if content_analysis['has_forms'] and '/login' in path:
            return 'Medium'
        
        if 'version_info' in content_analysis['pattern_matches']:
            return 'Medium'
        
        # Low severity (information disclosure)
        return 'Low'
    
    def _extract_title(self, content: str) -> str:
        """Extract page title from HTML content"""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()[:100]  # Limit title length
        return ""
    
    async def _recursive_scan(self, session: aiohttp.ClientSession, target: str, 
                             initial_findings: List[Dict[str, Any]], depth: int) -> List[Dict[str, Any]]:
        """Perform recursive scanning on interesting findings"""
        if depth <= 0:
            return []
        
        recursive_findings = []
        
        # Extract directories from initial findings for recursive scanning
        directories_to_scan = set()
        for finding in initial_findings:
            if finding.get('severity') in ['High', 'Critical']:
                path = finding.get('path', '')
                if path.endswith('/'):
                    directories_to_scan.add(path)
                else:
                    # Add parent directory
                    parent_dir = '/'.join(path.split('/')[:-1]) + '/'
                    if parent_dir != '/':
                        directories_to_scan.add(parent_dir)
        
        # Scan each directory with common subdirectories/files
        common_subdirs = ['uploads/', 'files/', 'backup/', 'config/', 'temp/', 'logs/']
        
        semaphore = asyncio.Semaphore(20)
        tasks = []
        
        for base_dir in directories_to_scan:
            for subdir in common_subdirs:
                recursive_path = base_dir.rstrip('/') + '/' + subdir
                task = self._scan_path(session, semaphore, target, recursive_path)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, dict):
                    result['recursive'] = True
                    result['depth'] = self.recursive_depth - depth + 1
                    recursive_findings.append(result)
        
        return recursive_findings