import inspect
import pkgutil
import importlib
from typing import List, Dict, Any
from ..modules import base as base_mod

class ModuleRegistry:
    """Registry for auto-discovering and managing modules"""
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self._discover_modules()
    
    def _discover_modules(self):
        """Auto-discover modules in the modules directory"""
        try:
            import spacecracker.modules as modules_package
            
            for finder, name, ispkg in pkgutil.iter_modules(modules_package.__path__, modules_package.__name__ + "."):
                if name.endswith('.base'):
                    continue
                    
                try:
                    module = importlib.import_module(name)
                    
                    # Find classes that inherit from BaseModule
                    for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
                        if (class_obj != base_mod.BaseModule and 
                            issubclass(class_obj, base_mod.BaseModule) and
                            hasattr(class_obj, 'module_id')):
                            
                            self.modules[class_obj.module_id] = class_obj
                            
                except Exception as e:
                    print(f"Warning: Failed to load module {name}: {e}")
                    
        except Exception as e:
            print(f"Warning: Failed to discover modules: {e}")
    
    def get_module(self, module_id: str) -> Any:
        """Get a module class by its ID"""
        return self.modules.get(module_id)
    
    def list_module_ids(self) -> List[str]:
        """Get list of all available module IDs"""
        return list(self.modules.keys())
    
    def list_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed info about all modules"""
        result = {}
        for module_id, module_class in self.modules.items():
            result[module_id] = {
                "name": getattr(module_class, 'name', module_id),
                "description": getattr(module_class, 'description', ''),
                "supports_batch": getattr(module_class, 'supports_batch', False)
            }
        return result
    
    def create_module(self, module_id: str, config: Any = None) -> Any:
        """Create an instance of a module"""
        module_class = self.get_module(module_id)
        if module_class:
            return module_class(config)
        return None