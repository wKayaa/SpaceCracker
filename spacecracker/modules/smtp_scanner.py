#!/usr/bin/env python3
"""
SMTP Security Scanner Module
Legitimate email service security validation for authorized testing
"""

import socket
import ssl
import smtplib
import dns.resolver
import re
import asyncio
import aiohttp
from typing import Dict, Any, List, Tuple
from .base import BaseModule


class SMTPScanner(BaseModule):
    module_id = "smtp_scanner"
    name = "SMTP Security Scanner"
    description = "Legitimate email service security validation and SMTP configuration testing for authorized penetration testing"
    supports_batch = True

    def __init__(self, config: Any = None):
        super().__init__(config)
        self.smtp_ports = [25, 465, 587, 2525]
        self.email_service_patterns = {
            'aws_ses': [
                r'MAIL_MAILER\s*=\s*["\']?ses["\']?',
                r'SES_KEY\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'SES_SECRET\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'AWS_SES_REGION\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'email\.amazonaws\.com'
            ],
            'sendgrid': [
                r'SENDGRID_API_KEY\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_MAILER\s*=\s*["\']?sendgrid["\']?',
                r'api\.sendgrid\.com'
            ],
            'mailgun': [
                r'MAILGUN_SECRET\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAILGUN_DOMAIN\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_MAILER\s*=\s*["\']?mailgun["\']?',
                r'api\.mailgun\.net'
            ],
            'postmark': [
                r'POSTMARK_TOKEN\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_MAILER\s*=\s*["\']?postmark["\']?',
                r'api\.postmarkapp\.com'
            ],
            'sparkpost': [
                r'SPARKPOST_SECRET\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'api\.sparkpost\.com'
            ],
            'smtp_generic': [
                r'MAIL_HOST\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_PORT\s*=\s*["\']?(\d+)["\']?',
                r'MAIL_USERNAME\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_PASSWORD\s*=\s*["\']?([^"\'\\s]+)["\']?',
                r'MAIL_ENCRYPTION\s*=\s*["\']?(tls|ssl)["\']?'
            ]
        }
        
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run SMTP security scanner against target"""
        findings = []
        errors = []
        
        try:
            # Extract domain from target URL
            domain = self._extract_domain(target)
            
            # Test SMTP configuration exposure
            config_findings = await self._check_smtp_config_exposure(target)
            findings.extend(config_findings)
            
            # Test SMTP services on domain
            smtp_findings = await self._test_smtp_services(domain)
            findings.extend(smtp_findings)
            
            # Test for email service configurations
            email_service_findings = await self._check_email_service_patterns(target)
            findings.extend(email_service_findings)
            
            # Test MX records and email infrastructure
            mx_findings = await self._analyze_mx_records(domain)
            findings.extend(mx_findings)
            
        except Exception as e:
            errors.append(f"SMTP scanner error: {str(e)}")
        
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import urllib.parse
        parsed = urllib.parse.urlparse(url if url.startswith('http') else f'http://{url}')
        return parsed.netloc or parsed.path.split('/')[0]
    
    async def _check_smtp_config_exposure(self, target: str) -> List[Dict[str, Any]]:
        """Check for exposed SMTP configuration files"""
        findings = []
        
        config_endpoints = [
            '.env',
            'config/mail.php',
            'config/email.php',
            'wp-config.php',
            'configuration.php',
            'config.php',
            'settings.php',
            'app.config',
            'web.config'
        ]
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                for endpoint in config_endpoints:
                    try:
                        test_url = f"{target.rstrip('/')}/{endpoint}"
                        async with session.get(test_url) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Check for email service patterns
                                smtp_config = self._extract_smtp_config(content, endpoint)
                                if smtp_config:
                                    severity = self._calculate_config_severity(smtp_config)
                                    
                                    findings.append({
                                        "id": f"smtp_config_exposure_{endpoint.replace('/', '_').replace('.', '_')}",
                                        "title": f"SMTP Configuration Exposure - {endpoint}",
                                        "severity": severity,
                                        "category": "config",
                                        "confidence": 0.9,
                                        "description": f"Exposed email/SMTP configuration in {endpoint}",
                                        "evidence": {
                                            "url": test_url,
                                            "endpoint": endpoint,
                                            "smtp_config": smtp_config,
                                            "content_preview": content[:300] + "..." if len(content) > 300 else content
                                        },
                                        "recommendation": "Secure email configuration files and use environment variables for sensitive data"
                                    })
                                    
                    except Exception as e:
                        continue  # Skip failed requests
                        
        except Exception:
            pass
            
        return findings
    
    def _extract_smtp_config(self, content: str, endpoint: str) -> Dict[str, List[Dict]]:
        """Extract SMTP configuration from content"""
        config_found = {}
        
        for service, patterns in self.email_service_patterns.items():
            config_found[service] = []
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    config_item = {
                        'pattern': pattern,
                        'match': match.group(0),
                        'line': content[:match.start()].count('\n') + 1
                    }
                    
                    # Extract captured groups (credentials/config values)
                    if match.groups():
                        config_item['value'] = match.group(1)
                        
                    config_found[service].append(config_item)
        
        # Filter out empty results
        return {k: v for k, v in config_found.items() if v}
    
    def _calculate_config_severity(self, smtp_config: Dict) -> str:
        """Calculate severity based on exposed configuration"""
        high_risk_services = ['aws_ses', 'sendgrid', 'mailgun', 'postmark']
        
        for service in high_risk_services:
            if service in smtp_config and any('KEY' in item.get('match', '').upper() or 'SECRET' in item.get('match', '').upper() or 'TOKEN' in item.get('match', '').upper() for item in smtp_config[service]):
                return "Critical"
        
        if 'smtp_generic' in smtp_config and any('PASSWORD' in item.get('match', '').upper() for item in smtp_config['smtp_generic']):
            return "High"
        
        return "Medium"
    
    async def _test_smtp_services(self, domain: str) -> List[Dict[str, Any]]:
        """Test SMTP services on domain"""
        findings = []
        
        for port in self.smtp_ports:
            try:
                smtp_info = await self._test_smtp_port(domain, port)
                if smtp_info:
                    findings.append({
                        "id": f"smtp_service_{domain}_{port}",
                        "title": f"SMTP Service Discovery - {domain}:{port}",
                        "severity": self._calculate_smtp_severity(smtp_info),
                        "category": "exposure",
                        "confidence": 0.8,
                        "description": f"SMTP service detected on {domain}:{port}",
                        "evidence": smtp_info,
                        "recommendation": "Ensure SMTP service is properly secured and authenticated"
                    })
                    
            except Exception as e:
                continue  # Skip failed connections
                
        return findings
    
    async def _test_smtp_port(self, domain: str, port: int) -> Dict[str, Any]:
        """Test specific SMTP port"""
        try:
            # Test connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((domain, port))
            
            if result == 0:  # Connection successful
                try:
                    # Get SMTP banner
                    sock.send(b'EHLO test\r\n')
                    response = sock.recv(1024).decode('utf-8', errors='ignore')
                    
                    smtp_info = {
                        "domain": domain,
                        "port": port,
                        "status": "open",
                        "banner": response.strip(),
                        "supports_starttls": "STARTTLS" in response,
                        "supports_auth": "AUTH" in response
                    }
                    
                    # Test for open relay (basic check)
                    if await self._test_open_relay(domain, port):
                        smtp_info["open_relay"] = True
                        smtp_info["security_risk"] = "High - Open Relay Detected"
                    
                    sock.close()
                    return smtp_info
                    
                except Exception:
                    sock.close()
                    return {
                        "domain": domain,
                        "port": port,
                        "status": "open",
                        "banner": "Unable to read banner"
                    }
            else:
                sock.close()
                return None
                
        except Exception:
            return None
    
    async def _test_open_relay(self, domain: str, port: int) -> bool:
        """Test for SMTP open relay (basic test)"""
        try:
            with smtplib.SMTP(domain, port, timeout=10) as server:
                server.ehlo()
                if server.has_extn('STARTTLS'):
                    server.starttls()
                
                # Try to send test email without authentication
                try:
                    server.mail('test@example.com')
                    server.rcpt('relay-test@example.org') 
                    server.quit()
                    return True  # Open relay detected
                except smtplib.SMTPRecipientsRefused:
                    return False  # Properly secured
                except smtplib.SMTPAuthenticationError:
                    return False  # Authentication required (good)
                    
        except Exception:
            return False
    
    def _calculate_smtp_severity(self, smtp_info: Dict) -> str:
        """Calculate SMTP finding severity"""
        if smtp_info.get('open_relay'):
            return "Critical"
        elif not smtp_info.get('supports_starttls'):
            return "High"
        elif smtp_info.get('status') == 'open':
            return "Medium" 
        else:
            return "Low"
    
    async def _check_email_service_patterns(self, target: str) -> List[Dict[str, Any]]:
        """Check for email service configuration patterns in web content"""
        findings = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(target) as response:
                    content = await response.text()
                    
                    # Look for email service indicators in HTML/JS
                    email_patterns = [
                        r'sendgrid\.com',
                        r'mailgun\.org',
                        r'ses\.amazonaws\.com',
                        r'postmarkapp\.com',
                        r'sparkpost\.com',
                        r'mandrillapp\.com'
                    ]
                    
                    for pattern in email_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            service_name = pattern.split('.')[0].title()
                            findings.append({
                                "id": f"email_service_reference_{service_name.lower()}",
                                "title": f"Email Service Reference - {service_name}",
                                "severity": "Low",
                                "category": "exposure", 
                                "confidence": 0.6,
                                "description": f"Reference to {service_name} email service found in web content",
                                "evidence": {
                                    "url": target,
                                    "service": service_name,
                                    "pattern": pattern,
                                    "context": content[max(0, match.start()-50):match.end()+50]
                                },
                                "recommendation": "Review email service integrations for security best practices"
                            })
                            
        except Exception:
            pass
            
        return findings
    
    async def _analyze_mx_records(self, domain: str) -> List[Dict[str, Any]]:
        """Analyze MX records for email infrastructure"""
        findings = []
        
        try:
            # Get MX records
            mx_records = []
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                for rdata in answers:
                    mx_records.append({
                        'priority': rdata.preference,
                        'exchange': str(rdata.exchange).rstrip('.')
                    })
            except Exception:
                return findings  # No MX records or DNS error
            
            if mx_records:
                # Analyze MX records for email services
                email_providers = self._identify_email_providers(mx_records)
                
                findings.append({
                    "id": f"mx_records_analysis_{domain}",
                    "title": f"Email Infrastructure Analysis - {domain}",
                    "severity": "Low",
                    "category": "exposure",
                    "confidence": 0.7,
                    "description": f"Email infrastructure information for {domain}",
                    "evidence": {
                        "domain": domain,
                        "mx_records": mx_records,
                        "email_providers": email_providers,
                        "mx_count": len(mx_records)
                    },
                    "recommendation": "Review email infrastructure security and SPF/DKIM/DMARC records"
                })
                
        except Exception:
            pass
            
        return findings
    
    def _identify_email_providers(self, mx_records: List[Dict]) -> List[str]:
        """Identify email service providers from MX records"""
        providers = []
        
        provider_patterns = {
            'Google Workspace': [r'google\.com', r'googlemail\.com'],
            'Microsoft 365': [r'outlook\.com', r'office365\.com', r'microsoft\.com'],
            'Amazon SES': [r'amazonaws\.com'],
            'Cloudflare': [r'cloudflare\.net'],
            'ProtonMail': [r'protonmail\.ch'],
            'Zoho': [r'zoho\.com'],
            'Fastmail': [r'fastmail\.com']
        }
        
        for record in mx_records:
            exchange = record['exchange'].lower()
            for provider, patterns in provider_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, exchange):
                        if provider not in providers:
                            providers.append(provider)
                        break
        
        return providers