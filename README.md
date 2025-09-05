# SpaceCracker V2 - Professional Credential Scanner & Exploitation Framework

```
   _____                     _____                _               __      _____  
  / ____|                   / ____|              | |              \ \    / /__ \ 
 | (___   __ _ _ __   ___  | |     _ __ __ _  ___| | _____ _ __     \ \  / /   ) |
  \___ \ / _` | '_ \ / _ \ | |    | '__/ _` |/ __| |/ / _ \ '__|     \ \/ /   / / 
  ___) | (_| | |_) |  __/ | |____| |  | (_| | (__|   <  __/ |       \  /   / /_ 
 |____/ \__,_| .__/ \___|  \_____|_|   \__,_|\___|_|\_\___/|_|        \/   |____|
             | |                                                                 
             |_|                                                                 
```

**🎯 Complete Rewrite - Professional Security Testing Suite**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/wKayaa/SpaceCracker)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> ⚠️ **FOR AUTHORIZED TESTING ONLY** - Only use on systems you own or have explicit permission to test

## ✨ What's New in V2

🔥 **Complete Architecture Rewrite**
- **Professional Modular Design**: Clean separation of concerns with dedicated modules
- **Async Processing**: High-performance asynchronous scanning engine
- **Real-time Statistics**: Live performance monitoring with formatted output
- **Advanced Exploitation**: Docker/Kubernetes infrastructure targeting

🎯 **Advanced Credential Detection**
- **Multi-Service Support**: AWS, SendGrid, Mailgun, Stripe, Twilio, GitHub, SMTP
- **Smart Validation**: Real-time credential verification with detailed reporting
- **Entropy Analysis**: Sophisticated pattern matching with confidence scoring
- **Context Awareness**: Intelligent extraction from various file formats

🚀 **Exploitation Capabilities**
- **Docker API Exploitation**: Automated container injection and scaling
- **Kubernetes Targeting**: Kubelet API abuse with pod deployment
- **Network Propagation**: Shodan integration for target discovery
- **Persistence Mechanisms**: Advanced agent deployment and stealth

🌐 **Multiple Interfaces**
- **CLI Interface**: Professional command-line tool with rich formatting
- **Web Dashboard**: Real-time monitoring with beautiful UI
- **Telegram Integration**: Instant notifications for discovered credentials
- **API Endpoints**: RESTful API for integration with other tools

## 🚀 Quick Start

### CLI Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Basic scan
python cli.py scan -t targets.txt -T 5000 -to 20

# Advanced scan with exploitation
python cli.py scan -t targets.txt -e all --telegram -o results.json

# Single credential test
python cli.py test -t aws -k AKIA... -s ... --verbose

# Exploitation only
python cli.py exploit -t target.com -e docker
```

### Web Interface
```bash
# Start web panel
python panel.py --host 0.0.0.0 --port 8080

# Access dashboard
http://localhost:8080
```

### Docker Deployment
```bash
# Build and run
docker build -t spacecracker-v2 .
docker run -p 8080:8080 spacecracker-v2
```

## 📊 Real-time Statistics Output

```
Crack (#2025090503661) stats:
⚙️ Last Update: 2025-09-05 03:27:20
⚙️ Timeout: 20
⚙️ Threads: 5000
⚙️ Status: scanning

ℹ️ Hits: 147
ℹ️ Checked Paths: 1,247,832
ℹ️ Checked URLs: 8,921
ℹ️ Invalid URLs: 234
ℹ️ Total URLs: 9,155/250,000

🐳 Docker Infected: 23
☸️ K8s Pods Infected: 7

⏱️ Progression: 3.66%
⏱️ ETA: 2:34:17

📊 AVG Checks/sec: 1,247
📊 AVG URL/sec: 89
```

## 🔍 Credential Detection Example

```
✨ New AWS Hit (#2025090503661)

👉 USER: AKIA1234567890EXAMPLE
👉 PASS: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
🔐 ACCESS LEVEL: Full SES + SNS

📊 3 regions with access

🌍 US-EAST-1:
🤞 STATUS - HEALTHY
📈 QUOTA - (200 per day - 0 sent today - 14 mail/s)
✅ VERIFIED EMAILS: admin@example.com, noreply@example.com
📧 VERIFIED DOMAINS: example.com

🚀 HIT WORKS: Yes
ℹ️ URL - https://target.com/.env
🆔 Crack ID - #2025090503661

✨ SpaceCracker.co - @SpaceCracker
```

## 🏗️ Architecture

### Directory Structure
```
SpaceCracker/
├── src/
│   ├── core/               # Core scanning engine
│   │   ├── scanner.py      # Async scanning engine
│   │   ├── stats_manager.py # Real-time statistics
│   │   └── orchestrator.py # Central coordination
│   ├── extractors/         # Credential extractors
│   │   ├── aws_extractor.py
│   │   ├── sendgrid_extractor.py
│   │   └── ...
│   ├── validators/         # Credential validators
│   │   ├── aws/
│   │   │   └── ses_validator.py
│   │   └── ...
│   ├── exploits/          # Exploitation modules
│   │   ├── docker_exploit.py
│   │   └── kubelet_exploit.py
│   ├── network/           # Network scanning
│   │   └── shodan_scanner.py
│   ├── reporters/         # Output formatting
│   │   ├── console_reporter.py
│   │   └── telegram_reporter.py
│   └── web/              # Web interface
│       ├── app.py
│       └── templates/
├── config/               # Configuration files
├── cli.py               # Main CLI interface
└── panel.py            # Web panel launcher
```

### Key Components

**Scanner Engine** (`src/core/scanner.py`)
- Asynchronous HTTP client with connection pooling
- Intelligent rate limiting and error handling
- Dynamic load balancing across multiple threads
- SSL/TLS configuration with custom contexts

**Statistics Manager** (`src/core/stats_manager.py`)
- Real-time performance tracking
- Formatted console output with progress indicators
- ETA calculation and throughput analysis
- Crack ID generation for finding correlation

**Extractors** (`src/extractors/`)
- Service-specific credential pattern matching
- Entropy analysis for false positive reduction
- Context-aware extraction from various formats
- Confidence scoring based on pattern complexity

**Validators** (`src/validators/`)
- Real-time credential verification
- Service-specific API testing
- Detailed capability assessment
- Region-aware testing for cloud providers

**Exploitation** (`src/exploits/`)
- Docker API abuse with container injection
- Kubernetes exploitation via Kubelet API
- Persistence and stealth mechanisms
- Network propagation and lateral movement

## 🔧 Configuration

### settings.yaml
```yaml
scanner:
  threads: 5000
  timeout: 20
  max_urls: 250000
  rate_limit: 100

api_keys:
  shodan: "your_shodan_api_key"
  telegram:
    bot_token: "your_bot_token"
    chat_id: "your_chat_id"

validation:
  enabled: true
  aws:
    regions: ["us-east-1", "us-west-2", "eu-west-1"]

exploitation:
  docker:
    enabled: false
    ports: [2375, 2376, 2377]
  kubernetes:
    enabled: false
    ports: [10250, 10255]
```

## 🎯 Supported Services

### Cloud Providers
- **AWS**: Access Keys, Secret Keys, Session Tokens, SES Configuration
- **Google Cloud**: Service Account Keys, API Keys
- **Azure**: Connection Strings, Access Keys

### Communication Services  
- **SendGrid**: API Keys with quota verification
- **Mailgun**: API Keys and domain validation
- **Twilio**: Account SID and Auth Tokens
- **SMTP**: Credentials and server configuration

### Payment Processors
- **Stripe**: Secret Keys, Publishable Keys, Restricted Keys
- **PayPal**: Client ID and Secret combinations

### Development Platforms
- **GitHub**: Personal Access Tokens, OAuth Tokens
- **GitLab**: Access Tokens and Deploy Keys
- **Docker Hub**: Registry credentials

### Databases
- **PostgreSQL**: Connection strings and credentials
- **MySQL**: Database URLs and authentication
- **MongoDB**: Connection strings with auth
- **Redis**: Connection URLs and passwords

## 🔬 Advanced Features

### Network Discovery
```bash
# Shodan integration for target discovery
python cli.py scan --shodan-discovery docker,k8s -t discovered_targets.txt

# Custom Shodan queries
python cli.py scan --shodan-query "port:2375 Docker" -e docker
```

### Exploitation Workflows
```bash
# Docker infrastructure targeting
python cli.py exploit -t targets.txt -e docker --scale 5

# Kubernetes cluster exploitation  
python cli.py exploit -t k8s_targets.txt -e k8s --namespaces all

# Combined reconnaissance and exploitation
python cli.py scan -t broad_targets.txt -e all --persist
```

### Web Dashboard Features
- **Real-time Monitoring**: Live statistics and progress tracking
- **Interactive Results**: Clickable findings with detailed information
- **Export Capabilities**: JSON, CSV, and PDF report generation
- **Multi-user Support**: Role-based access and session management

### Telegram Integration
```bash
# Setup Telegram notifications
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Enable notifications
python cli.py scan -t targets.txt --telegram
```

## 🛡️ Security Considerations

### Responsible Usage
- Always obtain explicit permission before testing
- Use only on systems you own or are authorized to test
- Respect rate limits and avoid denial of service
- Follow responsible disclosure for any findings

### Operational Security
- Use VPN or proxy for attribution avoidance
- Implement proper logging and audit trails
- Secure credential storage and transmission
- Regular updates for detection patterns

### Legal Compliance
- Ensure compliance with local laws and regulations
- Obtain proper authorization documentation
- Maintain clear scope boundaries
- Document all testing activities

## 📈 Performance Optimization

### Hardware Recommendations
- **CPU**: Multi-core processor (8+ cores recommended)
- **RAM**: 16GB+ for large-scale scans
- **Network**: High-bandwidth connection for optimal throughput
- **Storage**: SSD for faster I/O operations

### Tuning Parameters
```yaml
# High-performance configuration
scanner:
  threads: 10000
  timeout: 10
  connection_pool_size: 200
  dns_cache_ttl: 600
  
performance:
  batch_size: 500
  max_retries: 2
  backoff_factor: 0.5
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
```bash
# Clone repository
git clone https://github.com/wKayaa/SpaceCracker.git
cd SpaceCracker

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black src/ tests/
isort src/ tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for authorized security testing only. Users are responsible for ensuring they have proper authorization before testing any systems. The authors are not responsible for any misuse or damage caused by this tool.

---

**SpaceCracker V2** - Built with ❤️ for the security community
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run a quick scan (easiest way)
./spacecracker_simple demo_targets.txt

# 3. Preview what it would do (dry run)
./spacecracker_simple demo_targets.txt --dry-run

# 4. Scan your own targets
echo "https://your-target.com" > my_targets.txt
./spacecracker_simple my_targets.txt

# 5. For guided setup
python launch.py --interactive
```

---

## 🚀 Advanced Usage

### Quick Commands
```bash
# Quick scan with auto-optimization
python launch.py run targets.txt

# High-performance scan with English UI
python launch.py run domains.txt --language=en --performance-mode=high

# French interface with custom threading  
python launch.py run targets.txt --language=fr --threads=32

# Show scan plan without executing
python launch.py run targets.txt --dry-run
```

### Interactive Mode
```bash
python launch.py --interactive
# Launches interactive wizard - perfect for first-time users
```

### Traditional CLI Mode
```bash
# Target a single URL
python launch.py --targets https://example.com --language=fr

# Scan from file with specific modules  
python launch.py --targets targets.txt --modules laravel_scanner,smtp_scanner

# High-performance scan
python launch.py --targets large_targets.txt --performance-mode=high --threads=100
```

---

## 📋 Features

### 🎯 **Target Discovery & Exploitation (v3.1)**
- **Laravel Applications**: .env files, debug interfaces, configuration exposure
- **Email Services**: SMTP configuration testing, AWS SES security assessment  
- **Kubernetes Clusters**: Service account tokens, API enumeration, pod escape
- **AWS Infrastructure**: Metadata service, IAM credentials, S3 enumeration
- **Web Applications**: Git exposure, configuration files, backup discovery
- **Generic Buckets**: Cloud storage exposure across multiple providers

### 🔐 **Credential Harvesting & Validation**
- **30+ Advanced Regex Patterns**: AWS keys, API tokens, database URLs, SMTP configs
- **Email Service Detection**: SendGrid, Mailgun, AWS SES, SMTP credentials
- **Laravel Configuration**: Environment files, database credentials, mail settings
- **Real-time Validation**: Live credential verification during scanning
- **Context Analysis**: Line numbers, surrounding code, source URLs

### ✅ **Enhanced Validation Engine (v3.1)**
- **AWS SES**: Credential validation, sending quota analysis, verified email enumeration  
- **Email Services**: SendGrid, Mailgun, Postmark, SparkPost, Brevo validation
- **SMTP Security**: Connection testing, authentication validation, open relay detection
- **Database**: MySQL, PostgreSQL, MongoDB, Redis connections
- **SMS Services**: Twilio account validation

### 📊 **High-Performance Progress Display (v3.1)**
```
🔍 EVYL SCANNER V3.1 - SCAN IN PROGRESS 🔍

📁 File: domains-list-hq.txt
⏱️ Elapsed time: 73s 33m 21s  
📊 Progress: [████████████████████████████████████] 88.4%

📈 TOTAL STATS:
🌐 URLs processed: 5,566,407
🎯 Unique URLs: 4,475,128
✅ URLs validated: 1,001,339
📉 Success rate: 88.4%

🏆 HITS FOUND (TOTAL: 2,808):
✅ AWS: 342  ✅ SendGrid: 156  ✅ Brevo: 89  ✅ SMTP: 134
✅ Postmark: 78  ✅ SparkPost: 45  ✅ Mailgun: 67  ✅ Laravel: 32

💻 CPU: 100.0% | 🧠 RAM: 8141.2 MB | 📡 HTTP: 2,341/s | ⏰ 15:30:45
```

### ⚡ **Performance & OpSec (v3.1)**  
- **Auto-Detection**: Intelligent system resource detection and optimization
- **Performance Modes**: Low/Normal/High/Auto profiles with smart threading
- **Memory Management**: Automatic cleanup for large-scale scans (1M+ URLs)
- **Rate Limiting**: Token bucket implementation with burst support
- **Multi-Language**: English/French UI support
- **Connection Pooling**: HTTP connection reuse with DNS caching

---

## 📖 Usage Examples (v3.1)

### Quick Commands
```bash
# List available modules
python launch.py --list-modules

# Quick scan with auto-configuration  
python launch.py run targets.txt

# High-performance French interface
python launch.py run targets.txt --language=fr --performance-mode=high

# Dry run to see execution plan
python launch.py run targets.txt --dry-run --language=en
```

### Traditional CLI Mode
```bash
# Basic scan with new Laravel and SMTP modules
python launch.py --targets targets.txt

# Specific modules with multi-language support
python launch.py --targets targets.txt --modules laravel_scanner,smtp_scanner --language=fr

# High-performance mode with all modules
python launch.py --targets targets.txt --modules all --performance-mode=high --threads 50
```

### Interactive Wizard (Multi-Language)
```bash
python launch.py --interactive --language=fr
# Launches French interactive wizard
```

---

## 🧪 **Available Modules (v3.1)**

### New Security Modules
- **`laravel_scanner`**: Complete Laravel security assessment (.env, debug mode, configs)
- **`smtp_scanner`**: Email service security validation (SMTP, AWS SES, SendGrid patterns)

### Enhanced Existing Modules  
- **`js_scanner`**: JavaScript secrets & API key extraction
- **`git_scanner`**: Exposed Git metadata detection (.git/)  
- **`ggb_scanner`**: Generic/Global bucket exposure detection
- **`cve_k8s_podescape_2024_3177`**: K8s pod escape vulnerability check

---

## 📋 Command Line Options (v3.1)

### Quick Commands
```bash
# Quick launch command with auto-configuration
python launch.py run <targets_file> [options]

Options for 'run' command:
  --language {en,fr}              UI language (English/French)
  --performance-mode {low,normal,high,auto}  Performance profile
  --threads N                     Override thread count
  --telegram                      Enable Telegram notifications
  --dry-run                       Show scan plan without executing
```

### Traditional Arguments
```bash
Target Options:
-t, --targets FILE              Target file containing URLs/domains
-m, --modules MODULES           Comma-separated modules or "all"

Performance Options (Enhanced):
-T, --threads N                 Number of threads (default: auto-detected)
-r, --rate-limit N              Requests per second (default: auto-detected)  
-b, --burst N                   Rate limit burst (default: 20)
--performance-mode MODE         Performance profile: low/normal/high/auto

New v3.1 Options:
--language {en,fr}              UI language support (default: en)
--list-modules                  List all available modules
--dry-run                       Show execution plan without running
--interactive                   Force interactive wizard mode

Output Options:
-o, --output-dir DIR            Output directory (default: results)
-f, --formats FORMATS           Output formats: json,txt,csv (default: all)

Integration:
-g, --telegram                  Enable Telegram notifications
-s, --severity-filter LEVEL     Minimum severity to report
--no-color                      Disable colored output
```
---

## 📁 Project Structure

```
spacecracker/
├── launch.py                 # Universal entrypoint
├── spacecracker_simple       # Simple launcher (easiest)
├── spacecracker/
│   ├── __init__.py
│   ├── __main__.py          # Module entry point
│   ├── version.py           
│   ├── cli.py               # CLI interface & wizard
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── registry.py      # Module auto-discovery
│   │   ├── runner.py        # Scan orchestration
│   │   ├── reporting.py     # Multi-format reports
│   │   └── rate_limiter.py  # Token bucket rate limiting
│   ├── modules/
│   │   ├── base.py          # BaseModule interface
│   │   ├── js_scanner.py    # JavaScript secrets
│   │   ├── git_scanner.py   # Git exposure
│   │   ├── ggb_scanner.py   # Storage buckets
│   │   └── cve_*.py         # CVE modules
│   └── utils/
│       ├── http.py          # HTTP utilities
│       └── text.py          # Text processing
├── configs/
│   └── config.example.json  # Example configuration
├── results/                 # Scan output directory
├── tests/                   # Test suite
└── scripts/                 # Helper scripts
```

---

## 🛠 Installation & Setup

### Clone & Install
```bash
git clone https://github.com/wKayaa/SpaceCracker.git
cd SpaceCracker
pip install -r requirements.txt
chmod +x launch.py spacecracker_simple
```

### Three Ways to Launch
```bash
# 1. Simplest way (recommended for quick scans)
./spacecracker_simple targets.txt

# 2. Full CLI interface
python launch.py run targets.txt

# 3. As Python module  
python -m spacecracker run targets.txt
```

### Quick Test
```bash
# Test with demo target
./spacecracker_simple demo_targets.txt --dry-run
```

### Generate Sample Targets
```bash
./scripts/generate_sample_targets.sh
```

### Docker Support
```bash
docker-compose up --build
```

---

## 📖 Usage Examples

### Interactive Wizard
```bash
python launch.py
# Follow prompts to configure scan
```

### CLI Examples
```bash
# List available modules
python launch.py --list-modules

# Dry run (show plan without execution)
python launch.py --targets targets.txt --dry-run

# Quick scan with specific modules
python launch.py --targets https://example.com --modules js_scanner,git_scanner

# High-performance scan
python launch.py --targets targets.txt --threads 50 --rate-limit 10

# Custom output and formats
python launch.py --targets targets.txt --output-dir results_2024 --formats json,csv
```

### Configuration File
```bash
# Use custom config
python launch.py --config configs/my_config.json --targets targets.txt
```
---

## ⚙️ Configuration

Example `config.json`:
```json
{
  "threads": 50,
  "rate_limit": {
    "requests_per_second": 10,
    "burst": 20
  },
  "modules": ["js_scanner", "git_scanner", "ggb_scanner"],
  "secrets": {
    "patterns": [
      {"name": "AWS Access Key", "regex": "AKIA[0-9A-Z]{16}"},
      {"name": "GitHub Token", "regex": "ghp_[a-zA-Z0-9]{36}"}
    ],
    "entropy_min": 4.0
  },
  "telegram": {
    "enabled": false,
    "bot_token": "env:TELEGRAM_BOT_TOKEN",
    "chat_id": "env:TELEGRAM_CHAT_ID",
    "notify_severity_min": "High"
  },
  "outputs": {
    "directory": "results",
    "formats": ["json", "txt", "csv"]
  }
}
```

---

## 🔌 Extending with New Modules

### Create a New Module
```python
# spacecracker/modules/my_scanner.py
from .base import BaseModule

class MyScanner(BaseModule):
    module_id = "my_scanner"
    name = "My Custom Scanner"
    description = "Custom vulnerability scanner"
    
    async def run(self, target, config, context):
        return {
            "module_id": self.module_id,
            "target": target,
            "findings": [
                {
                    "id": "finding_1",
                    "title": "Custom Finding",
                    "severity": "Medium",
                    "category": "exposure", 
                    "confidence": 0.8,
                    "description": "Found something interesting",
                    "evidence": {"url": target},
                    "recommendation": "Fix this issue"
                }
            ],
            "errors": []
        }
```

Module will be automatically discovered and available via `--list-modules`!

---

## 📊 Sample Output

### JSON Report Structure
```json
{
  "metadata": {
    "started_at": "2024-01-15 10:30:45",
    "finished_at": "2024-01-15 10:35:20", 
    "targets": 3,
    "modules": ["js_scanner", "git_scanner"],
    "version": "0.1.0"
  },
  "summary": {
    "total_findings": 5,
    "by_severity": {"High": 2, "Medium": 2, "Low": 1},
    "errors": 0
  },
  "findings": [...]
}
```

### Text Report Preview
```
================================================================================
SPACECRACKER SCAN RESULTS
================================================================================
Started: 2024-01-15 10:30:45
Targets: 3
Modules: js_scanner, git_scanner

SUMMARY
----------------------------------------
Total Findings: 5
Severity Breakdown:
  High: 2
  Medium: 2
  Low: 1
```

---

## ⚡ Quick Reference

### Most Common Commands
```bash
# Quick scan (recommended)
./spacecracker_simple targets.txt

# Preview scan plan
./spacecracker_simple targets.txt --dry-run

# High performance scan
python launch.py run targets.txt --performance-mode=high

# Interactive setup (beginner-friendly)
python launch.py --interactive

# List available modules
python launch.py --list-modules
```

### Common Target Files
```bash
# Create your own targets file
echo "https://your-domain.com" > my_targets.txt
echo "https://sub.your-domain.com" >> my_targets.txt

# Use provided examples
./spacecracker_simple demo_targets.txt
./spacecracker_simple examples/targets.txt
```

---

## 🧪 Testing

```bash
# Run config tests
python tests/test_config.py

# Run registry tests  
python tests/test_registry.py

# Test CLI functionality
python launch.py --version
python launch.py --list-modules
python launch.py --targets test_target.txt --dry-run
```

---

## ❓ Troubleshooting

### Common Issues
```bash
# Permission error on launcher
chmod +x spacecracker_simple launch.py

# Missing dependencies
pip install -r requirements.txt

# Can't connect to targets
# Check network connectivity and target availability

# No findings in results
# Normal for test targets - try with known vulnerable applications
```

### Getting Help
```bash
# General help
python launch.py --help

# Run command help  
python launch.py run --help

# List all available modules
python launch.py --list-modules
```

---

## 📱 Telegram Integration

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get chat ID from [@userinfobot](https://t.me/userinfobot)  
3. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```
4. Enable in config or use `--telegram` flag

---

## ⚠️ Legal & Compliance

- **Authorization Required**: User must confirm they have permission during interactive wizard
- **Defensive Only**: No active exploit payloads - only passive checks and safe validation
- **Disclaimer**: Tool includes clear usage warnings and authorization prompts

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/my-module`)
3. Add your module in `spacecracker/modules/my_module.py`
4. Add tests in `tests/`
5. Submit pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Star ⭐ this repository if it helps your security assessments!**