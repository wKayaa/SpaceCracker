from typing import Dict, Any
from abc import ABC, abstractmethod

class BaseModule(ABC):
    """Base class for all scanning modules"""
    
    module_id: str = "base"
    name: str = "Base Module"
    description: str = "Base module interface"
    supports_batch: bool = False
    
    def __init__(self, config: Any = None):
        self.config = config
    
    @abstractmethod
    async def run(self, target: str, config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the module against a target
        
        Returns:
            {
                "module_id": str,
                "target": str,
                "findings": [
                    {
                        "id": str,
                        "title": str,
                        "severity": "Low|Medium|High|Critical",
                        "category": "secret|exposure|cve|config",
                        "confidence": float (0.0-1.0),
                        "description": str,
                        "evidence": dict,
                        "recommendation": str
                    }
                ],
                "errors": []
            }
        """
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": [],
            "errors": []
        }