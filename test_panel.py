#!/usr/bin/env python3
"""
SpaceCracker Enhanced Panel Tests
Test the new panel functionality and CLI integration
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

class PanelTester:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_panel_access(self):
        """Test basic panel access"""
        print("🔍 Testing panel access...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Panel is accessible")
                return True
            else:
                print(f"❌ Panel access failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Panel access error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("🔗 Testing API endpoints...")
        
        endpoints = [
            ("/api/stats", "GET"),
            ("/api/modules", "GET"),
        ]
        
        results = []
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - {response.status_code}")
                    results.append(True)
                else:
                    print(f"❌ {endpoint} - {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
                results.append(False)
        
        return all(results)
    
    def test_modules_loading(self):
        """Test module loading functionality"""
        print("🧩 Testing modules loading...")
        try:
            response = self.session.get(f"{self.base_url}/api/modules")
            if response.status_code == 200:
                data = response.json()
                modules = data.get('modules', [])
                print(f"✅ Loaded {len(modules)} modules")
                
                # Print some module info
                for i, module in enumerate(modules[:3]):
                    print(f"   • {module['name']} ({module['category']}) - {module['severity']}")
                
                return len(modules) > 0
            else:
                print(f"❌ Modules loading failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Modules loading error: {e}")
            return False
    
    def test_cli_integration(self):
        """Test CLI integration"""
        print("🖥️ Testing CLI integration...")
        try:
            test_data = {
                "targets": ["https://httpbin.org/get"],
                "options": {
                    "threads": 10,
                    "timeout": 15,
                    "modules": ["GGB Scanner"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cli/scan",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ CLI scan started - ID: {data.get('scan_id')}")
                    return True
                else:
                    print(f"❌ CLI scan failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ CLI integration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ CLI integration error: {e}")
            return False
    
    def test_scan_pages(self):
        """Test scan page accessibility"""
        print("📄 Testing scan pages...")
        
        pages = [
            "/scan",
            "/results", 
            "/config"
        ]
        
        results = []
        for page in pages:
            try:
                response = self.session.get(f"{self.base_url}{page}")
                if response.status_code == 200:
                    print(f"✅ {page} - Accessible")
                    results.append(True)
                else:
                    print(f"❌ {page} - {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {page} - Error: {e}")
                results.append(False)
        
        return all(results)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 SpaceCracker Enhanced Panel Tests")
        print("=" * 50)
        
        tests = [
            ("Panel Access", self.test_panel_access),
            ("API Endpoints", self.test_api_endpoints),
            ("Modules Loading", self.test_modules_loading),
            ("CLI Integration", self.test_cli_integration),
            ("Scan Pages", self.test_scan_pages)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔬 Running {test_name}...")
            results.append(test_func())
            time.sleep(0.5)  # Small delay between tests
        
        print(f"\n📊 Test Results: {sum(results)}/{len(results)} tests passed")
        
        if all(results):
            print("🎉 All tests passed! Panel is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Check the output above.")
            return False

def main():
    """Main test runner"""
    tester = PanelTester()
    
    # Check if panel is running
    if not tester.test_panel_access():
        print("❌ Panel is not accessible. Make sure it's running on http://127.0.0.1:8080")
        return False
    
    # Run all tests
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)