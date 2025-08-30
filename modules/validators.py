#!/usr/bin/env python3
"""
Secret Validator Module
Validates extracted secrets using API calls and connections
"""

import asyncio
import aiohttp
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import base64
import hashlib
import hmac
from urllib.parse import urlencode
import json
import re

class SecretValidator:
    """Validates extracted secrets"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validation_config = config.get('validation', {})
        
    async def validate_secret(self, secret_data):
        """Main validation function"""
        if not isinstance(secret_data, dict) or 'type' not in secret_data:
            return {'valid': False, 'error': 'Invalid secret format'}
            
        secret_type = secret_data['type']
        secret_value = secret_data.get('value', '')
        
        try:
            if secret_type == 'aws_access_key' and self.validation_config.get('check_aws'):
                return await self._validate_aws_key(secret_data)
            elif secret_type == 'aws_ses_key' and self.validation_config.get('check_aws_ses'):
                return await self._validate_aws_ses_key(secret_data)
            elif secret_type == 'sendgrid_key' and self.validation_config.get('check_sendgrid'):
                return await self._validate_sendgrid_key(secret_value)
            elif secret_type == 'mailgun_key' and self.validation_config.get('check_mailgun'):
                return await self._validate_mailgun_key(secret_data)
            elif secret_type == 'postmark_token' and self.validation_config.get('check_postmark'):
                return await self._validate_postmark_token(secret_value)
            elif secret_type == 'sparkpost_key' and self.validation_config.get('check_sparkpost'):
                return await self._validate_sparkpost_key(secret_value)
            elif secret_type == 'smtp_credentials' and self.validation_config.get('check_smtp'):
                return await self._validate_smtp_credentials(secret_data)
            elif secret_type == 'stripe_key' and self.validation_config.get('check_stripe'):
                return await self._validate_stripe_key(secret_value)
            elif secret_type == 'github_token' and self.validation_config.get('check_github'):
                return await self._validate_github_token(secret_value)
            elif secret_type == 'database_url':
                return await self._validate_database_url(secret_value)
            elif secret_type == 'jwt_token':
                return await self._validate_jwt_token(secret_value)
            else:
                return {'valid': False, 'error': f'Validation not supported for {secret_type}'}
                
        except Exception as e:
            self.logger.error(f"Error validating {secret_type}: {e}")
            return {'valid': False, 'error': str(e)}
            
    async def _validate_aws_key(self, secret_data):
        """Validate AWS access key"""
        try:
            access_key = secret_data.get('access_key', '')
            secret_key = secret_data.get('secret_key', '')
            
            if not access_key or not secret_key:
                return {'valid': False, 'error': 'Missing access key or secret key'}
                
            # Create boto3 session with provided credentials
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            
            # Test with STS get-caller-identity (low privilege operation)
            sts_client = session.client('sts')
            response = sts_client.get_caller_identity()
            
            return {
                'valid': True,
                'service': 'AWS',
                'account_id': response.get('Account'),
                'user_id': response.get('UserId'),
                'arn': response.get('Arn')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidUserID.NotFound':
                return {'valid': False, 'error': 'Invalid AWS credentials'}
            elif error_code == 'AccessDenied':
                return {'valid': True, 'service': 'AWS', 'note': 'Valid credentials but access denied'}
            else:
                return {'valid': False, 'error': f'AWS error: {error_code}'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    async def _validate_sendgrid_key(self, api_key):
        """Validate SendGrid API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Test with user profile endpoint
                async with session.get('https://api.sendgrid.com/v3/user/profile', headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'service': 'SendGrid',
                            'email': data.get('email'),
                            'username': data.get('username')
                        }
                    elif response.status == 401:
                        return {'valid': False, 'error': 'Invalid SendGrid API key'}
                    else:
                        return {'valid': False, 'error': f'SendGrid API error: {response.status}'}
                        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    async def _validate_smtp_credentials(self, secret_data):
        """Validate SMTP credentials"""
        try:
            host = secret_data.get('host', '')
            port = secret_data.get('port', 587)
            username = secret_data.get('username', '')
            password = secret_data.get('password', '')
            
            if not all([host, username, password]):
                return {'valid': False, 'error': 'Missing SMTP credentials'}
                
            # Create SSL context
            context = ssl.create_default_context()
            
            # Test connection
            with smtplib.SMTP(host, port) as server:
                server.starttls(context=context)
                server.login(username, password)
                
            return {
                'valid': True,
                'service': 'SMTP',
                'host': host,
                'port': port,
                'username': username
            }
            
        except smtplib.SMTPAuthenticationError:
            return {'valid': False, 'error': 'Invalid SMTP credentials'}
        except smtplib.SMTPException as e:
            return {'valid': False, 'error': f'SMTP error: {str(e)}'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    async def _validate_stripe_key(self, api_key):
        """Validate Stripe API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                # Test with account endpoint
                async with session.get('https://api.stripe.com/v1/account', headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'service': 'Stripe',
                            'account_id': data.get('id'),
                            'country': data.get('country'),
                            'email': data.get('email')
                        }
                    elif response.status == 401:
                        return {'valid': False, 'error': 'Invalid Stripe API key'}
                    else:
                        return {'valid': False, 'error': f'Stripe API error: {response.status}'}
                        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    async def _validate_github_token(self, token):
        """Validate GitHub token"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {token}',
                    'User-Agent': 'SpaceCracker-Validator'
                }
                
                # Test with user endpoint
                async with session.get('https://api.github.com/user', headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'service': 'GitHub',
                            'username': data.get('login'),
                            'name': data.get('name'),
                            'email': data.get('email')
                        }
                    elif response.status == 401:
                        return {'valid': False, 'error': 'Invalid GitHub token'}
                    else:
                        return {'valid': False, 'error': f'GitHub API error: {response.status}'}
                        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    async def _validate_database_url(self, db_url):
        """Validate database URL (basic format check)"""
        try:
            # Basic URL format validation
            db_patterns = {
                'mongodb': r'^mongodb://.*',
                'mysql': r'^mysql://.*',
                'postgresql': r'^postgresql://.*',
                'redis': r'^redis://.*'
            }
            
            for db_type, pattern in db_patterns.items():
                if re.match(pattern, db_url, re.IGNORECASE):
                    # Extract basic info without actually connecting
                    parts = db_url.split('://')
                    if len(parts) > 1:
                        connection_info = parts[1]
                        return {
                            'valid': True,
                            'service': f'{db_type.title()} Database',
                            'type': db_type,
                            'url': db_url[:50] + '...' if len(db_url) > 50 else db_url,
                            'note': 'URL format valid - connection not tested'
                        }
                        
            return {'valid': False, 'error': 'Unknown database URL format'}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    async def _validate_jwt_token(self, token):
        """Validate JWT token (basic format check and decode)"""
        try:
            # Split JWT token
            parts = token.split('.')
            if len(parts) != 3:
                return {'valid': False, 'error': 'Invalid JWT format'}
                
            # Decode header and payload (without signature verification)
            header = self._decode_jwt_part(parts[0])
            payload = self._decode_jwt_part(parts[1])
            
            if not header or not payload:
                return {'valid': False, 'error': 'Cannot decode JWT'}
                
            result = {
                'valid': True,
                'service': 'JWT Token',
                'algorithm': header.get('alg'),
                'type': header.get('typ')
            }
            
            # Extract useful payload information
            if 'exp' in payload:
                import datetime
                exp_timestamp = payload['exp']
                exp_date = datetime.datetime.fromtimestamp(exp_timestamp)
                result['expires'] = exp_date.isoformat()
                result['expired'] = exp_date < datetime.datetime.now()
                
            if 'iss' in payload:
                result['issuer'] = payload['iss']
                
            if 'sub' in payload:
                result['subject'] = payload['sub']
                
            return result
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    def _decode_jwt_part(self, part):
        """Decode JWT part (header or payload)"""
        try:
            # Add padding if necessary
            missing_padding = len(part) % 4
            if missing_padding:
                part += '=' * (4 - missing_padding)
                
            decoded_bytes = base64.urlsafe_b64decode(part)
            return json.loads(decoded_bytes.decode('utf-8'))
        except Exception:
            return None
            
    async def validate_multiple_secrets(self, secrets_list):
        """Validate multiple secrets concurrently"""
        tasks = [self.validate_secret(secret) for secret in secrets_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        validated_secrets = []
        for secret, result in zip(secrets_list, results):
            if isinstance(result, dict):
                validated_secrets.append({
                    'secret': secret,
                    'validation': result
                })
            else:
                validated_secrets.append({
                    'secret': secret,
                    'validation': {'valid': False, 'error': str(result)}
                })
                
        return validated_secrets

    async def _validate_aws_ses_key(self, secret_data):
        """Validate AWS SES credentials and get sending quota"""
        try:
            access_key = secret_data.get('access_key', '')
            secret_key = secret_data.get('secret_key', '')
            region = secret_data.get('region', 'us-east-1')
            
            if not access_key or not secret_key:
                return {'valid': False, 'error': 'Missing AWS SES access key or secret key'}
                
            # Create boto3 session with provided credentials
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            # Test with SES-specific calls
            ses_client = session.client('ses')
            
            # Get sending quota
            quota_response = ses_client.get_send_quota()
            
            # Get verified email addresses
            verified_response = ses_client.list_verified_email_addresses()
            
            return {
                'valid': True,
                'service': 'AWS SES',
                'region': region,
                'max_24_hour_send': quota_response.get('Max24HourSend'),
                'max_send_rate': quota_response.get('MaxSendRate'),
                'sent_last_24_hours': quota_response.get('SentLast24Hours'),
                'verified_emails_count': len(verified_response.get('VerifiedEmailAddresses', [])),
                'verified_emails': verified_response.get('VerifiedEmailAddresses', [])[:5]  # Show first 5
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['InvalidUserID.NotFound', 'SignatureDoesNotMatch']:
                return {'valid': False, 'error': 'Invalid AWS SES credentials'}
            elif error_code == 'AccessDenied':
                return {'valid': True, 'service': 'AWS SES', 'note': 'Valid credentials but SES access denied'}
            else:
                return {'valid': False, 'error': f'AWS SES error: {error_code}'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def _validate_mailgun_key(self, secret_data):
        """Validate Mailgun API key"""
        try:
            api_key = secret_data.get('api_key', '')
            domain = secret_data.get('domain', '')
            
            if not api_key:
                return {'valid': False, 'error': 'Missing Mailgun API key'}
                
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth('api', api_key)
                
                # Test with domain stats endpoint
                if domain:
                    url = f'https://api.mailgun.net/v3/{domain}/stats/total'
                else:
                    url = 'https://api.mailgun.net/v3/domains'
                    
                async with session.get(url, auth=auth) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {
                            'valid': True,
                            'service': 'Mailgun',
                            'api_key_type': 'Domain' if domain else 'Account'
                        }
                        
                        if domain:
                            result['domain'] = domain
                            result['stats'] = data.get('stats', [])[:1]  # Show recent stats
                        else:
                            result['domains_count'] = len(data.get('items', []))
                            
                        return result
                    elif response.status == 401:
                        return {'valid': False, 'error': 'Invalid Mailgun API key'}
                    else:
                        return {'valid': False, 'error': f'Mailgun API error: {response.status}'}
                        
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def _validate_postmark_token(self, api_token):
        """Validate Postmark server token"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-Postmark-Server-Token': api_token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Test with server info endpoint
                async with session.get('https://api.postmarkapp.com/server', headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'service': 'Postmark',
                            'server_name': data.get('Name'),
                            'server_id': data.get('ID'),
                            'color': data.get('Color'),
                            'bounce_hook_url': bool(data.get('BounceHookUrl')),
                            'inbound_hook_url': bool(data.get('InboundHookUrl'))
                        }
                    elif response.status == 401:
                        return {'valid': False, 'error': 'Invalid Postmark server token'}
                    else:
                        return {'valid': False, 'error': f'Postmark API error: {response.status}'}
                        
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def _validate_sparkpost_key(self, api_key):
        """Validate SparkPost API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': api_key,
                    'Content-Type': 'application/json'
                }
                
                # Test with account endpoint
                async with session.get('https://api.sparkpost.com/api/v1/account', headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('results', {})
                        return {
                            'valid': True,
                            'service': 'SparkPost',
                            'company_name': result.get('company_name'),
                            'country_code': result.get('country_code'),
                            'anniversary': result.get('anniversary'),
                            'created': result.get('created')
                        }
                    elif response.status == 401:
                        return {'valid': False, 'error': 'Invalid SparkPost API key'}
                    else:
                        return {'valid': False, 'error': f'SparkPost API error: {response.status}'}
                        
        except Exception as e:
            return {'valid': False, 'error': str(e)}