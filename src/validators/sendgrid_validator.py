import aiohttp
from typing import Dict, Optional
import asyncio

class SendGridValidator:
    def __init__(self):
        self.api_url = "https://api.sendgrid.com/v3"
    
    async def validate_api_key(self, api_key: str, source_url: str) -> Dict:
        """Validate SendGrid API key"""
        result = {
            'valid': False,
            'service': 'sendgrid',
            'source_url': source_url,
            'api_key': api_key
        }
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get user profile
                async with session.get(f"{self.api_url}/user/profile", headers=headers) as response:
                    if response.status == 200:
                        profile_data = await response.json()
                        result['valid'] = True
                        result['profile'] = profile_data
                        
                        # Get sending quota
                        async with session.get(f"{self.api_url}/user/credits", headers=headers) as credits_response:
                            if credits_response.status == 200:
                                credits_data = await credits_response.json()
                                result['credits'] = credits_data
                        
                        return result
                    elif response.status == 401:
                        result['error'] = 'Unauthorized - Invalid API key'
                    elif response.status == 403:
                        result['error'] = 'Forbidden - Insufficient permissions'
                    else:
                        result['error'] = f'HTTP {response.status}'
                        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def format_output(self, validation_result: Dict, crack_id: str) -> str:
        """Format SendGrid validation result"""
        output = f"""
✨ New SendGrid Hit (#{crack_id})

🔑 API KEY: {validation_result.get('api_key', 'N/A')}
🚀 HIT WORKS: {'Yes' if validation_result['valid'] else 'No'}
"""
        
        if validation_result['valid'] and 'profile' in validation_result:
            profile = validation_result['profile']
            output += f"""
👤 USER: {profile.get('username', 'N/A')}
📧 EMAIL: {profile.get('email', 'N/A')}
🏢 COMPANY: {profile.get('company', 'N/A')}
"""
            
            if 'credits' in validation_result:
                credits = validation_result['credits']
                output += f"""
💰 CREDITS: {credits.get('remain', 0)} remaining
📊 TOTAL: {credits.get('total', 0)} total
"""
        
        output += f"""
ℹ️ URL - {validation_result['source_url']}
🆔 Crack ID - #{crack_id}

✨ SpaceCracker.co - @SpaceCracker
"""
        return output