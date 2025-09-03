#!/usr/bin/env python3
"""
SMTP API Checker
Validate SMTP credentials and email service configurations
"""

import re
import smtplib
import ssl
import asyncio
from typing import Dict, Any, List
from email.mime.text import MIMEText
from .base import BaseAPIChecker, ValidationResult

class SMTPChecker(BaseAPIChecker):
    """SMTP credential validator"""
    
    @property
    def service_name(self) -> str:
        return "SMTP"
    
    @property
    def supported_credential_types(self) -> List[str]:
        return ["smtp_credentials", "email_config"]
    
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        """Extract SMTP credentials from content"""
        credentials = []
        
        # SMTP URL pattern
        smtp_url_pattern = r'smtp://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?'
        matches = re.finditer(smtp_url_pattern, content, re.IGNORECASE)
        
        for match in matches:
            username, password, server, port = match.groups()
            credentials.append({
                'type': 'smtp_url',
                'username': username,
                'password': password,
                'server': server,
                'port': port or '587',
                'raw': match.group(0)
            })
        
        # Configuration pattern
        config_patterns = [
            (r'smtp[_-]?server["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'server'),
            (r'smtp[_-]?port["\']?\s*[:=]\s*["\']?(\d+)["\']?', 'port'),
            (r'smtp[_-]?user(?:name)?["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'username'),
            (r'smtp[_-]?pass(?:word)?["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'password'),
            (r'mail[_-]?host["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'server'),
            (r'mail[_-]?port["\']?\s*[:=]\s*["\']?(\d+)["\']?', 'port'),
            (r'mail[_-]?user(?:name)?["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'username'),
            (r'mail[_-]?pass(?:word)?["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'password')
        ]
        
        smtp_config = {}
        for pattern, key in config_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                smtp_config[key] = match.group(1)
        
        if len(smtp_config) >= 3:  # At least server, username, password
            smtp_config['type'] = 'smtp_config'
            credentials.append(smtp_config)
        
        return credentials
    
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        """Validate SMTP credential"""
        try:
            # Parse credential
            if isinstance(credential, str):
                # Try to parse as SMTP URL
                smtp_url_match = re.match(r'smtp://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?', credential)
                if smtp_url_match:
                    username, password, server, port = smtp_url_match.groups()
                    config = {
                        'server': server,
                        'port': int(port) if port else 587,
                        'username': username,
                        'password': password
                    }
                else:
                    return ValidationResult(
                        service=self.service_name,
                        credential_type=credential_type or 'unknown',
                        is_valid=False,
                        confidence=0.0,
                        details={'error': 'Invalid credential format'},
                        error="Could not parse SMTP credential"
                    )
            elif isinstance(credential, dict):
                config = credential
            else:
                return ValidationResult(
                    service=self.service_name,
                    credential_type=credential_type or 'unknown',
                    is_valid=False,
                    confidence=0.0,
                    details={'error': 'Invalid credential type'},
                    error="Credential must be string or dict"
                )
            
            # Validate required fields
            required_fields = ['server', 'username', 'password']
            for field in required_fields:
                if field not in config:
                    return ValidationResult(
                        service=self.service_name,
                        credential_type=credential_type or 'smtp_config',
                        is_valid=False,
                        confidence=0.0,
                        details={'error': f'Missing required field: {field}'},
                        error=f"Missing required field: {field}"
                    )
            
            # Test SMTP connection
            result = await self._test_smtp_connection(config)
            
            return ValidationResult(
                service=self.service_name,
                credential_type=credential_type or 'smtp_config',
                is_valid=result['valid'],
                confidence=result['confidence'],
                details=result['details'],
                error=result.get('error'),
                response_data=result.get('response_data')
            )
            
        except Exception as e:
            return ValidationResult(
                service=self.service_name,
                credential_type=credential_type or 'unknown',
                is_valid=False,
                confidence=0.0,
                details={'error': str(e)},
                error=str(e)
            )
    
    async def _test_smtp_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test SMTP connection in a separate thread"""
        def test_connection():
            try:
                server = config['server']
                port = int(config.get('port', 587))
                username = config['username']
                password = config['password']
                
                # Determine if SSL/TLS should be used
                use_ssl = port == 465
                use_tls = port in [587, 25] and not use_ssl
                
                if use_ssl:
                    context = ssl.create_default_context()
                    smtp = smtplib.SMTP_SSL(server, port, context=context, timeout=self.timeout)
                else:
                    smtp = smtplib.SMTP(server, port, timeout=self.timeout)
                
                # Enable debugging to capture server responses
                smtp.set_debuglevel(0)
                
                if use_tls:
                    smtp.starttls(context=ssl.create_default_context())
                
                # Attempt login
                smtp.login(username, password)
                
                # Get server capabilities
                capabilities = smtp.ehlo_resp.decode('utf-8') if hasattr(smtp, 'ehlo_resp') else ''
                
                smtp.quit()
                
                return {
                    'valid': True,
                    'confidence': 0.95,
                    'details': {
                        'server': server,
                        'port': port,
                        'username': username,
                        'ssl_used': use_ssl,
                        'tls_used': use_tls,
                        'capabilities': capabilities
                    },
                    'response_data': {
                        'auth_success': True,
                        'capabilities': capabilities
                    }
                }
                
            except smtplib.SMTPAuthenticationError as e:
                return {
                    'valid': False,
                    'confidence': 0.9,
                    'details': {'auth_error': str(e)},
                    'error': f"SMTP Authentication failed: {e}"
                }
                
            except smtplib.SMTPConnectError as e:
                return {
                    'valid': False,
                    'confidence': 0.7,
                    'details': {'connection_error': str(e)},
                    'error': f"SMTP Connection failed: {e}"
                }
                
            except Exception as e:
                return {
                    'valid': False,
                    'confidence': 0.3,
                    'details': {'general_error': str(e)},
                    'error': f"SMTP test failed: {e}"
                }
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, test_connection)
        return result