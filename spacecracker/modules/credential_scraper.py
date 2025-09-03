#!/usr/bin/env python3
"""
SpaceCracker Pro - Credential Scraper Module
Advanced credential and secret extraction with regex patterns and parsers
"""

import asyncio
import aiohttp
import re
import json
import xml.etree.ElementTree as ET
import base64
import logging
import math
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from ..utils.http import create_session
from .base import BaseModule

class CredentialScraper(BaseModule):
    """Advanced credential and secret extraction module"""
    
    module_id = "credential_scraper"
    name = "Credential Scraper"
    description = "Extract credentials, API keys, and sensitive information"
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.secret_patterns = self._init_secret_patterns()
        self.parsers = self._init_parsers()
        self.min_entropy = getattr(config, 'min_entropy', 4.0) if config else 4.0
        self.max_content_size = getattr(config, 'max_content_size', 5 * 1024 * 1024) if config else 5 * 1024 * 1024  # 5MB
    
    def _init_secret_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive secret detection patterns"""
        return {
            # API Keys and Tokens
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'severity': 'Critical',
                'description': 'AWS Access Key ID'
            },
            'aws_secret_key': {
                'pattern': r'[A-Za-z0-9/+=]{40}',
                'context': ['aws_secret_access_key', 'aws_secret', 'secret_access_key'],
                'severity': 'Critical',
                'description': 'AWS Secret Access Key'
            },
            'github_token': {
                'pattern': r'ghp_[a-zA-Z0-9]{36}',
                'severity': 'High',
                'description': 'GitHub Personal Access Token'
            },
            'github_oauth': {
                'pattern': r'gho_[a-zA-Z0-9]{36}',
                'severity': 'High',
                'description': 'GitHub OAuth Token'
            },
            'github_app': {
                'pattern': r'(ghu|ghs)_[a-zA-Z0-9]{36}',
                'severity': 'High',
                'description': 'GitHub App Token'
            },
            'stripe_api_key': {
                'pattern': r'sk_live_[0-9a-zA-Z]{24,}',
                'severity': 'Critical',
                'description': 'Stripe Live API Key'
            },
            'stripe_test_key': {
                'pattern': r'sk_test_[0-9a-zA-Z]{24,}',
                'severity': 'Medium',
                'description': 'Stripe Test API Key'
            },
            'stripe_publishable': {
                'pattern': r'pk_(live|test)_[0-9a-zA-Z]{24,}',
                'severity': 'Low',
                'description': 'Stripe Publishable Key'
            },
            'sendgrid_api_key': {
                'pattern': r'SG\.[a-zA-Z0-9_\-\.]{66}',
                'severity': 'High',
                'description': 'SendGrid API Key'
            },
            'mailgun_api_key': {
                'pattern': r'key-[0-9a-zA-Z]{32}',
                'severity': 'High',
                'description': 'Mailgun API Key'
            },
            'twilio_sid': {
                'pattern': r'AC[0-9a-fA-F]{32}',
                'severity': 'High',
                'description': 'Twilio Account SID'
            },
            'twilio_auth_token': {
                'pattern': r'[0-9a-fA-F]{32}',
                'context': ['auth_token', 'twilio_auth', 'twilio_token'],
                'severity': 'High',
                'description': 'Twilio Auth Token'
            },
            'slack_token': {
                'pattern': r'xox[baprs]-([0-9a-zA-Z]{10,48})',
                'severity': 'High',
                'description': 'Slack Token'
            },
            'discord_webhook': {
                'pattern': r'https://discord(app)?\.com/api/webhooks/[0-9]{18}/[a-zA-Z0-9_-]{68}',
                'severity': 'Medium',
                'description': 'Discord Webhook'
            },
            'discord_bot_token': {
                'pattern': r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}',
                'severity': 'High',
                'description': 'Discord Bot Token'
            },
            
            # JWT Tokens
            'jwt_token': {
                'pattern': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
                'severity': 'Medium',
                'description': 'JWT Token'
            },
            
            # Database Connection Strings
            'mysql_connection': {
                'pattern': r'mysql://[^\s"\']+',
                'severity': 'Critical',
                'description': 'MySQL Connection String'
            },
            'postgresql_connection': {
                'pattern': r'postgres(ql)?://[^\s"\']+',
                'severity': 'Critical',
                'description': 'PostgreSQL Connection String'
            },
            'mongodb_connection': {
                'pattern': r'mongodb://[^\s"\']+',
                'severity': 'Critical',
                'description': 'MongoDB Connection String'
            },
            'redis_connection': {
                'pattern': r'redis://[^\s"\']+',
                'severity': 'High',
                'description': 'Redis Connection String'
            },
            
            # Generic Patterns
            'api_key_generic': {
                'pattern': r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                'severity': 'Medium',
                'description': 'Generic API Key'
            },
            'password_hash': {
                'pattern': r'\$2[ayb]\$[0-9]{2}\$[A-Za-z0-9./]{53}',
                'severity': 'High',
                'description': 'BCrypt Password Hash'
            },
            'md5_hash': {
                'pattern': r'\b[a-fA-F0-9]{32}\b',
                'context': ['password', 'hash', 'md5'],
                'severity': 'Medium',
                'description': 'MD5 Hash'
            },
            'sha1_hash': {
                'pattern': r'\b[a-fA-F0-9]{40}\b',
                'context': ['password', 'hash', 'sha1'],
                'severity': 'Medium',
                'description': 'SHA1 Hash'
            },
            'sha256_hash': {
                'pattern': r'\b[a-fA-F0-9]{64}\b',
                'context': ['password', 'hash', 'sha256'],
                'severity': 'Medium',
                'description': 'SHA256 Hash'
            },
            
            # SSH Keys
            'ssh_private_key': {
                'pattern': r'-----BEGIN (?:RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY-----',
                'severity': 'Critical',
                'description': 'SSH Private Key'
            },
            'ssh_public_key': {
                'pattern': r'ssh-(?:rsa|dss|ed25519) [A-Za-z0-9+/=]+',
                'severity': 'Medium',
                'description': 'SSH Public Key'
            },
            
            # Cloud Provider Keys
            'google_api_key': {
                'pattern': r'AIza[0-9A-Za-z_\-]{35}',
                'severity': 'High',
                'description': 'Google API Key'
            },
            'google_oauth': {
                'pattern': r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
                'severity': 'Medium',
                'description': 'Google OAuth Client ID'
            },
            'azure_storage': {
                'pattern': r'DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]+',
                'severity': 'Critical',
                'description': 'Azure Storage Connection String'
            },
            
            # Generic High-Entropy Strings
            'high_entropy_string': {
                'pattern': r'[a-zA-Z0-9+/=]{32,}',
                'entropy_check': True,
                'severity': 'Low',
                'description': 'High Entropy String'
            },
            
            # Email and Usernames
            'email_addresses': {
                'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'severity': 'Low',
                'description': 'Email Address'
            },
            
            # URLs with credentials
            'url_with_creds': {
                'pattern': r'https?://[a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+',
                'severity': 'High',
                'description': 'URL with embedded credentials'
            }
        }
    
    def _init_parsers(self) -> Dict[str, callable]:
        """Initialize content parsers for different formats"""
        return {
            'json': self._parse_json,
            'xml': self._parse_xml,
            'html': self._parse_html,
            'env': self._parse_env,
            'config': self._parse_config,
            'yaml': self._parse_yaml
        }
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0.0
        
        # Count frequency of each character
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_length = len(text)
        
        for count in char_counts.values():
            probability = count / text_length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run credential scraper against target"""
        findings = []
        errors = []
        
        try:
            async with create_session() as session:
                # Get main content
                async with session.get(target, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_size = len(content)
                        
                        if content_size > self.max_content_size:
                            content = content[:self.max_content_size]
                            self.logger.warning(f"Content truncated for {target} (size: {content_size})")
                        
                        # Extract secrets from content
                        secrets = await self._extract_secrets(content, target, response.headers)
                        
                        for secret in secrets:
                            findings.append({
                                'type': 'Secret Discovery',
                                'severity': secret['severity'],
                                'secret_type': secret['type'],
                                'description': secret['description'],
                                'value': secret['value'],
                                'context': secret.get('context', ''),
                                'confidence': secret.get('confidence', 1.0),
                                'location': secret.get('location', 'content'),
                                'target': target
                            })
                
                # Also check common sensitive file paths
                sensitive_paths = [
                    '/.env', '/.env.local', '/.env.production',
                    '/config.json', '/config.yml', '/settings.json',
                    '/credentials.json', '/auth.json', '/secrets.json',
                    '/wp-config.php', '/configuration.php',
                    '/.aws/credentials', '/.ssh/id_rsa',
                    '/backup.sql', '/dump.sql', '/database.sql'
                ]
                
                for path in sensitive_paths:
                    try:
                        file_url = urljoin(target, path)
                        async with session.get(file_url, timeout=10) as file_response:
                            if file_response.status == 200:
                                file_content = await file_response.text()
                                
                                # Extract secrets from file
                                file_secrets = await self._extract_secrets(
                                    file_content, file_url, file_response.headers
                                )
                                
                                for secret in file_secrets:
                                    secret['location'] = f'file:{path}'
                                    findings.append({
                                        'type': 'Sensitive File',
                                        'severity': 'Critical' if secret['severity'] in ['Critical', 'High'] else secret['severity'],
                                        'secret_type': secret['type'],
                                        'description': f"Sensitive file exposed: {path}",
                                        'value': secret['value'],
                                        'context': secret.get('context', ''),
                                        'confidence': secret.get('confidence', 1.0),
                                        'location': secret['location'],
                                        'file_path': path,
                                        'target': file_url
                                    })
                    
                    except Exception as e:
                        # Silently ignore file access errors
                        continue
        
        except Exception as e:
            self.logger.error(f"Credential scraper error for {target}: {e}")
            errors.append(str(e))
        
        return {
            "module": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    async def _extract_secrets(self, content: str, url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract secrets from content using various methods"""
        secrets = []
        
        # Determine content type for appropriate parsing
        content_type = headers.get('Content-Type', '').lower()
        
        # Parse content based on type
        parsed_data = {}
        if 'json' in content_type:
            parsed_data = self._parse_json(content)
        elif 'xml' in content_type:
            parsed_data = self._parse_xml(content)
        elif 'html' in content_type:
            parsed_data = self._parse_html(content)
        elif url.endswith('.env'):
            parsed_data = self._parse_env(content)
        elif url.endswith(('.yml', '.yaml')):
            parsed_data = self._parse_yaml(content)
        else:
            parsed_data = self._parse_config(content)
        
        # Apply regex patterns to raw content and parsed data
        for pattern_name, pattern_config in self.secret_patterns.items():
            pattern = pattern_config['pattern']
            severity = pattern_config['severity']
            description = pattern_config['description']
            context_keywords = pattern_config.get('context', [])
            entropy_check = pattern_config.get('entropy_check', False)
            
            # Search in raw content
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                matched_text = match.group(1) if match.groups() else match.group(0)
                
                # Skip if entropy check required and string doesn't meet minimum entropy
                if entropy_check and self._calculate_entropy(matched_text) < self.min_entropy:
                    continue
                
                # Check context if required
                confidence = 1.0
                context = ""
                
                if context_keywords:
                    # Look for context keywords around the match
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(content), match.end() + 100)
                    surrounding_text = content[start_pos:end_pos].lower()
                    
                    context_found = any(keyword.lower() in surrounding_text for keyword in context_keywords)
                    if not context_found:
                        confidence *= 0.5  # Reduce confidence without context
                    else:
                        context = surrounding_text.strip()
                
                # Skip low-confidence matches for high-entropy patterns
                if entropy_check and confidence < 0.7:
                    continue
                
                secrets.append({
                    'type': pattern_name,
                    'value': matched_text,
                    'severity': severity,
                    'description': description,
                    'confidence': confidence,
                    'context': context,
                    'location': 'content'
                })
        
        # Extract secrets from parsed structured data
        if parsed_data:
            structured_secrets = self._extract_from_structured_data(parsed_data)
            secrets.extend(structured_secrets)
        
        # Remove duplicates
        unique_secrets = []
        seen_values = set()
        
        for secret in secrets:
            secret_value = secret['value']
            if secret_value not in seen_values:
                seen_values.add(secret_value)
                unique_secrets.append(secret)
        
        return unique_secrets
    
    def _extract_from_structured_data(self, data: Any, path: str = "") -> List[Dict[str, Any]]:
        """Extract secrets from structured data (dict, list)"""
        secrets = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if key suggests sensitive data
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in [
                    'password', 'pass', 'pwd', 'secret', 'token', 'key', 'api',
                    'credential', 'auth', 'private', 'cert', 'signature'
                ]):
                    if isinstance(value, str) and len(value) > 8:
                        severity = self._classify_secret_severity(key_lower, value)
                        secrets.append({
                            'type': f'structured_{key_lower}',
                            'value': value,
                            'severity': severity,
                            'description': f'Sensitive data in structured field: {key}',
                            'confidence': 0.8,
                            'context': f'Field: {current_path}',
                            'location': 'structured_data'
                        })
                
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    nested_secrets = self._extract_from_structured_data(value, current_path)
                    secrets.extend(nested_secrets)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                if isinstance(item, (dict, list)):
                    nested_secrets = self._extract_from_structured_data(item, current_path)
                    secrets.extend(nested_secrets)
        
        return secrets
    
    def _classify_secret_severity(self, field_name: str, value: str) -> str:
        """Classify severity based on field name and value characteristics"""
        field_name = field_name.lower()
        
        # Critical severity keywords
        if any(keyword in field_name for keyword in [
            'private_key', 'secret_key', 'aws_secret', 'database_password',
            'root_password', 'admin_password', 'encryption_key'
        ]):
            return 'Critical'
        
        # High severity keywords
        if any(keyword in field_name for keyword in [
            'api_key', 'auth_token', 'access_token', 'password', 'credential'
        ]):
            return 'High'
        
        # Check value characteristics
        if len(value) > 50 and self._calculate_entropy(value) > 4.5:
            return 'High'
        elif len(value) > 20 and self._calculate_entropy(value) > 3.5:
            return 'Medium'
        
        return 'Low'
    
    # Parser methods
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON content"""
        try:
            return json.loads(content)
        except:
            return {}
    
    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """Parse XML content"""
        try:
            root = ET.fromstring(content)
            return self._xml_to_dict(root)
        except:
            return {}
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            if len(result) == 0:
                return element.text.strip()
            else:
                result['_text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _parse_html(self, content: str) -> Dict[str, Any]:
        """Parse HTML content and extract useful information"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract form data
            forms = []
            for form in soup.find_all('form'):
                form_data = {'action': form.get('action'), 'method': form.get('method'), 'inputs': []}
                for input_elem in form.find_all('input'):
                    form_data['inputs'].append({
                        'name': input_elem.get('name'),
                        'type': input_elem.get('type'),
                        'value': input_elem.get('value')
                    })
                forms.append(form_data)
            
            # Extract meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                if name:
                    meta_tags[name] = meta.get('content')
            
            # Extract script content
            scripts = []
            for script in soup.find_all('script'):
                if script.string:
                    scripts.append(script.string)
            
            return {
                'forms': forms,
                'meta_tags': meta_tags,
                'scripts': scripts,
                'title': soup.title.string if soup.title else ''
            }
        except:
            return {}
    
    def _parse_env(self, content: str) -> Dict[str, Any]:
        """Parse .env file format"""
        result = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip().strip('"\'')
        return result
    
    def _parse_config(self, content: str) -> Dict[str, Any]:
        """Parse generic configuration file format"""
        result = {}
        
        # Try to parse as key=value pairs
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                try:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip().strip('"\'')
                except:
                    continue
        
        return result
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Parse YAML content"""
        try:
            import yaml
            return yaml.safe_load(content) or {}
        except:
            return {}