# SpaceCracker Pro - Advanced Pentesting Suite

## 🚀 What's New in Pro Edition

SpaceCracker has been completely transformed into **SpaceCracker Pro** - a comprehensive penetration testing suite with professional-grade features and a beautiful web interface.

### 🎨 Professional Web Interface
- **Dark Pink Theme**: Modern gradient design with professional aesthetics
- **Real-time Dashboard**: Live statistics, charts, and progress monitoring
- **Interactive Scan Interface**: Drag-drop file uploads, module selection, advanced configuration
- **Comprehensive Results Viewer**: Filtering, pagination, detailed analysis, export functionality
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 🔧 Enhanced Core Features

#### New Scanning Modules
- **Path Scanner**: Intelligent directory/file discovery with wordlist support and content analysis
- **Exploit Runner**: Automated exploit execution with sample vulnerabilities (SQLi, XSS, LFI)
- **Credential Scraper**: Advanced secret extraction with 20+ patterns for API keys, tokens, credentials
- **API Checkers**: Validation for AWS, SMTP, Stripe, Twilio, Nexmo, SNS credentials

#### Advanced Configuration
- **YAML Support**: Enhanced configuration system with environment variable resolution
- **Plugin Architecture**: Auto-discovery module system for easy extension
- **Performance Optimization**: Async operations with proper session management
- **Wordlist Management**: Built-in wordlists for common paths and admin panels

### 🎯 Key Improvements

1. **Modular Architecture**: Clean separation of concerns with plugin system
2. **Async Operations**: Full asyncio implementation for better performance  
3. **Professional UI**: Commercial-grade web interface ready for enterprise use
4. **Enhanced Reporting**: Multiple export formats (JSON, CSV) with detailed analysis
5. **Real-time Monitoring**: Live progress tracking and statistics updates
6. **Mobile Responsive**: Works on all devices with adaptive layout

### 🛠 Technical Stack

- **Backend**: Flask with Blueprint architecture
- **Frontend**: Vanilla JS with Chart.js for visualizations
- **Styling**: Custom CSS with pink dark theme
- **Configuration**: YAML/JSON with environment variable support
- **Scanning**: Async HTTP with aiohttp and proper session management

### 📊 Interface Screenshots

![Dashboard](https://github.com/user-attachments/assets/bc0af9c2-283e-45ec-a074-638a54a6ec31)
*Professional dashboard with real-time statistics and pink dark theme*

![Scan Interface](https://github.com/user-attachments/assets/2d74d17a-fad2-44cb-b37f-f823bf6cb892)
*Advanced scan configuration with module selection and file upload*

### 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**:
   Edit `config.yaml` for your environment

3. **Launch Web UI**:
   ```bash
   python run_webui.py
   ```

4. **Access Dashboard**:
   Open http://127.0.0.1:8080 in your browser

### 🎨 Theme Colors
- **Primary Background**: #1A1A1D
- **Accent Primary**: #C3073F  
- **Accent Secondary**: #950740
- **Border/Tertiary**: #6F2232
- **Secondary Background**: #4E4E50

### 📋 Available Modules

| Module | Description | Batch Support |
|--------|-------------|---------------|
| Path Scanner | Intelligent directory discovery | ✅ |
| Exploit Runner | Automated vulnerability exploitation | ✅ |
| Credential Scraper | API keys, tokens, secrets extraction | ✅ |
| Laravel Scanner | Laravel-specific security assessment | ✅ |
| SMTP Scanner | Email service security validation | ✅ |
| Git Scanner | Exposed Git metadata detection | ✅ |
| JavaScript Scanner | JS file secret extraction | ✅ |
| GGB Scanner | Global bucket exposure detection | ✅ |

### 🔒 Security & Compliance

- **Authorization Prompts**: Built-in permission validation
- **Safe Operations**: No destructive payloads by default
- **Ethical Usage**: Clear usage warnings and disclaimers
- **Audit Trail**: Comprehensive logging and reporting

This transformation makes SpaceCracker Pro ready for professional penetration testing engagements with enterprise-grade features and a polished user experience.