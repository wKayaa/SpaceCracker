import requests
from typing import Dict, Optional

def fetch(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> requests.Response:
    """Simple HTTP fetch utility"""
    return requests.get(url, headers=headers or {}, timeout=timeout)

def safe_fetch(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[requests.Response]:
    """Safe HTTP fetch that returns None on error"""
    try:
        return fetch(url, headers, timeout)
    except Exception:
        return None