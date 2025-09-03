import requests
import aiohttp
import asyncio
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

def create_session() -> aiohttp.ClientSession:
    """Create an aiohttp session with default settings"""
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    connector = aiohttp.TCPConnector(
        limit=100,
        ttl_dns_cache=300,
        use_dns_cache=True,
        keepalive_timeout=30,
        enable_cleanup_closed=True
    )
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    return aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers=headers
    )