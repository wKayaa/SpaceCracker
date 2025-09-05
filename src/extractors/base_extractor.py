from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import re

class BaseExtractor(ABC):
    """Base class for all credential extractors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.patterns = self._init_patterns()
        self.name = self.__class__.__name__
    
    @abstractmethod
    def _init_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for credential extraction"""
        pass
    
    @abstractmethod
    def extract(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Extract credentials from content"""
        pass
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0.0
        
        # Count frequency of each character
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_length = len(text)
        
        import math
        for count in char_counts.values():
            probability = count / text_length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _extract_by_pattern(self, content: str, pattern: str, group: int = 1) -> List[str]:
        """Extract matches using regex pattern"""
        try:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if isinstance(matches[0], tuple):
                # If pattern has groups, extract the specified group
                return [match[group-1] if len(match) >= group else match[0] for match in matches]
            return matches
        except (IndexError, re.error):
            return []
    
    def _validate_length(self, value: str, min_length: int = 10, max_length: int = 200) -> bool:
        """Validate credential length"""
        return min_length <= len(value) <= max_length
    
    def _validate_entropy(self, value: str, min_entropy: float = 3.0) -> bool:
        """Validate credential has sufficient entropy"""
        return self._calculate_entropy(value) >= min_entropy