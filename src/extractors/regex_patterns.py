"""
Centralized regex patterns for credential extraction
"""

# AWS Patterns
AWS_PATTERNS = {
    'access_key': r'(AKIA[0-9A-Z]{16})',
    'secret_key': r'([A-Za-z0-9/+=]{40})',
    'session_token': r'(ASIA[0-9A-Z]{16})',
    'mws_key': r'(AMZN\.MWS\.[a-f0-9\-]{8}\-[a-f0-9\-]{4}\-[a-f0-9\-]{4}\-[a-f0-9\-]{4}\-[a-f0-9\-]{12})',
}

# SendGrid Patterns
SENDGRID_PATTERNS = {
    'api_key': r'(SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43})',
}

# Mailgun Patterns
MAILGUN_PATTERNS = {
    'api_key': r'key-([a-f0-9]{32})',
    'domain': r'([a-zA-Z0-9.-]+\.mailgun\.org)',
}

# Stripe Patterns
STRIPE_PATTERNS = {
    'secret_key': r'(sk_live_[0-9a-zA-Z]{24})',
    'publishable_key': r'(pk_live_[0-9a-zA-Z]{24})',
    'restricted_key': r'(rk_live_[0-9a-zA-Z]{24})',
}

# Twilio Patterns
TWILIO_PATTERNS = {
    'account_sid': r'(AC[a-f0-9]{32})',
    'auth_token': r'([a-f0-9]{32})',
}

# GitHub Patterns
GITHUB_PATTERNS = {
    'personal_token': r'(ghp_[A-Za-z0-9_]{36})',
    'oauth_token': r'(gho_[A-Za-z0-9_]{36})',
    'user_token': r'(ghu_[A-Za-z0-9_]{36})',
    'server_token': r'(ghs_[A-Za-z0-9_]{36})',
    'refresh_token': r'(ghr_[A-Za-z0-9_]{36})',
}

# SMTP Patterns
SMTP_PATTERNS = {
    'url': r'smtp://([^:\s]+):([^@\s]+)@([^:\s]+)(?::(\d+))?',
    'config_host': r'smtp[_-]?host["\']?\s*[:=]\s*["\']?([^"\'>\s]+)["\']?',
    'config_user': r'smtp[_-]?(?:user|username)["\']?\s*[:=]\s*["\']?([^"\'>\s]+)["\']?',
    'config_pass': r'smtp[_-]?(?:pass|password)["\']?\s*[:=]\s*["\']?([^"\'>\s]+)["\']?',
    'config_port': r'smtp[_-]?port["\']?\s*[:=]\s*["\']?(\d+)["\']?',
}

# Database Patterns
DATABASE_PATTERNS = {
    'mysql': r'mysql://([^:\s]+):([^@\s]+)@([^:\s]+)(?::(\d+))?/([^?\s]+)',
    'postgres': r'postgres(?:ql)?://([^:\s]+):([^@\s]+)@([^:\s]+)(?::(\d+))?/([^?\s]+)',
    'mongodb': r'mongodb://([^:\s]+):([^@\s]+)@([^:\s]+)(?::(\d+))?/([^?\s]+)',
    'redis': r'redis://([^:\s]+):([^@\s]+)@([^:\s]+)(?::(\d+))?/(\d+)',
}

# JWT Patterns
JWT_PATTERNS = {
    'token': r'(eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*)',
}

# Generic API Key Patterns
GENERIC_PATTERNS = {
    'api_key': r'api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
    'secret_key': r'secret[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
    'auth_token': r'auth[_-]?token["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
    'bearer_token': r'Bearer\s+([A-Za-z0-9_\-\.]{20,})',
}

# All patterns combined
ALL_PATTERNS = {
    'aws': AWS_PATTERNS,
    'sendgrid': SENDGRID_PATTERNS,
    'mailgun': MAILGUN_PATTERNS,
    'stripe': STRIPE_PATTERNS,
    'twilio': TWILIO_PATTERNS,
    'github': GITHUB_PATTERNS,
    'smtp': SMTP_PATTERNS,
    'database': DATABASE_PATTERNS,
    'jwt': JWT_PATTERNS,
    'generic': GENERIC_PATTERNS,
}