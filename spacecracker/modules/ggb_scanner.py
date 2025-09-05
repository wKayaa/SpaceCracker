#!/usr/bin/env python3
"""
SpaceCracker V2 - Enhanced GGB Scanner
GitHub/GitLab/Bitbucket repository scanner with comprehensive analysis
"""

import aiohttp
import asyncio
import base64
import re
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from .base import BaseModule


class GGBScanner(BaseModule):
    """Enhanced GitHub/GitLab/Bitbucket repository scanner"""
    
    module_id = "ggb_scanner"
    name = "GitHub/GitLab/Bitbucket Scanner"
    description = "Comprehensive Git repository analysis for exposed credentials and secrets"
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        
        # API endpoints
        self.github_api = "https://api.github.com"
        self.gitlab_api = "https://gitlab.com/api/v4"
        self.bitbucket_api = "https://api.bitbucket.org/2.0"
        
        # Sensitive file patterns to search for
        self.sensitive_files = [
            '.env', '.env.local', '.env.production', '.env.staging',
            'config.json', 'config.yml', 'config.yaml', 'settings.json',
            'credentials.json', 'auth.json', 'secrets.json', 'keys.json',
            'wp-config.php', 'configuration.php', 'database.php',
            '.aws/credentials', '.ssh/id_rsa', '.ssh/id_dsa', '.ssh/config',
            'backup.sql', 'dump.sql', 'database.sql', 'db.sql',
            'docker-compose.yml', 'docker-compose.yaml',
            'kubernetes.yaml', 'k8s-config.yaml', 'deployment.yaml',
            'app.yaml', 'appengine-web.xml', 'firebase.json',
            'package.json', 'composer.json', 'requirements.txt',
            'Gemfile', 'Cargo.toml', 'pom.xml', 'build.gradle',
            'terraform.tfvars', '.terraform.tfvars',
            'ansible.cfg', 'inventory.yml', 'playbook.yml'
        ]
        
        # Credential patterns for content analysis
        self.credential_patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
            'github_token': r'ghp_[a-zA-Z0-9]{36}',
            'sendgrid_key': r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
            'stripe_key': r'sk_(live|test)_[0-9a-zA-Z]{24,}',
            'mailgun_key': r'key-[0-9a-zA-Z]{32}',
            'twilio_sid': r'AC[0-9a-fA-F]{32}',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'api_key': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
            'database_url': r'(mysql|postgres|mongodb)://[^\s"\']+',
            'private_key': r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
        }
        
        # Common sensitive directories in repos
        self.sensitive_dirs = [
            'config/', 'configs/', 'configuration/',
            'secrets/', 'keys/', 'credentials/',
            'backup/', 'backups/', 'dumps/',
            'deploy/', 'deployment/', 'infrastructure/',
            '.aws/', '.ssh/', '.kube/',
            'docker/', 'k8s/', 'kubernetes/',
            'terraform/', 'ansible/', 'scripts/'
        ]
    
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run enhanced GGB repository scanner against target"""
        findings = []
        errors = []
        
        try:
            # Determine repository type and extract information
            repo_info = self._parse_repository_url(target)
            
            if not repo_info:
                # Not a repository URL, skip
                return {
                    "module": self.module_id,
                    "target": target,
                    "findings": findings,
                    "errors": errors
                }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                if repo_info['platform'] == 'github':
                    repo_findings = await self._scan_github_repo(session, repo_info)
                elif repo_info['platform'] == 'gitlab':
                    repo_findings = await self._scan_gitlab_repo(session, repo_info)
                elif repo_info['platform'] == 'bitbucket':
                    repo_findings = await self._scan_bitbucket_repo(session, repo_info)
                else:
                    repo_findings = []
                
                findings.extend(repo_findings)
                
        except Exception as e:
            errors.append(f"GGB scanner error: {str(e)}")
        
        return {
            "module": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _parse_repository_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse repository URL to extract platform and repository information"""
        parsed = urlparse(url)
        
        # GitHub patterns
        github_patterns = [
            r'github\.com/([^/]+)/([^/]+)',
            r'raw\.githubusercontent\.com/([^/]+)/([^/]+)',
            r'api\.github\.com/repos/([^/]+)/([^/]+)'
        ]
        
        # GitLab patterns  
        gitlab_patterns = [
            r'gitlab\.com/([^/]+)/([^/]+)',
            r'gitlab\.com/api/v4/projects/([^/]+)%2F([^/]+)'
        ]
        
        # Bitbucket patterns
        bitbucket_patterns = [
            r'bitbucket\.org/([^/]+)/([^/]+)',
            r'api\.bitbucket\.org/2\.0/repositories/([^/]+)/([^/]+)'
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, url)
            if match:
                return {
                    'platform': 'github',
                    'owner': match.group(1),
                    'repo': match.group(2).replace('.git', ''),
                    'api_base': self.github_api
                }
        
        for pattern in gitlab_patterns:
            match = re.search(pattern, url)
            if match:
                return {
                    'platform': 'gitlab', 
                    'owner': match.group(1),
                    'repo': match.group(2).replace('.git', ''),
                    'api_base': self.gitlab_api
                }
        
        for pattern in bitbucket_patterns:
            match = re.search(pattern, url)
            if match:
                return {
                    'platform': 'bitbucket',
                    'owner': match.group(1),
                    'repo': match.group(2).replace('.git', ''),
                    'api_base': self.bitbucket_api
                }
        
        return None
    
    async def _scan_github_repo(self, session: aiohttp.ClientSession, repo_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Comprehensive GitHub repository scanning"""
        findings = []
        owner = repo_info['owner']
        repo = repo_info['repo']
        
        try:
            # 1. Check if repository exists and is public
            repo_url = f"{self.github_api}/repos/{owner}/{repo}"
            async with session.get(repo_url) as response:
                if response.status != 200:
                    return findings
                
                repo_data = await response.json()
                
                # Check for sensitive repository information
                if repo_data.get('private') == False:
                    findings.append({
                        "id": f"github_public_repo",
                        "title": "Public GitHub Repository",
                        "severity": "Low",
                        "category": "information_disclosure",
                        "confidence": 1.0,
                        "description": f"Repository {owner}/{repo} is publicly accessible",
                        "evidence": {
                            "repository_url": repo_data.get('html_url'),
                            "description": repo_data.get('description', ''),
                            "created_at": repo_data.get('created_at'),
                            "updated_at": repo_data.get('updated_at'),
                            "language": repo_data.get('language'),
                            "size": repo_data.get('size')
                        }
                    })
            
            # 2. Search for sensitive files in repository
            for sensitive_file in self.sensitive_files:
                file_findings = await self._check_github_file(session, owner, repo, sensitive_file)
                findings.extend(file_findings)
            
            # 3. Search in code for credentials
            code_findings = await self._search_github_code(session, owner, repo)
            findings.extend(code_findings)
            
            # 4. Check commit history for exposed secrets
            commit_findings = await self._scan_github_commits(session, owner, repo)
            findings.extend(commit_findings)
            
            # 5. Check issues and pull requests for sensitive information
            issues_findings = await self._scan_github_issues(session, owner, repo)
            findings.extend(issues_findings)
            
            # 6. Check releases for sensitive attachments
            releases_findings = await self._scan_github_releases(session, owner, repo)
            findings.extend(releases_findings)
            
        except Exception as e:
            # Log error but don't fail the entire scan
            pass
        
        return findings
    
    async def _check_github_file(self, session: aiohttp.ClientSession, owner: str, repo: str, file_path: str) -> List[Dict[str, Any]]:
        """Check for specific sensitive files in GitHub repository"""
        findings = []
        
        try:
            file_url = f"{self.github_api}/repos/{owner}/{repo}/contents/{file_path}"
            async with session.get(file_url) as response:
                if response.status == 200:
                    file_data = await response.json()
                    
                    # Decode file content if it's base64 encoded
                    content = ""
                    if file_data.get('encoding') == 'base64':
                        try:
                            content = base64.b64decode(file_data['content']).decode('utf-8')
                        except:
                            content = ""
                    
                    # Analyze content for credentials
                    credentials = self._extract_credentials_from_content(content)
                    
                    if credentials:
                        for cred in credentials:
                            findings.append({
                                "id": f"github_sensitive_file_{file_path.replace('/', '_')}",
                                "title": f"Sensitive File Exposed: {file_path}",
                                "severity": "Critical",
                                "category": "credential_exposure",
                                "confidence": 0.9,
                                "description": f"File {file_path} contains {cred['type']} credentials",
                                "evidence": {
                                    "file_path": file_path,
                                    "file_url": file_data.get('html_url'),
                                    "credential_type": cred['type'],
                                    "credential_value": cred['value'][:20] + "..." if len(cred['value']) > 20 else cred['value'],
                                    "line_context": cred.get('context', '')
                                }
                            })
                    else:
                        # File exists but no obvious credentials - still a finding
                        findings.append({
                            "id": f"github_sensitive_file_exposure_{file_path.replace('/', '_')}",
                            "title": f"Sensitive File Available: {file_path}",
                            "severity": "Medium",
                            "category": "information_disclosure",
                            "confidence": 0.8,
                            "description": f"Sensitive file {file_path} is publicly accessible",
                            "evidence": {
                                "file_path": file_path,
                                "file_url": file_data.get('html_url'),
                                "file_size": file_data.get('size', 0)
                            }
                        })
                        
        except Exception as e:
            # File doesn't exist or access denied
            pass
        
        return findings
    
    async def _search_github_code(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Search repository code for credential patterns"""
        findings = []
        
        # GitHub Code Search API has rate limits, so we'll search for high-value patterns
        high_value_patterns = ['AKIA', 'SG.', 'sk_live_', 'ghp_']
        
        for pattern in high_value_patterns:
            try:
                search_url = f"{self.github_api}/search/code?q={pattern}+repo:{owner}/{repo}"
                async with session.get(search_url) as response:
                    if response.status == 200:
                        search_data = await response.json()
                        
                        for item in search_data.get('items', [])[:5]:  # Limit to 5 results per pattern
                            findings.append({
                                "id": f"github_code_credential_{pattern}",
                                "title": f"Potential Credential in Code: {pattern}",
                                "severity": "High",
                                "category": "credential_exposure",
                                "confidence": 0.7,
                                "description": f"Code contains pattern {pattern} which may indicate credentials",
                                "evidence": {
                                    "file_path": item.get('path'),
                                    "file_url": item.get('html_url'),
                                    "repository": item.get('repository', {}).get('full_name'),
                                    "pattern": pattern
                                }
                            })
                            
            except Exception as e:
                # Rate limited or other error
                continue
        
        return findings
    
    async def _scan_github_commits(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Scan recent commit messages and diffs for sensitive information"""
        findings = []
        
        try:
            commits_url = f"{self.github_api}/repos/{owner}/{repo}/commits?per_page=10"
            async with session.get(commits_url) as response:
                if response.status == 200:
                    commits = await response.json()
                    
                    for commit in commits:
                        message = commit.get('commit', {}).get('message', '')
                        
                        # Check commit message for sensitive patterns
                        if any(word in message.lower() for word in ['password', 'secret', 'key', 'token', 'credential']):
                            findings.append({
                                "id": f"github_sensitive_commit_{commit['sha'][:8]}",
                                "title": "Potentially Sensitive Commit Message",
                                "severity": "Medium",
                                "category": "information_disclosure", 
                                "confidence": 0.6,
                                "description": f"Commit message may contain sensitive information",
                                "evidence": {
                                    "commit_sha": commit['sha'],
                                    "commit_url": commit.get('html_url'),
                                    "message": message,
                                    "author": commit.get('commit', {}).get('author', {}).get('name'),
                                    "date": commit.get('commit', {}).get('author', {}).get('date')
                                }
                            })
                            
        except Exception as e:
            pass
        
        return findings
    
    async def _scan_github_issues(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Scan issues and pull requests for sensitive information"""
        findings = []
        
        try:
            issues_url = f"{self.github_api}/repos/{owner}/{repo}/issues?state=all&per_page=20"
            async with session.get(issues_url) as response:
                if response.status == 200:
                    issues = await response.json()
                    
                    for issue in issues:
                        body = issue.get('body', '') or ''
                        title = issue.get('title', '') or ''
                        
                        # Check for credentials in issue content
                        credentials = self._extract_credentials_from_content(f"{title}\n{body}")
                        
                        if credentials:
                            for cred in credentials:
                                findings.append({
                                    "id": f"github_issue_credential_{issue['number']}",
                                    "title": f"Credential in Issue #{issue['number']}",
                                    "severity": "High",
                                    "category": "credential_exposure",
                                    "confidence": 0.8,
                                    "description": f"Issue contains {cred['type']} credentials",
                                    "evidence": {
                                        "issue_number": issue['number'],
                                        "issue_url": issue.get('html_url'),
                                        "issue_title": title,
                                        "credential_type": cred['type']
                                    }
                                })
                                
        except Exception as e:
            pass
        
        return findings
    
    async def _scan_github_releases(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Scan releases for sensitive information or files"""
        findings = []
        
        try:
            releases_url = f"{self.github_api}/repos/{owner}/{repo}/releases?per_page=10"
            async with session.get(releases_url) as response:
                if response.status == 200:
                    releases = await response.json()
                    
                    for release in releases:
                        # Check release notes for credentials
                        body = release.get('body', '') or ''
                        credentials = self._extract_credentials_from_content(body)
                        
                        if credentials:
                            for cred in credentials:
                                findings.append({
                                    "id": f"github_release_credential_{release['id']}",
                                    "title": f"Credential in Release {release.get('tag_name')}",
                                    "severity": "High",
                                    "category": "credential_exposure",
                                    "confidence": 0.8,
                                    "description": f"Release notes contain {cred['type']} credentials",
                                    "evidence": {
                                        "release_tag": release.get('tag_name'),
                                        "release_url": release.get('html_url'),
                                        "credential_type": cred['type']
                                    }
                                })
                        
                        # Check for sensitive file attachments
                        assets = release.get('assets', [])
                        for asset in assets:
                            if any(pattern in asset.get('name', '').lower() for pattern in ['.env', 'config', 'credential', 'secret', 'backup', '.sql']):
                                findings.append({
                                    "id": f"github_release_sensitive_file_{asset['id']}",
                                    "title": f"Sensitive File in Release: {asset.get('name')}",
                                    "severity": "Medium",
                                    "category": "information_disclosure",
                                    "confidence": 0.7,
                                    "description": f"Release contains potentially sensitive file",
                                    "evidence": {
                                        "file_name": asset.get('name'),
                                        "download_url": asset.get('browser_download_url'),
                                        "file_size": asset.get('size'),
                                        "release_tag": release.get('tag_name')
                                    }
                                })
                                
        except Exception as e:
            pass
        
        return findings
    
    async def _scan_gitlab_repo(self, session: aiohttp.ClientSession, repo_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scan GitLab repository (simplified implementation)"""
        findings = []
        # GitLab implementation would be similar to GitHub but using GitLab API
        # For now, returning empty to keep the implementation focused
        return findings
    
    async def _scan_bitbucket_repo(self, session: aiohttp.ClientSession, repo_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scan Bitbucket repository (simplified implementation)"""
        findings = []
        # Bitbucket implementation would be similar but using Bitbucket API
        # For now, returning empty to keep the implementation focused
        return findings
    
    def _extract_credentials_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract credentials from content using regex patterns"""
        credentials = []
        
        for cred_type, pattern in self.credential_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Get some context around the match
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].replace('\n', ' ')
                
                credentials.append({
                    'type': cred_type,
                    'value': match.group(0),
                    'context': context,
                    'position': match.start()
                })
        
        return credentials