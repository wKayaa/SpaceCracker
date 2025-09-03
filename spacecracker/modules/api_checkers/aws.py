#!/usr/bin/env python3
"""
AWS API Checker
Validate AWS credentials and test permissions
"""

import re
import json
import base64
from typing import Dict, Any, List
from .base import BaseAPIChecker, ValidationResult

class AWSChecker(BaseAPIChecker):
    """AWS credential validator"""
    
    @property
    def service_name(self) -> str:
        return "AWS"
    
    @property
    def supported_credential_types(self) -> List[str]:
        return ["access_key", "secret_key", "session_token", "credentials_pair"]
    
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        """Extract AWS credentials from content"""
        credentials = []
        
        # AWS Access Key ID pattern
        access_key_pattern = r'AKIA[0-9A-Z]{16}'
        access_keys = re.findall(access_key_pattern, content)
        
        for access_key in access_keys:
            credentials.append({
                'type': 'aws_access_key',
                'value': access_key,
                'credential_type': 'access_key'
            })
        
        # AWS Secret Access Key patterns
        secret_patterns = [
            (r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']', 'secret_key'),
            (r'aws[_-]?secret[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']', 'secret_key'),
            (r'secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']', 'secret_key')
        ]
        
        for pattern, cred_type in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                credentials.append({
                    'type': 'aws_secret_key',
                    'value': match.group(1),
                    'credential_type': cred_type
                })
        
        # AWS Session Token
        session_token_patterns = [
            r'aws[_-]?session[_-]?token["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{100,})["\']',
            r'session[_-]?token["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{100,})["\']'
        ]
        
        for pattern in session_token_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                credentials.append({
                    'type': 'aws_session_token',
                    'value': match.group(1),
                    'credential_type': 'session_token'
                })
        
        return credentials
    
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        """Validate AWS credential"""
        try:
            if credential_type == 'access_key':
                return await self._validate_access_key(credential)
            elif credential_type == 'secret_key':
                return await self._validate_secret_key(credential)
            elif credential_type == 'session_token':
                return await self._validate_session_token(credential)
            elif credential_type == 'credentials_pair':
                return await self._validate_credentials_pair(credential)
            else:
                # Try to auto-detect credential type
                if re.match(r'AKIA[0-9A-Z]{16}', credential):
                    return await self._validate_access_key(credential)
                elif len(credential) == 40 and re.match(r'[A-Za-z0-9/+=]+', credential):
                    return await self._validate_secret_key(credential)
                else:
                    return ValidationResult(
                        service=self.service_name,
                        credential_type='unknown',
                        is_valid=False,
                        confidence=0.0,
                        details={'error': 'Unknown AWS credential format'},
                        error="Could not determine AWS credential type"
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
    
    async def _validate_access_key(self, access_key: str) -> ValidationResult:
        """Validate AWS Access Key ID format"""
        if not re.match(r'AKIA[0-9A-Z]{16}', access_key):
            return ValidationResult(
                service=self.service_name,
                credential_type='access_key',
                is_valid=False,
                confidence=0.9,
                details={'error': 'Invalid AWS Access Key ID format'},
                error="Invalid AWS Access Key ID format"
            )
        
        # Format is valid, but we can't test without secret key
        return ValidationResult(
            service=self.service_name,
            credential_type='access_key',
            is_valid=True,
            confidence=0.6,
            details={
                'format_valid': True,
                'note': 'Format validation only - requires secret key for full validation'
            },
            response_data={'format_check': 'passed'}
        )
    
    async def _validate_secret_key(self, secret_key: str) -> ValidationResult:
        """Validate AWS Secret Access Key format"""
        if len(secret_key) != 40 or not re.match(r'[A-Za-z0-9/+=]+$', secret_key):
            return ValidationResult(
                service=self.service_name,
                credential_type='secret_key',
                is_valid=False,
                confidence=0.9,
                details={'error': 'Invalid AWS Secret Access Key format'},
                error="Invalid AWS Secret Access Key format"
            )
        
        # Format is valid, but we can't test without access key
        return ValidationResult(
            service=self.service_name,
            credential_type='secret_key',
            is_valid=True,
            confidence=0.6,
            details={
                'format_valid': True,
                'note': 'Format validation only - requires access key for full validation'
            },
            response_data={'format_check': 'passed'}
        )
    
    async def _validate_session_token(self, session_token: str) -> ValidationResult:
        """Validate AWS Session Token"""
        if len(session_token) < 100:
            return ValidationResult(
                service=self.service_name,
                credential_type='session_token',
                is_valid=False,
                confidence=0.8,
                details={'error': 'AWS Session Token too short'},
                error="AWS Session Token appears too short"
            )
        
        # Try to decode if it looks like base64
        try:
            decoded = base64.b64decode(session_token + '==')  # Add padding
            # Session tokens often contain JSON-like structures
            if b'{' in decoded or b'aws' in decoded.lower():
                confidence = 0.8
            else:
                confidence = 0.6
        except:
            confidence = 0.5
        
        return ValidationResult(
            service=self.service_name,
            credential_type='session_token',
            is_valid=True,
            confidence=confidence,
            details={
                'format_valid': True,
                'length': len(session_token),
                'note': 'Format validation only - requires full credential set for testing'
            },
            response_data={'format_check': 'passed'}
        )
    
    async def _validate_credentials_pair(self, credentials: Dict[str, str]) -> ValidationResult:
        """Validate AWS credentials pair using STS GetCallerIdentity"""
        try:
            access_key = credentials.get('access_key')
            secret_key = credentials.get('secret_key')
            session_token = credentials.get('session_token')
            
            if not access_key or not secret_key:
                return ValidationResult(
                    service=self.service_name,
                    credential_type='credentials_pair',
                    is_valid=False,
                    confidence=0.9,
                    details={'error': 'Missing access key or secret key'},
                    error="Both access key and secret key are required"
                )
            
            # Validate individual credential formats first
            access_key_result = await self._validate_access_key(access_key)
            secret_key_result = await self._validate_secret_key(secret_key)
            
            if not access_key_result.is_valid or not secret_key_result.is_valid:
                return ValidationResult(
                    service=self.service_name,
                    credential_type='credentials_pair',
                    is_valid=False,
                    confidence=0.9,
                    details={'error': 'Invalid credential format'},
                    error="Invalid access key or secret key format"
                )
            
            # Test with AWS STS GetCallerIdentity (safe, read-only operation)
            result = await self._test_aws_credentials(access_key, secret_key, session_token)
            
            return ValidationResult(
                service=self.service_name,
                credential_type='credentials_pair',
                is_valid=result['valid'],
                confidence=result['confidence'],
                details=result['details'],
                error=result.get('error'),
                response_data=result.get('response_data')
            )
            
        except Exception as e:
            return ValidationResult(
                service=self.service_name,
                credential_type='credentials_pair',
                is_valid=False,
                confidence=0.0,
                details={'error': str(e)},
                error=str(e)
            )
    
    async def _test_aws_credentials(self, access_key: str, secret_key: str, session_token: str = None) -> Dict[str, Any]:
        """Test AWS credentials using STS GetCallerIdentity"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Create session with provided credentials
            session_kwargs = {
                'aws_access_key_id': access_key,
                'aws_secret_access_key': secret_key
            }
            
            if session_token:
                session_kwargs['aws_session_token'] = session_token
            
            session = boto3.Session(**session_kwargs)
            sts_client = session.client('sts', region_name='us-east-1')
            
            # Call GetCallerIdentity (safe, minimal permissions required)
            response = sts_client.get_caller_identity()
            
            return {
                'valid': True,
                'confidence': 0.95,
                'details': {
                    'user_id': response.get('UserId'),
                    'account': response.get('Account'),
                    'arn': response.get('Arn'),
                    'test_method': 'STS GetCallerIdentity'
                },
                'response_data': response
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code in ['InvalidUserID.NotFound', 'AccessDenied']:
                return {
                    'valid': False,
                    'confidence': 0.9,
                    'details': {'aws_error': error_code, 'message': str(e)},
                    'error': f"AWS Error: {error_code}"
                }
            else:
                return {
                    'valid': False,
                    'confidence': 0.7,
                    'details': {'aws_error': error_code, 'message': str(e)},
                    'error': f"AWS Client Error: {error_code}"
                }
                
        except NoCredentialsError:
            return {
                'valid': False,
                'confidence': 0.9,
                'details': {'error': 'No valid credentials provided'},
                'error': "Invalid AWS credentials"
            }
            
        except Exception as e:
            return {
                'valid': False,
                'confidence': 0.3,
                'details': {'general_error': str(e)},
                'error': f"AWS credential test failed: {e}"
            }