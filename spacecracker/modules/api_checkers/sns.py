#!/usr/bin/env python3
"""
AWS SNS API Checker
"""

import re
from typing import Dict, Any, List
from .base import BaseAPIChecker, ValidationResult

class SNSChecker(BaseAPIChecker):
    @property
    def service_name(self) -> str:
        return "AWS SNS"
    
    @property
    def supported_credential_types(self) -> List[str]:
        return ["topic_arn", "subscription_arn"]
    
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        credentials = []
        
        # SNS Topic ARN pattern
        topic_pattern = r'arn:aws:sns:[a-z0-9-]+:\d{12}:[a-zA-Z0-9_-]+'
        topics = re.findall(topic_pattern, content)
        
        for topic in topics:
            credentials.append({'type': 'sns_topic_arn', 'value': topic})
        
        return credentials
    
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        # Validate ARN format
        arn_pattern = r'arn:aws:sns:[a-z0-9-]+:\d{12}:[a-zA-Z0-9_-]+'
        
        if re.match(arn_pattern, credential):
            return ValidationResult(
                service=self.service_name,
                credential_type='topic_arn',
                is_valid=True,
                confidence=0.8,
                details={'format_valid': True, 'arn': credential},
                response_data={'format_check': 'passed'}
            )
        
        return ValidationResult(
            service=self.service_name,
            credential_type=credential_type or 'unknown',
            is_valid=False,
            confidence=0.0,
            details={'error': 'Invalid SNS ARN format'},
            error="Invalid SNS ARN format"
        )