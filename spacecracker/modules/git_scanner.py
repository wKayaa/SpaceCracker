import requests
from .base import BaseModule
from urllib.parse import urljoin
from typing import Dict, Any

class GitScanner(BaseModule):
    module_id = "git_scanner"
    name = "Git Scanner" 
    description = "Detect possible exposed Git metadata (.git/)."
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        self.git_files = [
            '.git/config',
            '.git/HEAD',
            '.git/index',
            '.git/logs/HEAD',
            '.git/refs/heads/master',
            '.git/refs/heads/main',
            '.git/objects/',
            '.git/description'
        ]
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run Git scanner against target"""
        findings = []
        errors = []
        
        try:
            for git_file in self.git_files:
                url = urljoin(target, git_file)
                
                try:
                    response = requests.get(url, timeout=10, allow_redirects=False)
                    
                    if response.status_code == 200:
                        # Check if this looks like a Git file
                        if self._validate_git_file(git_file, response):
                            severity = "High" if git_file in ['.git/config', '.git/index'] else "Medium"
                            
                            findings.append({
                                "id": f"git_exposure_{git_file.replace('/', '_').replace('.', '_')}",
                                "title": f"Git File Exposure: {git_file}",
                                "severity": severity,
                                "category": "exposure",
                                "confidence": 0.9,
                                "description": f"Git metadata file {git_file} is publicly accessible",
                                "evidence": {
                                    "url": url,
                                    "status_code": response.status_code,
                                    "content_length": len(response.text),
                                    "content_preview": response.text[:100]
                                },
                                "recommendation": "Block access to .git directory and remove from web root"
                            })
                            
                except Exception as e:
                    errors.append(f"Failed to check {url}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Module execution failed: {str(e)}")
        
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _validate_git_file(self, filename: str, response: requests.Response) -> bool:
        """Validate that the response looks like a legitimate Git file"""
        content = response.text
        
        if filename == '.git/config':
            return '[core]' in content or 'repositoryformatversion' in content
        elif filename == '.git/HEAD':
            return content.startswith('ref:') or len(content.strip()) == 40
        elif filename == '.git/index':
            return response.headers.get('content-type', '').startswith('application/') or len(content) > 50
        elif 'refs/heads' in filename:
            return len(content.strip()) == 40  # SHA-1 hash
        elif filename == '.git/description':
            return 'Unnamed repository' in content or len(content) > 10
        
        return True  # Default to true for other files