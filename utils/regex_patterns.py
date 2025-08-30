#!/usr/bin/env python3
"""
Regex Patterns Module
Comprehensive regex patterns for extracting sensitive information
"""

import re
import logging

class RegexPatterns:
    """Comprehensive regex patterns for secret extraction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive regex patterns
        self.patterns = {
            # AWS Keys
            'aws_access_key': [
                r'AKIA[0-9A-Z]{16}',
                r'(?i)aws[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?(AKIA[0-9A-Z]{16})["\']?',
                r'(?i)access[_-]?key[_-]?id["\']?\s*[:=]\s*["\']?(AKIA[0-9A-Z]{16})["\']?'
            ],
            
            'aws_secret_key': [
                r'(?i)aws[_-]?secret[_-]?(?:access[_-]?)?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9+/]{40})["\']?',
                r'(?i)secret[_-]?(?:access[_-]?)?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9+/]{40})["\']?'
            ],
            
            'aws_session_token': [
                r'(?i)aws[_-]?session[_-]?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9+/=]{100,})["\']?'
            ],
            
            # SendGrid
            'sendgrid_api_key': [
                r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
                r'(?i)sendgrid[_-]?(?:api[_-]?)?key["\']?\s*[:=]\s*["\']?(SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43})["\']?'
            ],
            
            # Mailgun
            'mailgun_api_key': [
                r'key-[a-zA-Z0-9]{32}',
                r'(?i)mailgun[_-]?(?:api[_-]?)?key["\']?\s*[:=]\s*["\']?(key-[a-zA-Z0-9]{32})["\']?'
            ],
            
            # Twilio
            'twilio_account_sid': [
                r'AC[a-zA-Z0-9]{32}',
                r'(?i)twilio[_-]?(?:account[_-]?)?sid["\']?\s*[:=]\s*["\']?(AC[a-zA-Z0-9]{32})["\']?'
            ],
            
            'twilio_auth_token': [
                r'(?i)twilio[_-]?(?:auth[_-]?)?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{32})["\']?'
            ],
            
            # Stripe
            'stripe_api_key': [
                r'sk_live_[a-zA-Z0-9]{24,}',
                r'sk_test_[a-zA-Z0-9]{24,}',
                r'pk_live_[a-zA-Z0-9]{24,}',
                r'pk_test_[a-zA-Z0-9]{24,}',
                r'(?i)stripe[_-]?(?:api[_-]?)?key["\']?\s*[:=]\s*["\']?(sk_(?:live|test)_[a-zA-Z0-9]{24,})["\']?'
            ],
            
            # GitHub
            'github_token': [
                r'ghp_[a-zA-Z0-9]{36}',
                r'gho_[a-zA-Z0-9]{36}',
                r'ghu_[a-zA-Z0-9]{36}',
                r'ghs_[a-zA-Z0-9]{36}',
                r'ghr_[a-zA-Z0-9]{36}',
                r'(?i)github[_-]?(?:access[_-]?)?token["\']?\s*[:=]\s*["\']?(gh[a-z]_[a-zA-Z0-9]{36})["\']?'
            ],
            
            # GitLab
            'gitlab_token': [
                r'glpat-[a-zA-Z0-9_-]{20}',
                r'(?i)gitlab[_-]?(?:access[_-]?)?token["\']?\s*[:=]\s*["\']?(glpat-[a-zA-Z0-9_-]{20})["\']?'
            ],
            
            # Slack
            'slack_token': [
                r'xox[a-z]-[a-zA-Z0-9-]+',
                r'(?i)slack[_-]?(?:api[_-]?)?token["\']?\s*[:=]\s*["\']?(xox[a-z]-[a-zA-Z0-9-]+)["\']?'
            ],
            
            'slack_webhook': [
                r'https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+',
                r'(?i)slack[_-]?webhook[_-]?url["\']?\s*[:=]\s*["\']?(https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+)["\']?'
            ],
            
            # Discord
            'discord_token': [
                r'[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_-]{27}',
                r'(?i)discord[_-]?(?:bot[_-]?)?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_-]{27})["\']?'
            ],
            
            'discord_webhook': [
                r'https://discord\.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+',
                r'https://discordapp\.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+'
            ],
            
            # Database URLs
            'database_url': [
                r'mongodb://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[0-9]+/[a-zA-Z0-9_.-]+',
                r'mysql://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[0-9]+/[a-zA-Z0-9_.-]+',
                r'postgresql://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[0-9]+/[a-zA-Z0-9_.-]+',
                r'redis://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[0-9]+/?[a-zA-Z0-9_.-]*'
            ],
            
            # SMTP Credentials
            'smtp_credentials': [
                r'(?i)smtp[_-]?(?:host|server)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9.-]+)["\']?',
                r'(?i)smtp[_-]?(?:user|username)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']?',
                r'(?i)smtp[_-]?(?:pass|password)["\']?\s*[:=]\s*["\']?([^"\'\\s]{8,})["\']?'
            ],
            
            # JWT Tokens
            'jwt_token': [
                r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
                r'(?i)jwt[_-]?token["\']?\s*[:=]\s*["\']?(eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)["\']?'
            ],
            
            # API Keys (Generic)
            'api_key': [
                r'(?i)api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)apikey["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)access[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)secret[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?'
            ],
            
            # Bearer Tokens
            'bearer_token': [
                r'(?i)bearer\s+([a-zA-Z0-9_.-]{20,})',
                r'(?i)authorization:\s*bearer\s+([a-zA-Z0-9_.-]{20,})'
            ],
            
            # Email Addresses
            'email': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ],
            
            # Phone Numbers
            'phone_number': [
                r'\+[1-9]\d{1,14}',
                r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
                r'[0-9]{3}-[0-9]{3}-[0-9]{4}'
            ],
            
            # Internal IP Addresses
            'internal_ip': [
                r'192\.168\.\d{1,3}\.\d{1,3}',
                r'10\.\d{1,3}\.\d{1,3}\.\d{1,3}',
                r'172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}'
            ],
            
            # SSH Private Keys
            'ssh_private_key': [
                r'-----BEGIN (?:RSA )?PRIVATE KEY-----[a-zA-Z0-9+/=\s]+-----END (?:RSA )?PRIVATE KEY-----',
                r'-----BEGIN OPENSSH PRIVATE KEY-----[a-zA-Z0-9+/=\s]+-----END OPENSSH PRIVATE KEY-----'
            ],
            
            # Passwords (Generic)
            'password': [
                r'(?i)password["\']?\s*[:=]\s*["\']?([^"\'\\s]{8,})["\']?',
                r'(?i)passwd["\']?\s*[:=]\s*["\']?([^"\'\\s]{8,})["\']?',
                r'(?i)pwd["\']?\s*[:=]\s*["\']?([^"\'\\s]{8,})["\']?'
            ],
            
            # URLs with credentials
            'url_with_credentials': [
                r'https?://[a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+',
                r'ftp://[a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+'
            ],
            
            # Google Cloud Platform
            'gcp_service_account': [
                r'"type":\s*"service_account"',
                r'"project_id":\s*"([^"]+)"',
                r'"private_key_id":\s*"([^"]+)"',
                r'"private_key":\s*"([^"]+)"'
            ],
            
            # Azure Keys
            'azure_storage_key': [
                r'(?i)(?:azure|storage)[_-]?(?:account[_-]?)?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9+/]{88}==)["\']?'
            ],
            
            # Facebook/Meta
            'facebook_access_token': [
                r'EAA[a-zA-Z0-9]{100,}',
                r'(?i)facebook[_-]?(?:access[_-]?)?token["\']?\s*[:=]\s*["\']?(EAA[a-zA-Z0-9]{100,})["\']?'
            ],
            
            # Twitter/X
            'twitter_api_key': [
                r'(?i)twitter[_-]?(?:api[_-]?)?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{25})["\']?',
                r'(?i)twitter[_-]?(?:api[_-]?)?secret["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{50})["\']?'
            ],
            
            # PayPal
            'paypal_client_id': [
                r'(?i)paypal[_-]?client[_-]?id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{80})["\']?'
            ]
        }
        
    def extract_secrets(self, content):
        """Extract all secrets from content"""
        found_secrets = []
        
        for secret_type, patterns in self.patterns.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for match in matches:
                        if match.groups():
                            # Use the first capture group
                            secret_value = match.group(1)
                        else:
                            # Use the entire match
                            secret_value = match.group(0)
                            
                        # Skip if the secret is too short or too long
                        if len(secret_value) < 8 or len(secret_value) > 500:
                            continue
                            
                        # Create secret object
                        secret = {
                            'type': secret_type,
                            'value': secret_value,
                            'match_start': match.start(),
                            'match_end': match.end(),
                            'pattern_used': pattern
                        }
                        
                        # Add additional context for some secret types
                        if secret_type in ['aws_access_key', 'aws_secret_key']:
                            secret = self._enhance_aws_secret(secret, content, match)
                        elif secret_type == 'smtp_credentials':
                            secret = self._enhance_smtp_secret(secret, content)
                            
                        found_secrets.append(secret)
                        
                except Exception as e:
                    self.logger.debug(f"Error processing pattern {pattern}: {e}")
                    
        # Remove duplicates
        unique_secrets = []
        seen_values = set()
        
        for secret in found_secrets:
            if secret['value'] not in seen_values:
                unique_secrets.append(secret)
                seen_values.add(secret['value'])
                
        return unique_secrets
        
    def _enhance_aws_secret(self, secret, content, match):
        """Enhance AWS secret with additional context"""
        if secret['type'] == 'aws_access_key':
            # Look for corresponding secret key nearby
            access_key = secret['value']
            secret_key_patterns = [
                rf'(?i)secret[_-]?(?:access[_-]?)?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9+/]{{40}})["\']?',
                rf'{re.escape(access_key)}.*?([a-zA-Z0-9+/]{{40}})',
                rf'([a-zA-Z0-9+/]{{40}}).*?{re.escape(access_key)}'
            ]
            
            for pattern in secret_key_patterns:
                secret_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if secret_match:
                    secret['secret_key'] = secret_match.group(1)
                    break
                    
        return secret
        
    def _enhance_smtp_secret(self, secret, content):
        """Enhance SMTP secret with host/username/password context"""
        # This is a simplified version - in practice, you'd want more sophisticated parsing
        return secret
        
    def get_pattern_info(self, secret_type):
        """Get information about patterns for a specific secret type"""
        if secret_type in self.patterns:
            return {
                'type': secret_type,
                'pattern_count': len(self.patterns[secret_type]),
                'patterns': self.patterns[secret_type]
            }
        return None
        
    def add_custom_pattern(self, secret_type, pattern):
        """Add a custom pattern"""
        if secret_type not in self.patterns:
            self.patterns[secret_type] = []
        self.patterns[secret_type].append(pattern)
        self.logger.info(f"Added custom pattern for {secret_type}")
        
    def get_supported_types(self):
        """Get list of all supported secret types"""
        return list(self.patterns.keys())