import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spacecracker.core.registry import ModuleRegistry

def test_registry_discovers():
    """Test that registry discovers modules"""
    r = ModuleRegistry()
    module_ids = r.list_module_ids()
    
    # Should find our implemented modules
    expected_modules = ["js_scanner", "git_scanner", "ggb_scanner"]
    
    for expected in expected_modules:
        assert expected in module_ids, f"Module {expected} not discovered"
    
    print(f"✅ Found modules: {module_ids}")

def test_module_creation():
    """Test module creation"""
    r = ModuleRegistry()
    
    # Try to create a module
    module = r.create_module("js_scanner")
    assert module is not None
    assert hasattr(module, 'run')
    
if __name__ == "__main__":
    test_registry_discovers()
    test_module_creation()
    print("✅ Registry tests passed")