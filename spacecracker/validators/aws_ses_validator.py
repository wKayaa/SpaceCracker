#!/usr/bin/env python3
"""
SpaceCracker V2 - AWS SES Validator
Comprehensive AWS SES validation with multi-region quota checking and access levels
"""

import asyncio
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Dict, Any, List, Optional
import logging
import concurrent.futures
from datetime import datetime, timedelta


class SESValidator:
    """AWS SES validator with comprehensive multi-region analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # AWS regions that support SES
        self.ses_regions = [
            'us-east-1',      # US East (N. Virginia)
            'us-west-2',      # US West (Oregon)  
            'eu-west-1',      # Europe (Ireland)
            'eu-central-1',   # Europe (Frankfurt)
            'ap-south-1',     # Asia Pacific (Mumbai)
            'ap-southeast-2', # Asia Pacific (Sydney)
            'ca-central-1',   # Canada (Central)
            'us-gov-west-1', # AWS GovCloud (US-West)
            'ap-northeast-1', # Asia Pacific (Tokyo)
            'eu-north-1',     # Europe (Stockholm)
            'me-south-1',     # Middle East (Bahrain)
            'sa-east-1',      # South America (São Paulo)
        ]
        
    async def validate(self, access_key: str, secret_key: str, session_token: str = None) -> Dict[str, Any]:
        """
        Validate AWS credentials and analyze SES capabilities across all regions
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key  
            session_token: Optional session token for temporary credentials
            
        Returns:
            Dict containing validation results and comprehensive SES analysis
        """
        if not access_key or not secret_key:
            return {
                'valid': False,
                'error': 'Missing AWS credentials'
            }
        
        if not access_key.startswith(('AKIA', 'ASIA')):
            return {
                'valid': False,
                'error': 'Invalid AWS access key format'
            }
        
        try:
            # Test basic credential validity
            test_result = await self._test_credentials(access_key, secret_key, session_token)
            if not test_result.get('valid'):
                return test_result
            
            # Analyze SES capabilities across all regions
            regions_analysis = await self._analyze_all_regions(access_key, secret_key, session_token)
            
            # Determine access level
            access_level = self._determine_access_level(regions_analysis)
            
            # Check SNS capabilities (often used with SES)
            sns_analysis = await self._analyze_sns_capabilities(access_key, secret_key, session_token, regions_analysis)
            
            return {
                'valid': True,
                'service': 'aws_ses',
                'access_key': access_key,
                'secret_key': secret_key[:8] + '...' + secret_key[-4:],  # Partial for security
                'access_level': access_level,
                'regions': regions_analysis,
                'sns_capabilities': sns_analysis,
                'total_regions': len([r for r in regions_analysis if r.get('status') == 'HEALTHY']),
                'production_ready': any(r.get('daily_quota', 0) > 200 for r in regions_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"AWS SES validation error: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def _test_credentials(self, access_key: str, secret_key: str, session_token: str = None) -> Dict[str, Any]:
        """Test if AWS credentials are valid by making a simple API call"""
        try:
            loop = asyncio.get_event_loop()
            
            def test_creds():
                session = boto3.Session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token
                )
                
                # Test with STS get-caller-identity (minimal permissions required)
                sts = session.client('sts', region_name='us-east-1')
                identity = sts.get_caller_identity()
                
                return {
                    'valid': True,
                    'user_id': identity.get('UserId', 'Unknown'),
                    'account': identity.get('Account', 'Unknown'),
                    'arn': identity.get('Arn', 'Unknown')
                }
            
            # Run in thread pool to avoid blocking
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = loop.run_in_executor(executor, test_creds)
                result = await asyncio.wait_for(future, timeout=10)
                return result
                
        except (NoCredentialsError, PartialCredentialsError):
            return {
                'valid': False,
                'error': 'Invalid or incomplete AWS credentials'
            }
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code in ['InvalidUserID.NotFound', 'SignatureDoesNotMatch', 'InvalidAccessKeyId']:
                return {
                    'valid': False,
                    'error': 'Invalid AWS credentials'
                }
            else:
                return {
                    'valid': False,
                    'error': f'AWS API error: {error_code}'
                }
        except asyncio.TimeoutError:
            return {
                'valid': False,
                'error': 'AWS API timeout'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    async def _analyze_all_regions(self, access_key: str, secret_key: str, session_token: str = None) -> List[Dict[str, Any]]:
        """Analyze SES capabilities across all supported regions"""
        loop = asyncio.get_event_loop()
        
        def analyze_region(region: str) -> Dict[str, Any]:
            try:
                session = boto3.Session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token
                )
                
                ses = session.client('ses', region_name=region)
                
                region_info = {
                    'name': region.upper(),
                    'region_code': region,
                    'status': 'HEALTHY',
                    'daily_quota': 0,
                    'sent_today': 0,
                    'max_send_rate': 0,
                    'verified_emails': [],
                    'verified_domains': [],
                    'sending_enabled': False,
                    'reputation_tracking': False
                }
                
                # Get send quota
                try:
                    quota_response = ses.get_send_quota()
                    region_info.update({
                        'daily_quota': int(quota_response.get('Max24HourSend', 0)),
                        'sent_today': int(quota_response.get('SentLast24Hours', 0)),
                        'max_send_rate': int(quota_response.get('MaxSendRate', 0))
                    })
                    region_info['sending_enabled'] = True
                except ClientError as e:
                    if e.response.get('Error', {}).get('Code') != 'AccessDenied':
                        region_info['status'] = 'ERROR'
                
                # Get verified email addresses
                try:
                    emails_response = ses.list_verified_email_addresses()
                    region_info['verified_emails'] = emails_response.get('VerifiedEmailAddresses', [])
                except ClientError:
                    pass
                
                # Get verified domains
                try:
                    domains_response = ses.list_identities()
                    identities = domains_response.get('Identities', [])
                    # Filter domains (identities without @ are typically domains)
                    domains = [identity for identity in identities if '@' not in identity]
                    region_info['verified_domains'] = domains
                except ClientError:
                    pass
                
                # Check reputation tracking
                try:
                    ses.describe_reputation()
                    region_info['reputation_tracking'] = True
                except ClientError:
                    pass
                
                return region_info
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                if error_code in ['UnauthorizedOperation', 'AccessDenied']:
                    return {
                        'name': region.upper(),
                        'region_code': region,
                        'status': 'ACCESS_DENIED',
                        'error': 'Insufficient permissions'
                    }
                else:
                    return {
                        'name': region.upper(),
                        'region_code': region,
                        'status': 'ERROR',
                        'error': error_code
                    }
            except Exception as e:
                return {
                    'name': region.upper(),
                    'region_code': region,
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        # Analyze all regions concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                loop.run_in_executor(executor, analyze_region, region)
                for region in self.ses_regions
            ]
            
            results = []
            for future in asyncio.as_completed(futures):
                try:
                    result = await asyncio.wait_for(future, timeout=15)
                    results.append(result)
                except asyncio.TimeoutError:
                    results.append({
                        'name': 'UNKNOWN',
                        'status': 'TIMEOUT',
                        'error': 'Analysis timeout'
                    })
                except Exception as e:
                    results.append({
                        'name': 'UNKNOWN', 
                        'status': 'ERROR',
                        'error': str(e)
                    })
        
        return results
    
    async def _analyze_sns_capabilities(self, access_key: str, secret_key: str, session_token: str = None, ses_regions: List[Dict] = None) -> Dict[str, Any]:
        """Analyze SNS capabilities for email notifications"""
        loop = asyncio.get_event_loop()
        
        def check_sns():
            try:
                session = boto3.Session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token
                )
                
                # Check SNS in regions where SES is available
                active_regions = [r['region_code'] for r in (ses_regions or []) if r.get('status') == 'HEALTHY']
                
                total_topics = 0
                sns_regions = []
                
                for region in active_regions[:3]:  # Limit to first 3 regions to avoid too many API calls
                    try:
                        sns = session.client('sns', region_name=region)
                        topics_response = sns.list_topics()
                        topic_count = len(topics_response.get('Topics', []))
                        total_topics += topic_count
                        
                        if topic_count > 0:
                            sns_regions.append({
                                'region': region,
                                'topics': topic_count
                            })
                            
                    except ClientError:
                        continue
                
                return {
                    'total_topics': total_topics,
                    'active_regions': sns_regions,
                    'accessible': total_topics > 0 or len(active_regions) > 0
                }
                
            except Exception as e:
                return {
                    'total_topics': 0,
                    'active_regions': [],
                    'accessible': False,
                    'error': str(e)
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = loop.run_in_executor(executor, check_sns)
            try:
                result = await asyncio.wait_for(future, timeout=10)
                return result
            except asyncio.TimeoutError:
                return {
                    'total_topics': 0,
                    'active_regions': [],
                    'accessible': False,
                    'error': 'SNS analysis timeout'
                }
    
    def _determine_access_level(self, regions_analysis: List[Dict[str, Any]]) -> str:
        """Determine the access level based on SES capabilities"""
        healthy_regions = [r for r in regions_analysis if r.get('status') == 'HEALTHY']
        
        if not healthy_regions:
            return 'No SES Access'
        
        # Check for production quotas (> 200/day indicates out of sandbox)
        production_regions = [r for r in healthy_regions if r.get('daily_quota', 0) > 200]
        
        # Check for verified domains/emails
        has_verified_identities = any(
            r.get('verified_emails') or r.get('verified_domains') 
            for r in healthy_regions
        )
        
        # Check sending capabilities
        can_send = any(r.get('sending_enabled') for r in healthy_regions)
        
        if production_regions and has_verified_identities and can_send:
            return 'Full SES + SNS'
        elif production_regions and can_send:
            return 'Production SES'
        elif healthy_regions and can_send:
            return 'Sandbox SES'
        elif healthy_regions:
            return 'Read-only SES'
        else:
            return 'Limited Access'