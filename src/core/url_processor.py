from typing import List, Set
from urllib.parse import urlparse, urljoin
import re

class URLProcessor:
    """URL validation and processing utilities"""
    
    def __init__(self):
        self.valid_schemes = {'http', 'https'}
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return (
                bool(result.netloc) and
                result.scheme in self.valid_schemes and
                bool(self.url_pattern.match(url))
            )
        except Exception:
            return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL format"""
        url = url.strip()
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        return url
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    def filter_valid_urls(self, urls: List[str]) -> List[str]:
        """Filter and return only valid URLs"""
        valid_urls = []
        
        for url in urls:
            normalized = self.normalize_url(url)
            if self.validate_url(normalized):
                valid_urls.append(normalized)
        
        return valid_urls
    
    def deduplicate_urls(self, urls: List[str]) -> List[str]:
        """Remove duplicate URLs"""
        seen = set()
        unique_urls = []
        
        for url in urls:
            normalized = self.normalize_url(url)
            if normalized not in seen:
                seen.add(normalized)
                unique_urls.append(normalized)
        
        return unique_urls
    
    def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load URLs from file"""
        urls = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
        except Exception as e:
            print(f"Error loading URLs from {file_path}: {e}")
        
        return self.filter_valid_urls(self.deduplicate_urls(urls))