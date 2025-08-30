from .base import BaseModule
import requests
from typing import Dict, Any

class CVEK8SPodEscape20243177(BaseModule):
    module_id = "cve_k8s_podescape_2024_3177"
    name = "K8s Pod Escape CVE-2024-3177"
    description = "Passive indicator scan for K8s pod escape exposure (placeholder)."
    supports_batch = True
    
    def __init__(self, config: Any = None):
        super().__init__(config)
        self.k8s_indicators = [
            '/api/v1/namespaces',
            '/api/v1/pods',
            '/api/v1/nodes',
            '/metrics',
            '/healthz',
            '/.well-known/k8s'
        ]
    
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run K8s pod escape CVE check against target"""
        findings = []
        errors = []
        
        try:
            # Check for Kubernetes API endpoints
            for endpoint in self.k8s_indicators:
                try:
                    url = target.rstrip('/') + endpoint
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code in [200, 401, 403]:
                        # Look for k8s API indicators
                        if self._check_k8s_api(response):
                            severity = "High" if response.status_code == 200 else "Medium"
                            
                            findings.append({
                                "id": f"k8s_api_exposure_{endpoint.replace('/', '_')}",
                                "title": f"Kubernetes API Exposure: {endpoint}",
                                "severity": severity,
                                "category": "cve",
                                "confidence": 0.8,
                                "description": f"Kubernetes API endpoint {endpoint} accessible, potential CVE-2024-3177 exposure",
                                "evidence": {
                                    "url": url,
                                    "status_code": response.status_code,
                                    "headers": dict(response.headers),
                                    "content_snippet": response.text[:200]
                                },
                                "recommendation": "Secure Kubernetes API access and review pod security policies"
                            })
                            
                except Exception as e:
                    errors.append(f"Failed to check {endpoint}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Module execution failed: {str(e)}")
        
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": findings,
            "errors": errors
        }
    
    def _check_k8s_api(self, response: requests.Response) -> bool:
        """Check if response indicates Kubernetes API"""
        content = response.text.lower()
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        
        # Check for k8s API indicators in content
        k8s_indicators = [
            'kubernetes',
            'apiversion',
            'kind": "',
            'metadata',
            'namespace',
            'pod',
            'node'
        ]
        
        for indicator in k8s_indicators:
            if indicator in content:
                return True
        
        # Check headers
        if 'application/json' in headers.get('content-type', ''):
            return 'kubernetes' in content or 'apiversion' in content
            
        return False