#!/usr/bin/env python3
"""
Stripe API Checker
"""

import re
import aiohttp
from typing import Dict, Any, List
from .base import BaseAPIChecker, ValidationResult

class StripeChecker(BaseAPIChecker):
    @property
    def service_name(self) -> str:
        return "Stripe"
    
    @property
    def supported_credential_types(self) -> List[str]:
        return ["secret_key", "publishable_key", "webhook_secret"]
    
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        credentials = []
        
        patterns = [
            (r'sk_live_[0-9a-zA-Z]{24,}', 'stripe_live_secret'),
            (r'sk_test_[0-9a-zA-Z]{24,}', 'stripe_test_secret'),
            (r'pk_live_[0-9a-zA-Z]{24,}', 'stripe_live_publishable'),
            (r'pk_test_[0-9a-zA-Z]{24,}', 'stripe_test_publishable'),
            (r'whsec_[0-9a-zA-Z]{24,}', 'stripe_webhook_secret')
        ]
        
        for pattern, cred_type in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                credentials.append({'type': cred_type, 'value': match})
        
        return credentials
    
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        try:
            async with aiohttp.ClientSession() as session:
                if credential.startswith('sk_'):
                    # Test with Stripe API
                    headers = {'Authorization': f'Bearer {credential}'}
                    response = await self._make_request(
                        session, 'GET', 'https://api.stripe.com/v1/account', headers=headers
                    )
                    
                    if response['success']:
                        return ValidationResult(
                            service=self.service_name,
                            credential_type='secret_key',
                            is_valid=True,
                            confidence=0.95,
                            details={'api_test': 'success'},
                            response_data=response['json']
                        )
                    else:
                        return ValidationResult(
                            service=self.service_name,
                            credential_type='secret_key',
                            is_valid=False,
                            confidence=0.9,
                            details={'api_test': 'failed', 'status': response['status']},
                            error=f"Stripe API returned status {response['status']}"
                        )
                else:
                    # Format validation only for other types
                    return ValidationResult(
                        service=self.service_name,
                        credential_type=credential_type or 'publishable_key',
                        is_valid=True,
                        confidence=0.6,
                        details={'format_valid': True},
                        response_data={'format_check': 'passed'}
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