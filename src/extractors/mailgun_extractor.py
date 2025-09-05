from typing import List, Dict, Any
from .base_extractor import BaseExtractor

class MailgunExtractor(BaseExtractor):
    """Mailgun API credentials extractor"""
    
    def _init_patterns(self) -> Dict[str, str]:
        return {
            'api_key': r'key-([a-f0-9]{32})',
            'domain': r'([a-zA-Z0-9.-]+\.mailgun\.org)',
            'mailgun_context': r'(mailgun[_-]?api[_-]?key)\s*[:=]\s*["\']?(key-[a-f0-9]{32})["\']?'
        }
    
    def extract(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Extract Mailgun credentials from content"""
        credentials = []
        
        # Extract API keys
        api_keys = self._extract_by_pattern(content, self.patterns['api_key'])
        for key in api_keys:
            if self._validate_length(key, 36, 36):  # key- prefix + 32 hex chars
                credentials.append({
                    'type': 'mailgun_api_key',
                    'service': 'mailgun',
                    'value': f'key-{key}',
                    'source_url': url,
                    'severity': 'High',
                    'description': 'Mailgun API Key',
                    'confidence': 0.9
                })
        
        # Extract domains
        domains = self._extract_by_pattern(content, self.patterns['domain'])
        for domain in domains:
            if domain.endswith('.mailgun.org'):
                credentials.append({
                    'type': 'mailgun_domain',
                    'service': 'mailgun',
                    'value': domain,
                    'source_url': url,
                    'severity': 'Medium',
                    'description': 'Mailgun Domain',
                    'confidence': 0.8
                })
        
        # Extract contextual Mailgun keys
        contextual_matches = self._extract_by_pattern(content, self.patterns['mailgun_context'])
        for match in contextual_matches:
            if isinstance(match, tuple) and len(match) >= 2:
                context, value = match[0], match[1]
                if value.startswith('key-') and self._validate_length(value, 36, 36):
                    credentials.append({
                        'type': 'mailgun_api_key',
                        'service': 'mailgun',
                        'value': value,
                        'source_url': url,
                        'severity': 'High',
                        'description': 'Mailgun API Key',
                        'confidence': 0.9,
                        'context': context
                    })
        
        return credentials