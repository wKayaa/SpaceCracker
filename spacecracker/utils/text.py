def truncate(s: str, length: int = 120) -> str:
    """Truncate string to specified length"""
    return s if len(s) <= length else s[:length] + "..."

def clean_text(text: str) -> str:
    """Clean text for safe display"""
    return text.replace('\r', '').replace('\n', ' ').strip()

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except:
        return url