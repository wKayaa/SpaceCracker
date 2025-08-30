# SpaceCracker

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

**Advanced Modular Web Exposure & Secret Discovery Toolkit (Defensive Use Only)**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/wKayaa/SpaceCracker)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> ⚠️ **FOR AUTHORIZED TESTING ONLY** - Only use on systems you own or have explicit permission to test

---

## 🚀 Quick Start

### Interactive Mode (Default)
```bash
python launch.py
# Launches interactive wizard - perfect for first-time users
```

### CLI Mode
```bash
# Basic scan
python launch.py --targets targets.txt

# Specific modules with custom settings
python launch.py --targets targets.txt --modules js_scanner,git_scanner --threads 20

# All modules with Telegram notifications
python launch.py --targets targets.txt --modules all --telegram
```

## 📋 Features

### 🔍 **Modular Scanner Architecture**
- **Auto-Discovery**: Modules automatically registered from `spacecracker/modules/`
- **Standardized Interface**: All modules implement `BaseModule` with consistent `run()` method
- **Pluggable Design**: Drop new modules in directory - no code changes needed

### 🧪 **Available Modules**
- **`js_scanner`**: JavaScript secrets & API key extraction
- **`git_scanner`**: Exposed Git metadata detection (.git/)  
- **`ggb_scanner`**: Generic/Global bucket exposure detection
- **`cve_k8s_podescape_2024_3177`**: K8s pod escape vulnerability check (passive)

### 📊 **Standardized Reporting**
- **JSON**: Machine-readable results with full evidence
- **TXT**: Human-readable summary reports
- **CSV**: Tabular data for spreadsheet analysis
- **Severity Classification**: Low/Medium/High/Critical

### ⚡ **Performance & OpSec**  
- **Rate Limiting**: Token bucket implementation with burst support
- **Threading**: Concurrent scanning with configurable workers
- **Config-Driven**: JSON configuration for all parameters
- **Telegram Integration**: Real-time notifications for critical findings
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