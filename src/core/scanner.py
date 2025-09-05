import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import ssl
import time

class Scanner:
    def __init__(self, stats_manager):
        self.stats = stats_manager
        self.session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        self.semaphore = asyncio.Semaphore(5000)  # Max 5000 concurrent
        
    async def initialize(self):
        """Initialize aiohttp session with connection pooling"""
        timeout = aiohttp.ClientTimeout(total=self.stats.stats['timeout'])
        
        # Create SSL context that allows unverified certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.connector = aiohttp.TCPConnector(
            limit=5000,
            limit_per_host=30,
            ttl_dns_cache=300,
            ssl=ssl_context
        )
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
    
    async def scan_url(self, url: str, paths: List[str]) -> List[Dict]:
        """Scan URL with all paths"""
        results = []
        
        # Update current target
        self.stats.update_stats(current_target=url)
        
        async with self.semaphore:
            for path in paths:
                target = f"{url.rstrip('/')}/{path.lstrip('/')}"
                
                try:
                    async with self.session.get(target) as response:
                        if response.status == 200:
                            content = await response.text()
                            # Extract credentials from content
                            credentials = await self.extract_credentials(content, target)
                            if credentials:
                                crack_id = self.stats.get_crack_id()
                                result = {
                                    'crack_id': crack_id,
                                    'url': target,
                                    'credentials': credentials,
                                    'response_time': response.headers.get('X-Response-Time', '0'),
                                    'timestamp': time.time()
                                }
                                results.append(result)
                                self.stats.update_stats(hits=1)
                        
                        self.stats.update_stats(checked_paths=1)
                        
                except asyncio.TimeoutError:
                    self.stats.update_stats(invalid_urls=1)
                except Exception as e:
                    # Log error but continue
                    pass
                
        self.stats.update_stats(checked_urls=1)
        return results
    
    async def extract_credentials(self, content: str, url: str) -> List[Dict]:
        """Extract credentials from content using all extractors"""
        # This will be implemented with proper extractors
        credentials = []
        
        # Basic patterns for now - will be replaced with proper extractors
        aws_patterns = [
            r'AKIA[0-9A-Z]{16}',  # AWS Access Key
            r'[A-Za-z0-9/+=]{40}'  # AWS Secret Key (basic pattern)
        ]
        
        # Simple pattern matching for demonstration
        import re
        for pattern in aws_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match:
                    credentials.append({
                        'type': 'aws',
                        'value': match,
                        'source_url': url,
                        'severity': 'high'
                    })
        
        return credentials
    
    async def scan_multiple_urls(self, urls: List[str], paths: List[str]) -> List[Dict]:
        """Scan multiple URLs concurrently"""
        tasks = []
        
        # Set total URLs for progress tracking
        self.stats.update_stats(max_urls=len(urls))
        
        for url in urls:
            task = self.scan_url(url, paths)
            tasks.append(task)
        
        # Process in batches to avoid overwhelming the system
        batch_size = 100
        all_results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, list):
                    all_results.extend(result)
                elif isinstance(result, Exception):
                    # Log exception but continue
                    pass
        
        return all_results