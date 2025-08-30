import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spacecracker.core.config import load_config, Config

def test_load_default_config():
    """Test loading default configuration"""
    c = load_config("nonexistent.json")
    assert isinstance(c, Config)
    assert c.threads == 50
    assert c.rate_limit.requests_per_second == 10

def test_load_config_from_file():
    """Test loading configuration from file"""
    # Test with example config
    c = load_config("configs/config.example.json")
    assert isinstance(c, Config)
    # Should load defaults if file doesn't exist
    
if __name__ == "__main__":
    test_load_default_config()
    test_load_config_from_file()
    print("✅ Config tests passed")