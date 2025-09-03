#!/usr/bin/env python3
"""
Telegram Bot Module
Integration for sending scan results to Telegram
"""

import asyncio
import aiohttp
import logging
import json
import time
from datetime import datetime

class TelegramBot:
    """Telegram bot for sending scan results"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.logger = logging.getLogger(__name__)
        self.last_progress_update = 0
        self.progress_message_id = None
        self.progress_update_interval = 30  # Send progress updates every 30 seconds
        
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
            
    async def send_progress_update(self, stats, elapsed_time):
        """Send or update progress message"""
        try:
            current_time = time.time()
            
            # Rate limit progress updates
            if current_time - self.last_progress_update < self.progress_update_interval:
                return
                
            self.last_progress_update = current_time
            
            # Format progress message
            elapsed_str = self._format_elapsed_time(elapsed_time)
            urls_processed = stats.get('urls_processed', 0)
            total_findings = stats.get('total_findings', 0)
            findings_by_service = stats.get('findings_by_service', {})
            
            # Calculate rate
            rate = int(urls_processed / elapsed_time) if elapsed_time > 0 else 0
            
            message = f"""⚡ <b>SpaceCracker Progress Update</b> ⚡

⏱️ <b>Elapsed:</b> {elapsed_str}
🌐 <b>URLs Processed:</b> {urls_processed:,}
📡 <b>Rate:</b> {rate}/second
🏆 <b>Total Findings:</b> {total_findings}

📊 <b>Findings by Service:</b>"""
            
            if findings_by_service:
                for service, count in sorted(findings_by_service.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        message += f"\n• {service.title()}: {count}"
            else:
                message += "\n• No findings yet..."
                
            message += f"\n\n🔍 <i>Scan in progress... Next update in {self.progress_update_interval}s</i>"
            
            # Send or edit progress message
            if self.progress_message_id:
                await self._edit_message(message, self.progress_message_id)
            else:
                response_data = await self._send_single_message_with_response(message)
                if response_data and 'result' in response_data:
                    self.progress_message_id = response_data['result']['message_id']
                    
        except Exception as e:
            self.logger.error(f"Error sending progress update: {e}")
    
    async def send_scan_completion(self, stats, elapsed_time):
        """Send scan completion notification"""
        try:
            elapsed_str = self._format_elapsed_time(elapsed_time)
            urls_processed = stats.get('urls_processed', 0)
            total_findings = stats.get('total_findings', 0)
            findings_by_service = stats.get('findings_by_service', {})
            
            avg_rate = int(urls_processed / elapsed_time) if elapsed_time > 0 else 0
            
            message = f"""✅ <b>SpaceCracker Scan Completed</b> ✅

⏱️ <b>Total Time:</b> {elapsed_str}
🌐 <b>URLs Processed:</b> {urls_processed:,}
📡 <b>Average Rate:</b> {avg_rate}/second
🏆 <b>Total Findings:</b> {total_findings}

📈 <b>Final Results by Service:</b>"""
            
            if findings_by_service:
                for service, count in sorted(findings_by_service.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        message += f"\n• ✅ {service.title()}: {count}"
            else:
                message += "\n• No findings detected"
                
            message += f"\n\n🎯 <i>Detailed results will be sent for validated findings only.</i>"
            
            await self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending completion message: {e}")
    
    async def _edit_message(self, text, message_id, parse_mode='HTML'):
        """Edit an existing message"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'chat_id': self.chat_id,
                    'message_id': message_id,
                    'text': text,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': True
                }
                
                async with session.post(f"{self.base_url}/editMessageText", json=data) as response:
                    if response.status != 200:
                        # If edit fails, send new message
                        await self.send_message(text, parse_mode)
                        
        except Exception as e:
            self.logger.error(f"Error editing message: {e}")
            # Fallback: send new message
            await self.send_message(text, parse_mode)
    
    async def _send_single_message_with_response(self, text, parse_mode='HTML'):
        """Send a single message and return response data"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': True
                }
                
                async with session.post(f"{self.base_url}/sendMessage", json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Telegram API error: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error sending message with response: {e}")
            return None
    
    def _format_elapsed_time(self, seconds):
        """Format elapsed time as human readable string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    async def send_startup_message(self):
        """Send a message when the scanner starts"""
        message = f"""🚀 <b>SpaceCracker Started</b>
        
Scanner has been initialized and is ready to begin scanning.
        
⏰ <b>Started at:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>
        
You will receive periodic progress updates and notifications for validated findings only."""
        
        await self.send_message(message)
        """Send a message when the scanner starts"""
        message = f"""🚀 <b>SpaceCracker Started</b>
        
Scanner has been initialized and is ready to begin scanning.
        
⏰ <b>Started at:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>
        
You will receive notifications for validated findings only."""
        
        await self.send_message(message)