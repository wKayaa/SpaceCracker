#!/usr/bin/env python3
"""
SpaceCracker Test Suite
Comprehensive testing of all modules and functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test all module imports"""
    print("🧪 Testing module imports...")
    
    try:
        from modules.scanner_base import SpaceCracker
        from modules.ggb_scanner import GGBScanner
        from modules.js_scanner import JSScanner
        from modules.git_scanner import GitScanner
        from modules.cve_exploits import CVEExploits
        from modules.validators import SecretValidator
        from utils.regex_patterns import RegexPatterns
        from utils.rate_limiter import RateLimiter
        from utils.telegram_bot import TelegramBot
        from utils.reporting import Reporter
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_regex_patterns():
    """Test regex pattern functionality"""
    print("\n🔍 Testing regex patterns...")
    
    try:
        patterns = RegexPatterns()
        
        # Test secret extraction
        test_content = """
        AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
        aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        SENDGRID_API_KEY=SG.abcdefghijklmnop1234567890.ABCDEFGHIJKLMNOP1234567890123456789012345
        DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
        JWT_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ
        """
        
        secrets = patterns.extract_secrets(test_content)
        print(f"✅ Found {len(secrets)} secrets")
        
        # Test supported types
        supported_types = patterns.get_supported_types()
        print(f"✅ Supports {len(supported_types)} secret types")
        
        return True
    except Exception as e:
        print(f"❌ Regex test failed: {e}")
        return False

def test_rate_limiter():
    """Test rate limiter functionality"""
    print("\n⏱️ Testing rate limiter...")
    
    try:
        import time
        
        limiter = RateLimiter(rate=5.0, max_tokens=10)
        
        # Test token acquisition
        async def test_acquire():
            start = time.time()
            await limiter.acquire(1)
            await limiter.acquire(1)
            await limiter.acquire(1)
            end = time.time()
            return end - start
            
        duration = asyncio.run(test_acquire())
        print(f"✅ Rate limiter working (duration: {duration:.2f}s)")
        
        # Test status
        status = limiter.get_status()
        print(f"✅ Status: {status['available_tokens']:.1f}/{status['max_tokens']} tokens")
        
        return True
    except Exception as e:
        print(f"❌ Rate limiter test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        import json
        
        # Test config file exists and is valid JSON
        config_file = Path("config.json")
        if not config_file.exists():
            print("❌ config.json not found")
            return False
            
        with open(config_file) as f:
            config = json.load(f)
            
        required_sections = ['scanner', 'modules', 'telegram', 'output', 'validation']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing config section: {section}")
                return False
                
        print("✅ Configuration file valid")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_scanner_initialization():
    """Test scanner initialization"""
    print("\n🚀 Testing scanner initialization...")
    
    try:
        import json
        
        with open("config.json") as f:
            config = json.load(f)
            
        from modules.scanner_base import SpaceCracker
        scanner = SpaceCracker(config)
        
        print(f"✅ Scanner initialized with {len(scanner.modules)} modules")
        print(f"✅ Rate limiter: {scanner.rate_limiter.rate} req/s")
        print(f"✅ Vulnerable paths: {len(scanner.vulnerable_paths)}")
        
        return True
    except Exception as e:
        print(f"❌ Scanner initialization failed: {e}")
        return False

def test_cve_exploits():
    """Test CVE exploits functionality"""
    print("\n🛡️ Testing CVE exploits...")
    
    try:
        import json
        
        with open("config.json") as f:
            config = json.load(f)
            
        from modules.cve_exploits import CVEExploits
        cve_module = CVEExploits(config)
        
        exploits = cve_module.list_available_exploits()
        print(f"✅ {len(exploits)} CVE exploits available")
        
        for cve_id, name in list(exploits.items())[:3]:
            print(f"   • {cve_id}: {name}")
            
        return True
    except Exception as e:
        print(f"❌ CVE exploits test failed: {e}")
        return False

def test_files_structure():
    """Test file structure"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "scanner.py",
        "config.json",
        "requirements.txt",
        "README.md",
        "modules/scanner_base.py",
        "utils/regex_patterns.py",
        "data/paths.txt",
        "examples/targets.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🧪 SpaceCracker Test Suite")
    print("=" * 50)
    
    tests = [
        test_files_structure,
        test_imports,
        test_config_loading,
        test_regex_patterns,
        test_rate_limiter,
        test_scanner_initialization,
        test_cve_exploits
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SpaceCracker is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())