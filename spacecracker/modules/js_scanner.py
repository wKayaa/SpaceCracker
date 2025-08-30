import re
import requests
from .base import BaseModule
from typing import Dict, Any, List
from urllib.parse import urljoin

class JSScanner(BaseModule):
    module_id = "js_scanner" 
    name = "JavaScript Scanner"
    description = "Scan JavaScript files for secrets and sensitive information."
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        self.js_patterns = {
            'api_keys': [
                r'api[_-]?key["\']?\s*[:=]\s*["\']([\w\-]{20,})["\']]',
                r'key["\']?\s*[:=]\s*["\']([\w\-]{20,})["\']',
            ],
            'aws_keys': [
                r'AKIA[0-9A-Z]{16}',
                r'aws[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([\w\-]+)["\']',
            ],
            'tokens': [
                r'token["\']?\s*[:=]\s*["\']([\w\-\.]{20,})["\']',
                r'bearer["\']?\s*[:=]\s*["\']([\w\-\.]{20,})["\']',
            ],
            'endpoints': [
                r'https?://[^\s"\'<>]+',
            ]
        }
        
        self.js_extensions = ['.js', '.min.js', '.jsx']
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run JS scanner against target"""
        findings = []
        errors = []
        
        try:
            # First, get the main page to find JS files
            response = requests.get(target, timeout=10)
            js_files = self._find_js_files(response.text, target)
            
            # Scan each JavaScript file
            for js_url in js_files[:10]:  # Limit to first 10 JS files
                try:
                    js_response = requests.get(js_url, timeout=10)
                    if js_response.status_code == 200:
                        secrets = self._scan_js_content(js_response.text)
                        
                        if secrets:
                            # Calculate severity based on findings
                            severity = "Low"
                            if any(key in secrets for key in ['api_keys', 'aws_keys', 'tokens']):
                                severity = "High"
                            elif secrets.get('endpoints'):
                                severity = "Medium"
                                
                            findings.append({
                                "id": f"js_secrets_{hash(js_url)}",
                                "title": "Secrets Found in JavaScript",
                                "severity": severity,
                                "category": "secret",
                                "confidence": 0.8,
                                "description": f"Found {sum(len(v) for v in secrets.values())} potential secrets in JavaScript file",
                                "evidence": {
                                    "js_url": js_url,
                                    "secrets": secrets,
                                    "file_size": len(js_response.text)
                                },
                                "recommendation": "Review JavaScript files and remove hardcoded secrets"
                            })
                            
                except Exception as e:
                    errors.append(f"Failed to scan {js_url}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Failed to get main page: {str(e)}")
        
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _find_js_files(self, html_content: str, base_url: str) -> List[str]:
        """Find JavaScript file URLs in HTML content"""
        js_files = []
        
        # Find script tags with src attributes
        script_pattern = r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(script_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            if any(match.endswith(ext) for ext in self.js_extensions):
                # Convert relative URLs to absolute
                if match.startswith('http'):
                    js_files.append(match)
                else:
                    js_files.append(urljoin(base_url, match))
        
        return js_files
    
    def _scan_js_content(self, content: str) -> Dict[str, List[str]]:
        """Scan JavaScript content for secrets"""
        found_secrets = {}
        
        for category, patterns in self.js_patterns.items():
            category_findings = []
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                # Filter and validate matches
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]
                    
                    # Basic filtering to reduce false positives
                    if len(match) > 10 and not any(x in match.lower() for x in ['example', 'test', 'placeholder']):
                        category_findings.append(match)
            
            if category_findings:
                found_secrets[category] = list(set(category_findings))  # Remove duplicates
        
        return found_secrets