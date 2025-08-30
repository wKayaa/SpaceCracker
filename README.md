# SpaceCracker v3.1

```
   _____                     _____                _             
  / ____|                   / ____|              | |            
 | (___   __ _ _ __   ___  | |     _ __ __ _  ___| | _____ _ __ 
  \___ \ / _` | '_ \ / _ \ | |    | '__/ _` |/ __| |/ / _ \ '__|
   ___) | (_| | |_) |  __/ | |____| |  | (_| | (__|   <  __/ |   
  |____/ \__,_| .__/ \___|  \_____|_|   \__,_|\___|_|\_\___/|_|   
              | |                                                
              |_|                                                
```

**✨ What's New in v3.1**

🔐 **Enhanced Security Testing Capabilities**
- **Advanced Laravel Scanner**: Complete security assessment for Laravel applications
- **SMTP Security Testing**: Legitimate email service security validation for authorized testing
- **Enhanced Email Service Patterns**: Extended support for AWS SES, SMTP configurations
- **Configuration Exposure Detection**: Advanced Laravel and email configuration scanning

🚀 **Performance Optimizations**  
- **2x Faster UI**: Reduced refresh rate from 4fps to 2fps for smoother performance
- **Memory Management**: Automatic memory cleanup for large-scale scans (1M+ URLs)
- **Smart Threading**: Enhanced auto-detection algorithm based on system resources
- **Connection Pooling**: Optimized HTTP connection reuse with DNS caching

🌐 **User Interface Improvements**
- **Multi-Language Support**: English/French UI via --language parameter
- **Compact Layout**: Streamlined hits display for better visibility  
- **Performance Modes**: Low/Normal/High performance profiles
- **Better Error Handling**: Improved error messages and recovery

🎯 **Usability Enhancements**
- **One-Command Launch**: Simple `python launch.py run targets.txt` for instant scanning
- **Auto-Configuration**: Intelligent defaults based on system capabilities
- **Progress Throttling**: Reduced CPU overhead during high-frequency scans
- **Memory Monitoring**: Real-time memory usage tracking and optimization

**Advanced Laravel & Email Security Framework**

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/wKayaa/SpaceCracker)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> ⚠️ **FOR AUTHORIZED TESTING ONLY** - Only use on systems you own or have explicit permission to test

---

## 🚀 Quick Start (v3.1)

### One-Command Launch (New!)
```bash
# Quick scan with auto-optimization
python launch.py run targets.txt

# High-performance scan with English UI
python launch.py run domains.txt --language=en --performance-mode=high

# French interface with custom threading  
python launch.py run targets.txt --language=fr --threads=32

# Advanced scan with all optimizations
python launch.py run targets.txt --performance-mode=high --language=en --dry-run
```

### Interactive Mode (Classic)
```bash
python launch.py
# Launches interactive wizard - perfect for first-time users
```

### CLI Mode (Traditional)
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
├── spacecracker/
│   ├── __init__.py
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
chmod +x launch.py
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