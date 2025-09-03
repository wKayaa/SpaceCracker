#!/usr/bin/env python3
"""
Base API Checker Class
Common functionality for API credential verification
"""

import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of API credential validation"""
    service: str
    credential_type: str
    is_valid: bool
    confidence: float
    details: Dict[str, Any]
    error: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None

class BaseAPIChecker(ABC):
    """Base class for API credential checkers"""
    
    def __init__(self, config: Any = None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = getattr(config, 'api_timeout', 30) if config else 30
        self.max_retries = getattr(config, 'api_retries', 2) if config else 2
        
    @abstractmethod
    async def validate_credential(self, credential: str, credential_type: str = None) -> ValidationResult:
        """Validate a credential for this service"""
        pass
    
    @abstractmethod
    def extract_credentials(self, content: str) -> List[Dict[str, str]]:
        """Extract credentials from content that match this service"""
        pass
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Name of the service"""
        pass
    
    @property
    @abstractmethod
    def supported_credential_types(self) -> List[str]:
        """List of supported credential types"""
        pass
    
    async def _make_request(self, session: aiohttp.ClientSession, method: str, url: str, 
                           headers: Dict[str, str] = None, data: Any = None, 
                           json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        headers = headers or {}
        
        for attempt in range(self.max_retries + 1):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_text = await response.text()
                    
                    try:
                        response_json = await response.json()
                    except:
                        response_json = None
                    
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'text': response_text,
                        'json': response_json,
                        'success': response.status < 400
                    }
                    
            except asyncio.TimeoutError:
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("All retry attempts failed")
    
    def _calculate_confidence(self, response: Dict[str, Any], expected_indicators: List[str]) -> float:
        """Calculate confidence score based on response"""
        confidence = 0.0
        
        # Base confidence from successful response
        if response.get('success', False):
            confidence += 0.7
        
        # Check for service-specific indicators
        response_text = response.get('text', '').lower()
        response_json = response.get('json', {})
        
        indicator_matches = 0
        for indicator in expected_indicators:
            if indicator.lower() in response_text:
                indicator_matches += 1
            elif isinstance(response_json, dict) and indicator in str(response_json).lower():
                indicator_matches += 1
        
        if expected_indicators:
            confidence += 0.3 * (indicator_matches / len(expected_indicators))
        
        return min(confidence, 1.0)