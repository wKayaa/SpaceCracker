#!/usr/bin/env python3
"""
Git Scanner Module
Scans for exposed Git repositories and extracts sensitive information
"""

import asyncio
import aiohttp
import logging
import json
import re
from urllib.parse import urljoin

class GitScanner:
    """Git repository scanner"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Git-related paths to check
        self.git_paths = [
            '.git/',
            '.git/config',
            '.git/HEAD',
            '.git/index',
            '.git/logs/',
            '.git/logs/HEAD',
            '.git/refs/',
            '.git/refs/heads/',
            '.git/refs/heads/master',
            '.git/refs/heads/main',
            '.git/refs/remotes/',
            '.git/objects/',
            '.git/info/',
            '.git/info/refs',
            '.git/description',
            '.git/hooks/',
            '.git/packed-refs',
            '.gitignore',
            '.gitconfig',
            '.git-credentials'
        ]
        
        # Other VCS paths
        self.vcs_paths = [
            '.svn/',
            '.svn/entries',
            '.svn/wc.db',
            '.hg/',
            '.hg/hgrc',
            '.bzr/',
            '.bzr/branch/'
        ]
        
        # Patterns to look for in git files
        self.sensitive_patterns = {
            'credentials': [
                r'username\s*=\s*(.+)',
                r'password\s*=\s*(.+)',
                r'token\s*=\s*(.+)',
                r'key\s*=\s*(.+)'
            ],
            'urls': [
                r'url\s*=\s*(https?://[^\s]+)',
                r'origin\s+(https?://[^\s]+)'
            ],
            'emails': [
                r'email\s*=\s*([^\s]+@[^\s]+)',
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ],
            'branches': [
                r'ref:\s*refs/heads/(.+)',
                r'refs/heads/(.+)'
            ]
        }
        
    async def scan(self, session, target):
        """Main scanning function for Git"""
        results = []
        
        try:
            # Test Git paths
            git_results = await self._test_git_exposure(session, target)
            if git_results:
                results.extend(git_results)
                
            # Test other VCS
            vcs_results = await self._test_other_vcs(session, target)
            if vcs_results:
                results.extend(vcs_results)
                
            # If Git is exposed, try to extract more information
            if any(r.get('type') == 'git_exposure' for r in results):
                additional_results = await self._extract_git_info(session, target)
                if additional_results:
                    results.extend(additional_results)
                    
        except Exception as e:
            self.logger.error(f"Git Scanner error for {target}: {e}")
            
        return results
        
    async def _test_git_exposure(self, session, target):
        """Test for Git repository exposure"""
        results = []
        
        for git_path in self.git_paths:
            try:
                git_url = urljoin(target, git_path)
                
                async with session.get(git_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check if it's actually a Git file
                        is_git_file = self._validate_git_content(git_path, content)
                        
                        if is_git_file:
                            result = {
                                'module': 'git_scanner',
                                'type': 'git_exposure',
                                'url': git_url,
                                'base_target': target,
                                'status': response.status,
                                'git_file': git_path,
                                'content_length': len(content),
                                'severity': self._assess_git_severity(git_path),
                                'headers': dict(response.headers)
                            }
                            
                            # Extract sensitive information
                            extracted_info = self._extract_sensitive_info(content)
                            if extracted_info:
                                result['extracted_info'] = extracted_info
                                result['severity'] = 'high'
                                
                            results.append(result)
                            
                    elif response.status == 403:
                        # Git directory exists but access denied
                        result = {
                            'module': 'git_scanner',
                            'type': 'git_access_denied',
                            'url': urljoin(target, git_path),
                            'base_target': target,
                            'status': response.status,
                            'git_file': git_path,
                            'severity': 'medium',
                            'note': 'Git directory exists but access denied'
                        }
                        results.append(result)
                        
            except Exception as e:
                self.logger.debug(f"Error testing git path {git_path}: {e}")
                
        return results
        
    async def _test_other_vcs(self, session, target):
        """Test for other version control system exposures"""
        results = []
        
        for vcs_path in self.vcs_paths:
            try:
                vcs_url = urljoin(target, vcs_path)
                
                async with session.get(vcs_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        vcs_type = self._identify_vcs_type(vcs_path, content)
                        if vcs_type:
                            result = {
                                'module': 'git_scanner',
                                'type': 'vcs_exposure',
                                'vcs_type': vcs_type,
                                'url': vcs_url,
                                'base_target': target,
                                'status': response.status,
                                'vcs_file': vcs_path,
                                'content_length': len(content),
                                'severity': 'medium',
                                'headers': dict(response.headers)
                            }
                            
                            # Extract any sensitive information
                            extracted_info = self._extract_sensitive_info(content)
                            if extracted_info:
                                result['extracted_info'] = extracted_info
                                result['severity'] = 'high'
                                
                            results.append(result)
                            
            except Exception as e:
                self.logger.debug(f"Error testing VCS path {vcs_path}: {e}")
                
        return results
        
    async def _extract_git_info(self, session, target):
        """Extract additional information from Git repository"""
        results = []
        
        try:
            # Try to get commit logs
            logs_url = urljoin(target, '.git/logs/HEAD')
            try:
                async with session.get(logs_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        commits = self._parse_git_logs(content)
                        
                        if commits:
                            result = {
                                'module': 'git_scanner',
                                'type': 'git_commit_history',
                                'url': logs_url,
                                'base_target': target,
                                'status': response.status,
                                'commits': commits[:10],  # Limit to last 10 commits
                                'total_commits': len(commits),
                                'severity': 'medium'
                            }
                            results.append(result)
            except:
                pass
                
            # Try to get branch information
            refs_url = urljoin(target, '.git/refs/heads/')
            try:
                async with session.get(refs_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        branches = self._extract_branches(content)
                        
                        if branches:
                            result = {
                                'module': 'git_scanner',
                                'type': 'git_branches',
                                'url': refs_url,
                                'base_target': target,
                                'status': response.status,
                                'branches': branches,
                                'severity': 'low'
                            }
                            results.append(result)
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error extracting additional Git info: {e}")
            
        return results
        
    def _validate_git_content(self, git_path, content):
        """Validate if content is actually from a Git file"""
        if not content:
            return False
            
        # Check based on file type
        if git_path == '.git/config':
            return '[core]' in content or '[remote' in content
        elif git_path == '.git/HEAD':
            return 'ref:' in content or re.match(r'^[0-9a-f]{40}', content.strip())
        elif git_path == '.git/index':
            return content.startswith('DIRC')  # Git index signature
        elif 'logs' in git_path:
            return re.search(r'[0-9a-f]{40}\s+[0-9a-f]{40}', content)
        elif git_path == '.git/description':
            return 'Unnamed repository' in content or len(content) < 1000
        else:
            # Generic Git content check
            return any(indicator in content for indicator in [
                'refs/', 'objects/', 'HEAD', 'branch', 'commit', 'tree'
            ])
            
    def _identify_vcs_type(self, vcs_path, content):
        """Identify the type of version control system"""
        if '.svn' in vcs_path:
            if 'entries' in content or 'wc.db' in vcs_path:
                return 'Subversion'
        elif '.hg' in vcs_path:
            if '[paths]' in content or 'default' in content:
                return 'Mercurial'
        elif '.bzr' in vcs_path:
            return 'Bazaar'
            
        return None
        
    def _assess_git_severity(self, git_path):
        """Assess severity based on Git file type"""
        high_risk_files = ['.git/config', '.git/logs/HEAD', '.git-credentials']
        medium_risk_files = ['.git/', '.git/HEAD', '.git/refs/']
        
        if any(risk_file in git_path for risk_file in high_risk_files):
            return 'high'
        elif any(risk_file in git_path for risk_file in medium_risk_files):
            return 'medium'
        else:
            return 'low'
            
    def _extract_sensitive_info(self, content):
        """Extract sensitive information from Git content"""
        extracted = {}
        
        for category, patterns in self.sensitive_patterns.items():
            findings = []
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if match.groups():
                        findings.append(match.group(1).strip())
                    else:
                        findings.append(match.group(0).strip())
                        
            if findings:
                extracted[category] = list(set(findings))  # Remove duplicates
                
        return extracted if extracted else None
        
    def _parse_git_logs(self, content):
        """Parse Git log content"""
        commits = []
        
        try:
            lines = content.strip().split('\n')
            for line in lines:
                # Git log format: old_commit new_commit author timestamp timezone message
                parts = line.split(' ', 6)
                if len(parts) >= 6:
                    commit_info = {
                        'old_commit': parts[0][:8] if parts[0] != '0' * 40 else None,
                        'new_commit': parts[1][:8],
                        'author': parts[2],
                        'timestamp': int(parts[3]) if parts[3].isdigit() else None,
                        'timezone': parts[4],
                        'message': parts[5] if len(parts) > 5 else ''
                    }
                    commits.append(commit_info)
        except Exception as e:
            self.logger.debug(f"Error parsing git logs: {e}")
            
        return commits
        
    def _extract_branches(self, content):
        """Extract branch names from refs content"""
        branches = []
        
        try:
            # Look for HTML directory listing or direct file content
            if '<a href=' in content:
                # HTML directory listing
                branch_pattern = r'<a href="([^/"]+)/?">([^<]+)</a>'
                matches = re.findall(branch_pattern, content)
                for href, name in matches:
                    if not href.startswith(('..', '?', 'http')):
                        branches.append(href)
            else:
                # Direct content - look for refs
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('<'):
                        branches.append(line.strip())
                        
        except Exception as e:
            self.logger.debug(f"Error extracting branches: {e}")
            
        return branches