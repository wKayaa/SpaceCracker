#!/usr/bin/env python3
"""
SpaceCracker Scanner Base Module
Core scanning functionality with modular exploit support
"""

import asyncio
import aiohttp
import time
import random
import logging
from urllib.parse import urljoin, urlparse
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor

from modules.ggb_scanner import GGBScanner
from modules.js_scanner import JSScanner
from modules.git_scanner import GitScanner
from modules.cve_exploits import CVEExploits
from modules.validators import SecretValidator
from utils.regex_patterns import RegexPatterns
from utils.rate_limiter import RateLimiter

class SpaceCracker:
    """Main scanner class coordinating all modules"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            rate=config['scanner']['rate_limit'],
            max_tokens=config['scanner']['threads'] * 2
        )
        
        # Initialize modules based on configuration
        self.modules = {}
        if config['modules'].get('ggb_scanner'):
            self.modules['ggb'] = GGBScanner(config)
        if config['modules'].get('js_scanner'):
            self.modules['js'] = JSScanner(config)
        if config['modules'].get('git_scanner'):
            self.modules['git'] = GitScanner(config)
        if config['modules'].get('cve_exploits'):
            self.modules['cve'] = CVEExploits(config)
            
        # Initialize validators
        self.validator = SecretValidator(config)
        
        # Initialize regex patterns
        self.regex_patterns = RegexPatterns()
        
        # Load default paths
        self.vulnerable_paths = self._load_default_paths()
        
        # Session configuration
        self.session_config = {
            'timeout': aiohttp.ClientTimeout(total=config['scanner']['timeout']),
            'headers': {
                'User-Agent': config['scanner']['user_agent']
            },
            'connector': aiohttp.TCPConnector(
                limit=config['scanner']['threads'],
                limit_per_host=5
            )
        }
        
    def _load_default_paths(self):
        """Load default vulnerable paths"""
        default_paths = [
            # Storage/Cloud endpoints
            '/storage/',
            '/s3/',
            '/minio/',
            '/uploads/',
            '/backup/',
            '/backups/',
            '/dump/',
            '/data/',
            
            # Config files
            '/config.php',
            '/config.json',
            '/config.yml',
            '/config.yaml',
            '/.env',
            '/configuration.php',
            '/settings.php',
            '/app.config',
            '/web.config',
            
            # Debug/Development
            '/debug/',
            '/dev/',
            '/test/',
            '/staging/',
            '/phpinfo.php',
            '/info.php',
            '/server-info',
            '/server-status',
            
            # API endpoints
            '/api/',
            '/v1/',
            '/v2/',
            '/api/v1/',
            '/api/v2/',
            '/graphql',
            '/swagger',
            '/docs/',
            
            # Git/Version control
            '/.git/',
            '/.git/config',
            '/.git/HEAD',
            '/.svn/',
            '/.hg/',
            
            # Database dumps
            '/db/',
            '/database/',
            '/sql/',
            '/mysql/',
            '/backup.sql',
            '/dump.sql',
            '/db.sql',
            
            # Log files
            '/logs/',
            '/log/',
            '/access.log',
            '/error.log',
            '/debug.log',
            '/application.log'
        ]
        return default_paths
        
    def load_custom_paths(self, paths_file):
        """Load custom paths from file"""
        try:
            with open(paths_file, 'r') as f:
                custom_paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            self.vulnerable_paths.extend(custom_paths)
            self.logger.info(f"Loaded {len(custom_paths)} custom paths")
        except Exception as e:
            self.logger.error(f"Failed to load custom paths: {e}")
            
    async def scan_targets(self, targets):
        """Main scanning function"""
        results = []
        
        async with aiohttp.ClientSession(**self.session_config) as session:
            # Create semaphore for controlling concurrency
            semaphore = asyncio.Semaphore(self.config['scanner']['threads'])
            
            # Create tasks for all targets
            tasks = []
            for target in targets:
                task = self._scan_single_target(session, semaphore, target)
                tasks.append(task)
            
            # Execute all tasks
            target_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for target, result in zip(targets, target_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error scanning {target}: {result}")
                elif result:
                    results.extend(result)
                    
        return results
        
    async def _scan_single_target(self, session, semaphore, target):
        """Scan a single target with all modules"""
        async with semaphore:
            results = []
            
            try:
                # Apply rate limiting
                await self.rate_limiter.acquire()
                
                self.logger.info(f"Scanning: {target}")
                
                # Test base URL first
                base_result = await self._test_url(session, target)
                if base_result:
                    results.append(base_result)
                
                # Test all vulnerable paths
                path_tasks = []
                for path in self.vulnerable_paths:
                    url = urljoin(target, path)
                    task = self._test_url_with_modules(session, url, target)
                    path_tasks.append(task)
                
                # Execute path tests with internal rate limiting
                path_results = await asyncio.gather(*path_tasks, return_exceptions=True)
                
                # Process path results
                for result in path_results:
                    if isinstance(result, list):
                        results.extend(result)
                    elif result:
                        results.append(result)
                        
                # Run module-specific scans
                for module_name, module in self.modules.items():
                    try:
                        module_results = await module.scan(session, target)
                        if module_results:
                            results.extend(module_results)
                    except Exception as e:
                        self.logger.error(f"Module {module_name} failed for {target}: {e}")
                        
            except Exception as e:
                self.logger.error(f"Failed to scan {target}: {e}")
                
            return results
            
    async def _test_url_with_modules(self, session, url, base_target):
        """Test URL and apply all analysis modules"""
        results = []
        
        try:
            # Apply rate limiting for each request
            await self.rate_limiter.acquire()
            
            # Random delay for OpSec
            delay = random.uniform(
                self.config['scanner']['random_delay_min'],
                self.config['scanner']['random_delay_max']
            )
            await asyncio.sleep(delay)
            
            # Test the URL
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Basic result
                    result = {
                        'url': url,
                        'base_target': base_target,
                        'status': response.status,
                        'content_length': len(content),
                        'headers': dict(response.headers),
                        'timestamp': time.time()
                    }
                    
                    # Extract secrets using regex
                    secrets = self.regex_patterns.extract_secrets(content)
                    if secrets:
                        result['secrets'] = secrets
                        
                        # Validate secrets
                        validated_secrets = []
                        for secret in secrets:
                            validation_result = await self.validator.validate_secret(secret)
                            if validation_result['valid']:
                                validated_secrets.append(validation_result)
                                
                        if validated_secrets:
                            result['validated_secrets'] = validated_secrets
                            result['validated'] = True
                            
                    results.append(result)
                    
        except asyncio.TimeoutError:
            self.logger.debug(f"Timeout for {url}")
        except Exception as e:
            self.logger.debug(f"Error testing {url}: {e}")
            
        return results
        
    async def _test_url(self, session, url):
        """Basic URL test"""
        try:
            await self.rate_limiter.acquire()
            
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return {
                        'url': url,
                        'status': response.status,
                        'content_length': len(content),
                        'headers': dict(response.headers),
                        'timestamp': time.time()
                    }
        except Exception as e:
            self.logger.debug(f"Error testing base URL {url}: {e}")
            
        return None