#!/usr/bin/env python3
"""
Twilio API Checker
"""

import re
import aiohttp
from typing import Dict, Any, List
from .base import BaseAPIChecker, ValidationResult

class TwilioChecker(BaseAPIChecker):
    @property
    def service_name(self) -> str:
        return "Twilio"
    
    @property
    def supported_credential_types(self) -> List[str]:
        return ["account_sid", "auth_token", "api_key"]
    
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        credentials = []
        
        # Twilio Account SID
        sid_pattern = r'AC[0-9a-fA-F]{32}'
        sids = re.findall(sid_pattern, content)
        for sid in sids:
            credentials.append({'type': 'twilio_sid', 'value': sid})
        
        # Auth Token (generic 32-char hex)
        token_patterns = [
            r'twilio[_-]?auth[_-]?token["\']?\s*[:=]\s*["\']([0-9a-fA-F]{32})["\']',
            r'auth[_-]?token["\']?\s*[:=]\s*["\']([0-9a-fA-F]{32})["\']'
        ]
        
        for pattern in token_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                credentials.append({'type': 'twilio_auth_token', 'value': match.group(1)})
        
        return credentials
    
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        try:
            if credential_type == 'account_sid' or re.match(r'AC[0-9a-fA-F]{32}', credential):
                return ValidationResult(
                    service=self.service_name,
                    credential_type='account_sid',
                    is_valid=True,
                    confidence=0.8,
                    details={'format_valid': True},
                    response_data={'format_check': 'passed'}
                )
            
            return ValidationResult(
                service=self.service_name,
                credential_type=credential_type or 'unknown',
                is_valid=False,
                confidence=0.0,
                details={'error': 'Unknown Twilio credential format'},
                error="Could not validate Twilio credential"
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