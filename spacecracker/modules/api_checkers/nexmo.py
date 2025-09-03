#!/usr/bin/env python3
"""
Nexmo/Vonage API Checker
"""

import re
from typing import Dict, Any, List
from .base import BaseAPIChecker, ValidationResult

class NexmoChecker(BaseAPIChecker):
    @property
    def service_name(self) -> str:
        return "Nexmo"
    
    @property
    def supported_credential_types(self) -> List[str]:
        return ["api_key", "api_secret"]
    
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        credentials = []
        
        patterns = [
            (r'nexmo[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-fA-F0-9]{8})["\']', 'nexmo_api_key'),
            (r'nexmo[_-]?api[_-]?secret["\']?\s*[:=]\s*["\']([a-fA-F0-9]{16})["\']', 'nexmo_api_secret'),
            (r'vonage[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-fA-F0-9]{8})["\']', 'vonage_api_key')
        ]
        
        for pattern, cred_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                credentials.append({'type': cred_type, 'value': match.group(1)})
        
        return credentials
    
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        if len(credential) == 8 and re.match(r'[a-fA-F0-9]{8}', credential):
            return ValidationResult(
                service=self.service_name,
                credential_type='api_key',
                is_valid=True,
                confidence=0.7,
                details={'format_valid': True},
                response_data={'format_check': 'passed'}
            )
        
        return ValidationResult(
            service=self.service_name,
            credential_type=credential_type or 'unknown',
            is_valid=False,
            confidence=0.0,
            details={'error': 'Invalid Nexmo credential format'},
            error="Invalid Nexmo credential format"
        )