#!/usr/bin/env python3
"""
SpaceCracker V2 - SendGrid API Validator
Comprehensive SendGrid validation with quota checking and account details
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging


class SendGridValidator:
    """SendGrid API key validator with comprehensive account analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.sendgrid.com/v3"
        
    async def validate(self, api_key: str) -> Dict[str, Any]:
        """
        Validate SendGrid API key and gather comprehensive account information
        
        Args:
            api_key: SendGrid API key (format: SG.*)
            
        Returns:
            Dict containing validation results and account details
        """
        if not api_key or not api_key.startswith('SG.'):
            return {
                'valid': False,
                'error': 'Invalid SendGrid API key format'
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Test 1: Get API key scopes
                scopes_result = await self._get_api_scopes(session, headers)
                if not scopes_result.get('valid'):
                    return scopes_result
                
                # Test 2: Get account information
                account_info = await self._get_account_info(session, headers)
                
                # Test 3: Get quota and usage statistics
                quota_info = await self._get_quota_info(session, headers)
                
                # Test 4: Get verified senders
                senders_info = await self._get_verified_senders(session, headers)
                
                # Test 5: Get templates
                templates_info = await self._get_templates(session, headers)
                
                # Test 6: Get webhooks
                webhooks_info = await self._get_webhooks(session, headers)
                
                # Test 7: Get reputation
                reputation_info = await self._get_reputation(session, headers)
                
                # Combine all information
                return {
                    'valid': True,
                    'service': 'sendgrid',
                    'plan': account_info.get('type', 'Unknown'),
                    'credits': quota_info.get('credits_remaining', 'Unknown'),
                    'rate_limit': quota_info.get('rate_limit', 'Unknown'),
                    'reputation': reputation_info.get('reputation', 'Unknown'),
                    'verified_senders': senders_info.get('senders', []),
                    'templates': templates_info.get('count', 0),
                    'webhooks': webhooks_info.get('count', 0),
                    'monthly_sends': quota_info.get('monthly_sends', 0),
                    'monthly_limit': quota_info.get('monthly_limit', 0),
                    'scopes': scopes_result.get('scopes', []),
                    'account_type': account_info.get('type', 'Unknown'),
                    'user_id': account_info.get('user_id', 'Unknown')
                }
                
        except asyncio.TimeoutError:
            return {
                'valid': False,
                'error': 'Request timeout'
            }
        except Exception as e:
            self.logger.error(f"SendGrid validation error: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def _get_api_scopes(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get API key scopes to verify access"""
        try:
            async with session.get(f"{self.base_url}/scopes", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'valid': True,
                        'scopes': data.get('scopes', [])
                    }
                elif response.status == 401:
                    return {
                        'valid': False,
                        'error': 'Invalid API key or insufficient permissions'
                    }
                else:
                    return {
                        'valid': False,
                        'error': f'Unexpected response: {response.status}'
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Failed to get scopes: {str(e)}'
            }
    
    async def _get_account_info(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get account information"""
        try:
            async with session.get(f"{self.base_url}/user/account", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'type': data.get('type', 'Unknown'),
                        'user_id': data.get('id', 'Unknown'),
                        'reputation': data.get('reputation', 0)
                    }
        except Exception as e:
            self.logger.debug(f"Failed to get account info: {str(e)}")
        
        return {}
    
    async def _get_quota_info(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get quota and usage information"""
        quota_info = {}
        
        try:
            # Get user profile for quota information
            async with session.get(f"{self.base_url}/user/profile", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    quota_info.update({
                        'credits_remaining': data.get('credit', {}).get('remain', 'Unknown'),
                        'plan_type': data.get('type', 'Unknown')
                    })
        except Exception as e:
            self.logger.debug(f"Failed to get quota info: {str(e)}")
        
        try:
            # Get stats for usage information
            async with session.get(f"{self.base_url}/user/stats", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', [])
                    if stats:
                        latest_stats = stats[0] if isinstance(stats, list) else stats
                        quota_info.update({
                            'monthly_sends': latest_stats.get('metrics', {}).get('delivered', 0),
                            'rate_limit': '3000'  # SendGrid's default rate limit
                        })
        except Exception as e:
            self.logger.debug(f"Failed to get stats: {str(e)}")
        
        return quota_info
    
    async def _get_verified_senders(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get verified senders"""
        try:
            async with session.get(f"{self.base_url}/verified_senders", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    senders = []
                    for sender in data.get('results', []):
                        if sender.get('verified'):
                            senders.append(sender.get('from_email', ''))
                    return {'senders': senders}
        except Exception as e:
            self.logger.debug(f"Failed to get verified senders: {str(e)}")
        
        return {'senders': []}
    
    async def _get_templates(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get email templates count"""
        try:
            async with session.get(f"{self.base_url}/templates", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('templates', [])
                    active_count = sum(1 for t in templates if t.get('versions', []))
                    return {'count': active_count}
        except Exception as e:
            self.logger.debug(f"Failed to get templates: {str(e)}")
        
        return {'count': 0}
    
    async def _get_webhooks(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get webhook configuration count"""
        try:
            async with session.get(f"{self.base_url}/user/webhooks/event/settings", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    webhook_count = 0
                    if data.get('enabled'):
                        webhook_count = 1
                    
                    # Check for other webhook types
                    webhook_types = ['parse', 'inbound_parse']
                    for webhook_type in webhook_types:
                        try:
                            async with session.get(f"{self.base_url}/user/webhooks/{webhook_type}/settings", headers=headers) as wh_response:
                                if wh_response.status == 200:
                                    wh_data = await wh_response.json()
                                    if wh_data and isinstance(wh_data, list) and len(wh_data) > 0:
                                        webhook_count += len(wh_data)
                        except:
                            continue
                    
                    return {'count': webhook_count}
        except Exception as e:
            self.logger.debug(f"Failed to get webhooks: {str(e)}")
        
        return {'count': 0}
    
    async def _get_reputation(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get sender reputation"""
        try:
            async with session.get(f"{self.base_url}/user/account", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    reputation = data.get('reputation', 0)
                    if isinstance(reputation, (int, float)):
                        return {'reputation': f"{reputation:.1f}"}
        except Exception as e:
            self.logger.debug(f"Failed to get reputation: {str(e)}")
        
        return {'reputation': 'Unknown'}