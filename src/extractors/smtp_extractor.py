from typing import List, Dict, Any
from .base_extractor import BaseExtractor

class SMTPExtractor(BaseExtractor):
    """SMTP credentials extractor"""
    
    def _init_patterns(self) -> Dict[str, str]:
        return {
            'smtp_url': r'smtp://([^:\s]+):([^@\s]+)@([^:\s]+)(?::(\d+))?',
            'smtp_config': r'(smtp[_-]?(?:host|server|user|pass|username|password))\s*[:=]\s*["\']?([^"\'>\s]+)["\']?',
            'email_auth': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*[:]\s*([^\s]+)'
        }
    
    def extract(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Extract SMTP credentials from content"""
        credentials = []
        
        # Extract SMTP URLs
        smtp_urls = self._extract_by_pattern(content, self.patterns['smtp_url'])
        for match in smtp_urls:
            if isinstance(match, tuple) and len(match) >= 3:
                username, password, host = match[0], match[1], match[2]
                port = match[3] if len(match) > 3 else '587'
                
                credentials.append({
                    'type': 'smtp_credentials',
                    'service': 'smtp',
                    'value': {
                        'username': username,
                        'password': password,
                        'host': host,
                        'port': port
                    },
                    'source_url': url,
                    'severity': 'High',
                    'description': 'SMTP Credentials',
                    'confidence': 0.9
                })
        
        # Extract SMTP configuration
        smtp_configs = self._extract_by_pattern(content, self.patterns['smtp_config'])
        for match in smtp_configs:
            if isinstance(match, tuple) and len(match) >= 2:
                config_type, value = match[0], match[1]
                if self._validate_length(value, 3, 100):
                    credentials.append({
                        'type': f'smtp_{config_type.lower().replace("-", "_")}',
                        'service': 'smtp',
                        'value': value,
                        'source_url': url,
                        'severity': 'Medium',
                        'description': f'SMTP {config_type.title()}',
                        'confidence': 0.7,
                        'context': config_type
                    })
        
        # Extract email:password combinations
        email_auths = self._extract_by_pattern(content, self.patterns['email_auth'])
        for match in email_auths:
            if isinstance(match, tuple) and len(match) >= 2:
                email, password = match[0], match[1]
                if self._validate_length(password, 6, 50):
                    credentials.append({
                        'type': 'email_credentials',
                        'service': 'smtp',
                        'value': {
                            'email': email,
                            'password': password
                        },
                        'source_url': url,
                        'severity': 'High',
                        'description': 'Email Credentials',
                        'confidence': 0.8
                    })
        
        return credentials