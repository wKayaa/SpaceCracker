# VPS-Optimized SpaceCracker Guide

## 🚀 Quick Start for VPS Users

SpaceCracker v3.1 includes specialized optimizations for VPS environments with high bandwidth and processing power.

### VPS Quick Launch
```bash
# Simple one-command launch (recommended)
python vps_scanner.py domains.txt

# With custom configuration
python launch.py run domains.txt --performance-mode=vps --threads=150

# Ultra mode for powerful VPS (200 threads, 100 req/s)
python launch.py run domains.txt --performance-mode=ultra
```

### Performance Modes Comparison

| Mode | Threads | Rate Limit | Best For |
|------|---------|------------|----------|
| `low` | 10 | 2 req/s | Shared hosting, limited resources |
| `normal` | 25 | 5 req/s | Standard VPS, moderate scanning |
| `high` | 50 | 15 req/s | Good VPS, regular scanning |
| `vps` | 100 | 50 req/s | **High-bandwidth VPS (recommended)** |
| `ultra` | 200 | 100 req/s | Dedicated servers, maximum speed |
| `auto` | Varies | Varies | Auto-detects based on system resources |

### 🔧 VPS Configuration

#### Optimized Config File
Use the provided `config_vps.json` for VPS-optimized settings:
```bash
python launch.py run targets.txt --config=config_vps.json --performance-mode=vps
```

#### Key VPS Optimizations:
- **100-200 threads** for concurrent processing
- **50-100 requests/second** for high-bandwidth utilization
- **Reduced timeouts** (8s instead of 10s) for faster scanning
- **Minimal delays** (0.1-0.5s instead of 1-3s) between requests
- **HTTP enforcement** for safer mass scanning
- **Memory management** for large-scale scans

### 📱 Telegram Auto-Updates

Enable real-time monitoring on your VPS:

1. **Setup Telegram Bot:**
   ```bash
   # Talk to @BotFather on Telegram
   # Get your bot token and chat ID
   ```

2. **Configure:**
   ```json
   "telegram": {
     "enabled": true,
     "bot_token": "YOUR_BOT_TOKEN",
     "chat_id": "YOUR_CHAT_ID",
     "progress_updates": true
   }
   ```

3. **Features:**
   - Progress updates every 30 seconds
   - Live statistics (URLs/second, findings)
   - Scan completion notifications
   - Non-blocking operation

### 🌐 URL Handling

SpaceCracker now supports various input formats:

#### Supported Targets:
```bash
# IP addresses
192.168.1.1
8.8.8.8

# Domain names  
example.com
subdomain.example.org

# Full URLs
http://example.com
https://example.com/path

# Mixed file format
echo -e "192.168.1.1\nexample.com\nhttps://test.com" > targets.txt
python vps_scanner.py targets.txt
```

#### Safety Features:
- **Auto HTTPS→HTTP conversion** (safer for mass scanning)
- **Invalid target detection** with warnings
- **IP address validation**
- **Domain name validation**

### 🖥️ Enhanced Terminal Display

#### Real-time Progress:
```
🔍 EVYL SCANNER V3.1 - SCAN IN PROGRESS 🔍
======================================================

📁 File: domains.txt
⏱️ Elapsed time: 2m 15s  
📊 Progress: [████████████████████] 87.3%

📈 TOTAL STATS:
🌐 URLs processed: 15,234
🎯 Unique URLs: 12,891  
✅ URLs validated: 8,567
📉 Success rate: 89.2%

🏆 HITS FOUND (TOTAL: 156):
  ✅ AWS: 23  ✅ SendGrid: 18  ✅ SMTP: 31  ✅ Laravel: 12

💻 CPU: 78.5% | 🧠 RAM: 1,245 MB | 📡 HTTP: 48/s | ⏰ 14:23:45
======================================================
```

### 🔧 System Requirements

#### Recommended VPS Specs:
- **CPU:** 4+ cores (8+ for ultra mode)
- **RAM:** 4+ GB (8+ GB for ultra mode)  
- **Bandwidth:** Unlimited or high quota
- **OS:** Linux (Ubuntu/Debian/CentOS)

#### Resource Usage:
- **VPS Mode:** ~100 MB RAM per 1000 targets
- **Ultra Mode:** ~200 MB RAM per 1000 targets
- **CPU Usage:** 70-85% during active scanning
- **Network:** 50-100 requests/second sustained

### 📊 Performance Optimization Tips

1. **Target List Size:**
   - Small (< 1,000): Use `--performance-mode=high`
   - Medium (1,000-10,000): Use `--performance-mode=vps`  
   - Large (> 10,000): Use `--performance-mode=ultra`

2. **Memory Management:**
   - Automatic cleanup every 5 minutes
   - Monitor with `htop` or similar
   - Consider splitting very large target lists

3. **Network Optimization:**
   - Ensure DNS resolution is fast
   - Consider using public DNS (8.8.8.8, 1.1.1.1)
   - Monitor bandwidth usage

4. **Safety Considerations:**
   - Use HTTP instead of HTTPS for mass scanning
   - Respect rate limits and target servers
   - Monitor scan results for false positives

### 📈 Example VPS Scan Session

```bash
# Start VPS-optimized scan
./vps_scanner.py domains-10k.txt

# Output:
# 🚀 Starting VPS-Optimized SpaceCracker...
# 📋 Validating 10,000 targets from domains-10k.txt...
# ✅ 9,987 valid targets loaded
# ⚠️  13 invalid targets were skipped
# 
# 🔍 EVYL SCANNER V3.1 - SCAN IN PROGRESS 🔍
# Performance: VPS High-Bandwidth
# Rate: 47 URLs/second
# Expected completion: 3m 45s
```

This VPS optimization makes SpaceCracker **25-50x faster** than the original configuration while maintaining stability and accuracy.