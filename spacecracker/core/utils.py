import datetime
import re
import ipaddress
from typing import List, Dict, Any
from urllib.parse import urlparse, urlunparse

def severity_order(s: str):
    """Get numeric severity order"""
    ranks = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    return ranks.get(s, 1)

def format_timestamp(ts=None):
    """Format timestamp for output"""
    if ts is None:
        ts = datetime.datetime.now()
    return ts.strftime("%Y-%m-%d %H:%M:%S")

def deduplicate_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate findings based on id"""
    seen = set()
    deduped = []
    
    for finding in findings:
        finding_id = finding.get('id', '')
        if finding_id not in seen:
            seen.add(finding_id)
            deduped.append(finding)
    
    return deduped

def is_valid_ip(ip_string: str) -> bool:
    """Check if string is a valid IP address"""
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

def is_valid_domain(domain: str) -> bool:
    """Check if string is a valid domain name"""
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    return bool(domain_pattern.match(domain)) and len(domain) <= 255

def normalize_url(target: str, force_http: bool = False) -> str:
    """
    Normalize and validate URL/IP/domain input
    
    Args:
        target: Input target (URL, IP, or domain)
        force_http: Force HTTP instead of HTTPS for safety
    
    Returns:
        Normalized URL string
    """
    target = target.strip()
    
    # If it's already a full URL, parse and validate
    if target.startswith(('http://', 'https://')):
        try:
            parsed = urlparse(target)
            if not parsed.netloc:
                raise ValueError("Invalid URL: missing hostname")
            
            # For safety, convert HTTPS to HTTP if force_http is True
            if force_http and parsed.scheme == 'https':
                parsed = parsed._replace(scheme='http')
                return urlunparse(parsed)
            
            return target
        except Exception as e:
            raise ValueError(f"Invalid URL format: {e}")
    
    # Check if it's an IP address
    if is_valid_ip(target):
        scheme = 'http' if force_http else 'http'  # Always use HTTP for IPs for safety
        return f"{scheme}://{target}"
    
    # Check if it's a domain
    if is_valid_domain(target):
        scheme = 'http' if force_http else 'http'  # Default to HTTP for safety
        return f"{scheme}://{target}"
    
    # Try to extract domain from partial URLs
    if '/' in target or '.' in target:
        # Remove protocol if exists but incomplete
        if target.startswith(('http:', 'https:')):
            target = target.replace('http:', '').replace('https:', '').lstrip('/')
        
        # Extract hostname part
        hostname = target.split('/')[0]
        if is_valid_domain(hostname) or is_valid_ip(hostname):
            scheme = 'http' if force_http else 'http'
            return f"{scheme}://{hostname}"
    
    raise ValueError(f"Invalid target format: {target}")

def validate_target_list(targets: List[str], force_http: bool = False) -> List[str]:
    """
    Validate and normalize a list of targets
    
    Args:
        targets: List of target URLs/IPs/domains
        force_http: Force HTTP instead of HTTPS for safety
    
    Returns:
        List of normalized, valid URLs
    """
    normalized_targets = []
    errors = []
    
    for target in targets:
        try:
            normalized = normalize_url(target, force_http)
            normalized_targets.append(normalized)
        except ValueError as e:
            errors.append(f"Skipping invalid target '{target}': {e}")
    
    if errors:
        print("URL Validation Warnings:")
        for error in errors:
            print(f"  - {error}")
    
    return normalized_targets