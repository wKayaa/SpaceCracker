import time
import random
import string
from datetime import datetime

class CrackManager:
    """Manages unique crack IDs for findings"""
    
    def __init__(self):
        self.current_id = None
        
    def generate_crack_id(self) -> str:
        """Generate unique crack ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H")
        random_suffix = ''.join(random.choices(string.digits, k=3))
        crack_id = f"{timestamp}{random_suffix}"
        self.current_id = crack_id
        return crack_id
    
    def get_current_id(self) -> str:
        """Get current crack ID"""
        return self.current_id or self.generate_crack_id()