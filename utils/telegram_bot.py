#!/usr/bin/env python3
"""
Telegram Bot Module
Integration for sending scan results to Telegram
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime

class TelegramBot:
    """Telegram bot for sending scan results"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.logger = logging.getLogger(__name__)
        
    async def send_message(self, text, parse_mode='HTML'):
        """Send a message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            
            # Split long messages
            max_length = 4096
            if len(text) > max_length:
                messages = self._split_message(text, max_length)
                for msg in messages:
                    await self._send_single_message(msg, parse_mode)
                    await asyncio.sleep(0.1)  # Avoid rate limiting
            else:
                await self._send_single_message(text, parse_mode)
                
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            
    async def _send_single_message(self, text, parse_mode):
        """Send a single message"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': True
                }
                
                async with session.post(f"{self.base_url}/sendMessage", json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Telegram API error: {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Error sending single message: {e}")
            
    def _split_message(self, text, max_length):
        """Split long message into chunks"""
        messages = []
        while len(text) > max_length:
            # Find the last newline within the limit
            split_pos = text.rfind('\n', 0, max_length)
            if split_pos == -1:
                split_pos = max_length
                
            messages.append(text[:split_pos])
            text = text[split_pos:].lstrip()
            
        if text:
            messages.append(text)
            
        return messages
        
    async def send_results(self, results):
        """Send formatted scan results"""
        try:
            if not results:
                return
                
            # Filter and group results
            valid_results = [r for r in results if r.get('validated', False)]
            
            if not valid_results:
                self.logger.info("No validated results to send via Telegram")
                return
                
            # Create summary message
            summary = self._create_summary(valid_results)
            await self.send_message(summary)
            
            # Send detailed results for high severity findings
            high_severity_results = [r for r in valid_results if r.get('severity') == 'high']
            
            for result in high_severity_results[:5]:  # Limit to first 5 high severity
                detail_msg = self._format_result_detail(result)
                await self.send_message(detail_msg)
                await asyncio.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            self.logger.error(f"Error sending results to Telegram: {e}")
            
    def _create_summary(self, results):
        """Create a summary message"""
        total_results = len(results)
        
        # Count by severity
        severity_counts = {}
        module_counts = {}
        
        for result in results:
            severity = result.get('severity', 'unknown')
            module = result.get('module', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            module_counts[module] = module_counts.get(module, 0) + 1
            
        # Create message
        message = f"""🚨 <b>SpaceCracker Scan Results</b> 🚨
        
📊 <b>Summary:</b>
• Total validated findings: <b>{total_results}</b>
• Timestamp: <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>

🎯 <b>Severity Breakdown:</b>"""
        
        severity_emojis = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        for severity, count in sorted(severity_counts.items()):
            emoji = severity_emojis.get(severity, '⚪')
            message += f"\n• {emoji} {severity.title()}: <b>{count}</b>"
            
        message += f"\n\n🛠 <b>Module Results:</b>"
        for module, count in sorted(module_counts.items()):
            module_name = module.replace('_', ' ').title()
            message += f"\n• {module_name}: <b>{count}</b>"
            
        return message
        
    def _format_result_detail(self, result):
        """Format a detailed result message"""
        try:
            module = result.get('module', 'Unknown').replace('_', ' ').title()
            severity = result.get('severity', 'unknown').upper()
            url = result.get('url', 'N/A')
            result_type = result.get('type', 'Unknown').replace('_', ' ').title()
            
            # Severity emoji
            severity_emojis = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            severity_emoji = severity_emojis.get(severity, '⚪')
            
            message = f"""{severity_emoji} <b>{severity} FINDING</b>
            
🎯 <b>Type:</b> {result_type}
🛠 <b>Module:</b> {module}
🌐 <b>URL:</b> <code>{url}</code>"""
            
            # Add specific details based on result type
            if result.get('secrets'):
                message += f"\n🔑 <b>Secrets Found:</b> {len(result['secrets'])}"
                
            if result.get('validated_secrets'):
                message += f"\n✅ <b>Validated Secrets:</b> {len(result['validated_secrets'])}"
                
            if result.get('cve_id'):
                message += f"\n🚨 <b>CVE:</b> <code>{result['cve_id']}</code>"
                
            if result.get('files'):
                file_count = len(result['files'])
                message += f"\n📁 <b>Files Exposed:</b> {file_count}"
                
            if result.get('findings'):
                total_findings = sum(len(findings) for findings in result['findings'].values())
                message += f"\n🔍 <b>Total Findings:</b> {total_findings}"
                
            # Add extraction details if available
            if result.get('extracted_data'):
                message += "\n\n📋 <b>Extracted Data:</b>"
                for key, value in result['extracted_data'].items():
                    if isinstance(value, list):
                        message += f"\n• {key.title()}: {len(value)} items"
                    else:
                        message += f"\n• {key.title()}: <code>{str(value)[:50]}...</code>"
                        
            return message
            
        except Exception as e:
            self.logger.error(f"Error formatting result detail: {e}")
            return f"Error formatting result: {str(e)}"
            
    async def test_connection(self):
        """Test Telegram bot connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as response:
                    if response.status == 200:
                        bot_info = await response.json()
                        self.logger.info(f"Telegram bot connected: {bot_info['result']['first_name']}")
                        return True
                    else:
                        self.logger.error(f"Failed to connect to Telegram bot: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error testing Telegram connection: {e}")
            return False
            
    async def send_startup_message(self):
        """Send a message when the scanner starts"""
        message = f"""🚀 <b>SpaceCracker Started</b>
        
Scanner has been initialized and is ready to begin scanning.
        
⏰ <b>Started at:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>
        
You will receive notifications for validated findings only."""
        
        await self.send_message(message)