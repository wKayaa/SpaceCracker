# SpaceCracker - Advanced Web Vulnerability Scanner

SpaceCracker is a comprehensive Python tool designed for mass scanning of websites and IPs with multiple exploit modules, secret extraction, and validation capabilities.

## Features

### 🔍 **Scanning Modules**
- **GGB Scanner**: Cloud storage bucket detection (AWS S3, GCS, Azure, MinIO)
- **JS Scanner**: JavaScript file analysis and secret extraction
- **Git Scanner**: Exposed version control systems (.git, .svn, .hg)
- **CVE Exploits**: 2024-2025 CVE database with automated exploitation
- **Path Scanner**: Comprehensive vulnerable path testing

### 🔐 **Secret Extraction & Validation**
- **Regex Patterns**: 50+ secret types (AWS, SendGrid, GitHub, Stripe, etc.)
- **Live Validation**: Automated API testing for extracted secrets
- **Multi-Service Support**: SMTP, database URLs, JWT tokens, and more

### 📊 **Reporting & Notifications**
- **Multiple Formats**: JSON, TXT, CSV, and executive summaries
- **Telegram Integration**: Real-time notifications for validated findings
- **Risk Assessment**: Automated severity classification

### ⚡ **Performance & OpSec**
- **Rate Limiting**: Configurable requests per second
- **Threading**: Concurrent scanning with customizable thread count
- **Random Delays**: OpSec-friendly scanning patterns
- **Exponential Backoff**: Intelligent retry mechanisms

## Installation

```bash
# Clone the repository
git clone https://github.com/wKayaa/SpaceCracker.git
cd SpaceCracker

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x scanner.py
```

## Quick Start

```bash
# Basic scan
python scanner.py -t targets.txt

# Scan with specific modules
python scanner.py -t targets.txt --modules ggb js git

# Custom threading and rate limiting
python scanner.py -t targets.txt --threads 20 --rate-limit 5

# Enable Telegram notifications
python scanner.py -t targets.txt --telegram

# Custom paths and output
python scanner.py -t targets.txt -p custom_paths.txt -o results/
```

## Configuration

Edit `config.json` to customize:

```json
{
  "scanner": {
    "threads": 10,
    "rate_limit": 2,
    "timeout": 10,
    "max_retries": 3
  },
  "modules": {
    "ggb_scanner": true,
    "js_scanner": true,
    "git_scanner": true,
    "cve_exploits": true
  },
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

## Modules

### GGB Scanner
Detects exposed cloud storage buckets across multiple providers:
- Amazon S3
- Google Cloud Storage
- Azure Blob Storage
- MinIO instances

### JavaScript Scanner
Analyzes JS files for:
- API keys and tokens
- Database URLs
- Internal endpoints
- Email addresses
- Development artifacts

### Git Scanner
Finds exposed version control:
- Git repositories (.git/)
- Subversion (.svn/)
- Mercurial (.hg/)
- Extracts commit history and configuration

### CVE Exploits
Tests for recent vulnerabilities:
- Kubernetes exposures (CVE-2024-3177, CVE-2024-4068)
- NGINX auth bypass (CVE-2024-7646)
- MinIO authentication issues (CVE-2024-8572)
- Docker daemon exposures
- Generic API endpoints

## Secret Types Supported

- **AWS**: Access keys, secret keys, session tokens
- **SendGrid**: API keys
- **Mailgun**: API keys
- **Twilio**: Account SIDs and auth tokens
- **Stripe**: API keys (live/test)
- **GitHub/GitLab**: Personal access tokens
- **Slack/Discord**: Bot tokens and webhooks
- **Database URLs**: MongoDB, MySQL, PostgreSQL, Redis
- **SMTP**: Credentials and configurations
- **JWT**: Tokens with payload analysis
- **SSH**: Private keys
- **Generic**: API keys, bearer tokens, passwords

## Validation

SpaceCracker validates extracted secrets by:
- Making authenticated API calls
- Testing database connections
- Verifying SMTP credentials
- Analyzing JWT token validity
- AWS STS identity verification

## Output Formats

### JSON Report
Detailed machine-readable results with full metadata.

### Text Report
Human-readable summary with severity-based grouping.

### CSV Export
Validated secrets in spreadsheet format.

### Executive Summary
High-level risk assessment and recommendations.

## Telegram Integration

Set up notifications:
1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Configure in `config.json`
4. Enable with `--telegram` flag

## Performance Tuning

For powerful VPS deployments:

```bash
# High-performance scanning
python scanner.py -t targets.txt --threads 50 --rate-limit 10

# Large-scale assessment
python scanner.py -t targets.txt --threads 100 --rate-limit 20 -o results_$(date +%Y%m%d)
```

## OpSec Considerations

- Random delays between requests
- Configurable User-Agent strings
- Rate limiting to avoid detection
- Exponential backoff on failures
- Telegram notifications for stealth

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your exploit modules in `modules/`
4. Update patterns in `utils/regex_patterns.py`
5. Submit a pull request

## Legal Disclaimer

This tool is for authorized security testing only. Users are responsible for complying with applicable laws and obtaining proper authorization before scanning any systems they do not own.

## License

MIT License - see LICENSE file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/wKayaa/SpaceCracker/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/wKayaa/SpaceCracker/discussions)
- 📧 **Contact**: security@spacecracker.dev

---

**SpaceCracker v1.0.0** - Ready to crack the space between security and discovery! 🚀