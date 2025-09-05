from typing import List, Dict, Any
from .base_extractor import BaseExtractor

class AWSExtractor(BaseExtractor):
    """AWS credentials extractor (AKIA*, ASIA*)"""
    
    def _init_patterns(self) -> Dict[str, str]:
        return {
            'access_key': r'(AKIA[0-9A-Z]{16})',
            'secret_key': r'([A-Za-z0-9/+=]{40})',
            'session_token': r'(ASIA[0-9A-Z]{16})',
            'aws_context': r'(aws[_-]?(?:access[_-]?key|secret[_-]?key|session[_-]?token))\s*[:=]\s*["\']?([^"\'\s]+)["\']?'
        }
    
    def extract(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Extract AWS credentials from content"""
        credentials = []
        
        # Extract access keys
        access_keys = self._extract_by_pattern(content, self.patterns['access_key'])
        for key in access_keys:
            if self._validate_length(key, 20, 20):  # AWS access keys are exactly 20 chars
                credentials.append({
                    'type': 'aws_access_key',
                    'service': 'aws',
                    'value': key,
                    'source_url': url,
                    'severity': 'Critical',
                    'description': 'AWS Access Key',
                    'confidence': 0.9
                })
        
        # Extract secret keys (look for them near access keys)
        secret_keys = self._extract_by_pattern(content, self.patterns['secret_key'])
        for secret in secret_keys:
            if self._validate_length(secret, 40, 40) and self._validate_entropy(secret, 4.0):
                credentials.append({
                    'type': 'aws_secret_key',
                    'service': 'aws',
                    'value': secret,
                    'source_url': url,
                    'severity': 'Critical',
                    'description': 'AWS Secret Key',
                    'confidence': 0.8
                })
        
        # Extract session tokens
        session_tokens = self._extract_by_pattern(content, self.patterns['session_token'])
        for token in session_tokens:
            if self._validate_length(token, 20, 20):
                credentials.append({
                    'type': 'aws_session_token',
                    'service': 'aws',
                    'value': token,
                    'source_url': url,
                    'severity': 'High',
                    'description': 'AWS Session Token',
                    'confidence': 0.9
                })
        
        # Extract contextual AWS credentials
        contextual_matches = self._extract_by_pattern(content, self.patterns['aws_context'])
        for match in contextual_matches:
            if isinstance(match, tuple) and len(match) >= 2:
                key_type, value = match[0], match[1]
                if value and self._validate_length(value, 10, 200):
                    credentials.append({
                        'type': f'aws_{key_type.lower().replace("-", "_")}',
                        'service': 'aws',
                        'value': value,
                        'source_url': url,
                        'severity': 'High',
                        'description': f'AWS {key_type.title()}',
                        'confidence': 0.7,
                        'context': key_type
                    })
        
        return credentials