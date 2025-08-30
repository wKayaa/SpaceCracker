from .base import BaseModule
import requests
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List

class GGBScanner(BaseModule):
    module_id = "ggb_scanner"
    name = "Generic Global Bucket Scanner"
    description = "Detect exposed generic/global storage buckets (passive)."
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
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
        ]
        
        self.storage_paths = [
            '/storage/', '/buckets/', '/s3/', '/uploads/', '/backup/'
        ]
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run GGB scanner against target"""
        findings = []
        errors = []
        
        try:
            # Test storage paths
            for path in self.storage_paths:
                url = urljoin(target, path)
                try:
                    response = requests.get(url, timeout=10, allow_redirects=False)
                    
                    if response.status_code in [200, 403, 404]:
                        # Look for bucket indicators in response
                        if self._check_bucket_indicators(response.text, response.headers):
                            findings.append({
                                "id": f"ggb_storage_exposure_{path.strip('/')}",
                                "title": f"Potential Storage Bucket Exposure: {path}",
                                "severity": "Medium",
                                "category": "exposure",
                                "confidence": 0.7,
                                "description": f"Storage endpoint {path} returned indicators of bucket exposure",
                                "evidence": {
                                    "url": url,
                                    "status_code": response.status_code,
                                    "headers": dict(response.headers),
                                    "content_snippet": response.text[:200]
                                },
                                "recommendation": "Review storage bucket permissions and access controls"
                            })
                except Exception as e:
                    errors.append(f"Failed to test {url}: {str(e)}")
                    
            # Scan page content for bucket references
            try:
                response = requests.get(target, timeout=10)
                bucket_refs = self._find_bucket_references(response.text)
                
                for bucket_ref in bucket_refs:
                    findings.append({
                        "id": f"ggb_bucket_reference_{hash(bucket_ref)}",
                        "title": "Bucket Reference Found",
                        "severity": "Low",
                        "category": "exposure", 
                        "confidence": 0.6,
                        "description": f"Found reference to storage bucket: {bucket_ref}",
                        "evidence": {
                            "bucket_url": bucket_ref,
                            "source_url": target
                        },
                        "recommendation": "Verify bucket permissions and access controls"
                    })
                    
            except Exception as e:
                errors.append(f"Failed to scan page content: {str(e)}")
                
        except Exception as e:
            errors.append(f"Module execution failed: {str(e)}")
        
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _check_bucket_indicators(self, content: str, headers: dict) -> bool:
        """Check if response indicates bucket exposure"""
        indicators = [
            'bucketlisting',
            'listbucketresult',
            'contents>',
            'bucket>',
            'storage.googleapis.com',
            's3.amazonaws.com',
            'blob.core.windows.net'
        ]
        
        content_lower = content.lower()
        for indicator in indicators:
            if indicator in content_lower:
                return True
                
        # Check headers for bucket indicators
        server = headers.get('server', '').lower()
        if any(s in server for s in ['amazon', 'google', 'azure', 'minio']):
            return True
            
        return False
    
    def _find_bucket_references(self, content: str) -> List[str]:
        """Find bucket references in content"""
        bucket_refs = []
        for pattern in self.bucket_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            bucket_refs.extend(matches)
        
        return list(set(bucket_refs))  # Remove duplicates