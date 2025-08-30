#!/usr/bin/env python3
"""
GGB Scanner Module
Scans for Google Cloud Storage buckets and other cloud storage exposures
"""

import asyncio
import aiohttp
import logging
import json
import re
from urllib.parse import urljoin, urlparse

class GGBScanner:
    """Google Cloud Storage and general bucket scanner"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # GCS and cloud storage patterns
        self.bucket_patterns = [
            # Google Cloud Storage
            r'https://storage\.googleapis\.com/([a-zA-Z0-9\-_\.]+)',
            r'https://([a-zA-Z0-9\-_\.]+)\.storage\.googleapis\.com',
            r'gs://([a-zA-Z0-9\-_\.]+)',
            
            # Amazon S3
            r'https://([a-zA-Z0-9\-_\.]+)\.s3\.amazonaws\.com',
            r'https://s3\.amazonaws\.com/([a-zA-Z0-9\-_\.]+)',
            r's3://([a-zA-Z0-9\-_\.]+)',
            
            # Azure Blob Storage
            r'https://([a-zA-Z0-9\-_\.]+)\.blob\.core\.windows\.net',
            
            # MinIO and other S3-compatible
            r'https://([a-zA-Z0-9\-_\.]+)/minio',
            r'minio://([a-zA-Z0-9\-_\.]+)'
        ]
        
        # Storage-related paths to test
        self.storage_paths = [
            '/storage/',
            '/buckets/',
            '/s3/',
            '/gcs/',
            '/azure/',
            '/minio/',
            '/upload/',
            '/uploads/',
            '/files/',
            '/assets/',
            '/media/',
            '/static/',
            '/public/',
            '/private/',
            '/backup/',
            '/backups/',
            '/dump/',
            '/exports/',
            '/data/'
        ]
        
    async def scan(self, session, target):
        """Main scanning function for GGB"""
        results = []
        
        try:
            # Test storage paths
            for path in self.storage_paths:
                storage_url = urljoin(target, path)
                result = await self._test_storage_endpoint(session, storage_url, target)
                if result:
                    results.append(result)
                    
            # Look for bucket references in main page
            main_page_buckets = await self._scan_for_bucket_references(session, target)
            if main_page_buckets:
                results.extend(main_page_buckets)
                
            # Test common bucket name variations
            bucket_results = await self._test_bucket_variations(session, target)
            if bucket_results:
                results.extend(bucket_results)
                
        except Exception as e:
            self.logger.error(f"GGB Scanner error for {target}: {e}")
            
        return results
        
    async def _test_storage_endpoint(self, session, url, base_target):
        """Test a storage endpoint for accessibility"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for storage indicators
                    storage_indicators = [
                        '<ListBucketResult',  # S3/MinIO XML response
                        '"kind": "storage#',  # GCS JSON response
                        'bucket',
                        'storage',
                        'amazonaws',
                        'googleapis',
                        'blob.core.windows.net'
                    ]
                    
                    content_lower = content.lower()
                    found_indicators = [ind for ind in storage_indicators if ind in content_lower]
                    
                    if found_indicators:
                        # Extract file listings if present
                        files = self._extract_file_listings(content)
                        
                        result = {
                            'module': 'ggb_scanner',
                            'type': 'storage_exposure',
                            'url': url,
                            'base_target': base_target,
                            'status': response.status,
                            'indicators': found_indicators,
                            'content_length': len(content),
                            'headers': dict(response.headers),
                            'severity': 'high' if files else 'medium'
                        }
                        
                        if files:
                            result['files'] = files[:50]  # Limit to first 50 files
                            result['file_count'] = len(files)
                            
                        return result
                        
                elif response.status == 403:
                    # Bucket exists but access denied - still worth noting
                    return {
                        'module': 'ggb_scanner',
                        'type': 'storage_access_denied',
                        'url': url,
                        'base_target': base_target,
                        'status': response.status,
                        'severity': 'low',
                        'note': 'Storage endpoint exists but access denied'
                    }
                    
        except Exception as e:
            self.logger.debug(f"Error testing storage endpoint {url}: {e}")
            
        return None
        
    async def _scan_for_bucket_references(self, session, target):
        """Scan main page for bucket/storage references"""
        results = []
        
        try:
            async with session.get(target) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Find bucket references
                    all_buckets = set()
                    
                    for pattern in self.bucket_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            bucket_name = match.group(1)
                            all_buckets.add(bucket_name)
                            
                    if all_buckets:
                        # Test each found bucket
                        for bucket in all_buckets:
                            bucket_results = await self._test_specific_bucket(session, bucket, target)
                            if bucket_results:
                                results.extend(bucket_results)
                                
        except Exception as e:
            self.logger.debug(f"Error scanning for bucket references in {target}: {e}")
            
        return results
        
    async def _test_bucket_variations(self, session, target):
        """Test common bucket naming patterns based on domain"""
        results = []
        
        try:
            # Extract domain components
            parsed = urlparse(target)
            domain = parsed.netloc.lower()
            domain_parts = domain.replace('www.', '').split('.')
            
            # Generate potential bucket names
            bucket_candidates = []
            
            if domain_parts:
                base_name = domain_parts[0]
                bucket_candidates.extend([
                    base_name,
                    f"{base_name}-backup",
                    f"{base_name}-backups",
                    f"{base_name}-data",
                    f"{base_name}-files",
                    f"{base_name}-uploads",
                    f"{base_name}-assets",
                    f"{base_name}-static",
                    f"{base_name}-media",
                    f"{base_name}-prod",
                    f"{base_name}-production",
                    f"{base_name}-dev",
                    f"{base_name}-development",
                    f"{base_name}-staging",
                    f"{base_name}-test"
                ])
                
            # Test each candidate
            for bucket_name in bucket_candidates[:10]:  # Limit to avoid too many requests
                bucket_results = await self._test_specific_bucket(session, bucket_name, target)
                if bucket_results:
                    results.extend(bucket_results)
                    
        except Exception as e:
            self.logger.debug(f"Error testing bucket variations for {target}: {e}")
            
        return results
        
    async def _test_specific_bucket(self, session, bucket_name, base_target):
        """Test specific bucket across different cloud providers"""
        results = []
        
        # Test URLs for different cloud providers
        test_urls = [
            f"https://{bucket_name}.s3.amazonaws.com/",
            f"https://s3.amazonaws.com/{bucket_name}/",
            f"https://{bucket_name}.storage.googleapis.com/",
            f"https://storage.googleapis.com/{bucket_name}/",
            f"https://{bucket_name}.blob.core.windows.net/"
        ]
        
        for url in test_urls:
            try:
                async with session.get(url) as response:
                    if response.status in [200, 403]:
                        result = {
                            'module': 'ggb_scanner',
                            'type': 'bucket_found',
                            'bucket_name': bucket_name,
                            'bucket_url': url,
                            'base_target': base_target,
                            'status': response.status,
                            'accessible': response.status == 200,
                            'cloud_provider': self._identify_provider(url),
                            'severity': 'high' if response.status == 200 else 'medium'
                        }
                        
                        if response.status == 200:
                            content = await response.text()
                            files = self._extract_file_listings(content)
                            if files:
                                result['files'] = files[:20]
                                result['file_count'] = len(files)
                                
                        results.append(result)
                        break  # Found the bucket, no need to test other URLs
                        
            except Exception as e:
                self.logger.debug(f"Error testing bucket {url}: {e}")
                
        return results
        
    def _identify_provider(self, url):
        """Identify cloud storage provider from URL"""
        if 'amazonaws.com' in url:
            return 'AWS S3'
        elif 'googleapis.com' in url:
            return 'Google Cloud Storage'
        elif 'blob.core.windows.net' in url:
            return 'Azure Blob Storage'
        else:
            return 'Unknown'
            
    def _extract_file_listings(self, content):
        """Extract file listings from storage responses"""
        files = []
        
        try:
            # Try XML format (S3/MinIO)
            xml_pattern = r'<Key>([^<]+)</Key>'
            xml_matches = re.findall(xml_pattern, content)
            files.extend(xml_matches)
            
            # Try JSON format (GCS)
            if 'items' in content.lower():
                import json
                try:
                    data = json.loads(content)
                    if 'items' in data:
                        for item in data['items']:
                            if 'name' in item:
                                files.append(item['name'])
                except:
                    pass
                    
            # Try HTML listings
            html_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
            html_matches = re.findall(html_pattern, content)
            for href, text in html_matches:
                if not href.startswith(('http', '#', 'javascript')):
                    files.append(href)
                    
        except Exception as e:
            self.logger.debug(f"Error extracting file listings: {e}")
            
        return list(set(files))  # Remove duplicates