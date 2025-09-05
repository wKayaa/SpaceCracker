from typing import List, Dict, Any
from .base_extractor import BaseExtractor

class SendGridExtractor(BaseExtractor):
    """SendGrid API keys extractor (SG.*)"""
    
    def _init_patterns(self) -> Dict[str, str]:
        return {
            'api_key': r'(SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43})',
            'sendgrid_context': r'(sendgrid[_-]?api[_-]?key)\s*[:=]\s*["\']?(SG\.[^"\'>\s]+)["\']?'
        }
    
    def extract(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Extract SendGrid API keys from content"""
        credentials = []
        
        # Extract SendGrid API keys
        api_keys = self._extract_by_pattern(content, self.patterns['api_key'])
        for key in api_keys:
            if key.startswith('SG.') and self._validate_length(key, 60, 80):
                credentials.append({
                    'type': 'sendgrid_api_key',
                    'service': 'sendgrid',
                    'value': key,
                    'source_url': url,
                    'severity': 'Critical',
                    'description': 'SendGrid API Key',
                    'confidence': 0.95
                })
        
        # Extract contextual SendGrid keys
        contextual_matches = self._extract_by_pattern(content, self.patterns['sendgrid_context'])
        for match in contextual_matches:
            if isinstance(match, tuple) and len(match) >= 2:
                context, value = match[0], match[1]
                if value.startswith('SG.') and self._validate_length(value, 60, 80):
                    credentials.append({
                        'type': 'sendgrid_api_key',
                        'service': 'sendgrid',
                        'value': value,
                        'source_url': url,
                        'severity': 'Critical',
                        'description': 'SendGrid API Key',
                        'confidence': 0.9,
                        'context': context
                    })
        
        return credentials