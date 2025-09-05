import asyncio
from typing import List, Dict, Any, Optional
from .scanner import Scanner
from .stats_manager import StatsManager
from .url_processor import URLProcessor

class Orchestrator:
    """Central orchestration system for SpaceCracker V2"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stats_manager = StatsManager()
        self.scanner = Scanner(self.stats_manager)
        self.url_processor = URLProcessor()
        self.running = False
        
        # Configure from settings
        if config:
            self.stats_manager.stats.update({
                'threads': config.get('threads', 5000),
                'timeout': config.get('timeout', 20),
                'max_urls': config.get('max_urls', 250000)
            })
    
    async def initialize(self):
        """Initialize all components"""
        await self.scanner.initialize()
        self.running = True
    
    async def cleanup(self):
        """Cleanup all resources"""
        self.running = False
        await self.scanner.cleanup()
    
    async def run_scan(self, targets: List[str], paths: List[str]) -> List[Dict[str, Any]]:
        """Run comprehensive scan"""
        if not self.running:
            await self.initialize()
        
        try:
            # Process and validate URLs
            processed_urls = self.url_processor.filter_valid_urls(targets)
            processed_urls = self.url_processor.deduplicate_urls(processed_urls)
            
            # Update stats with total URLs
            self.stats_manager.update_stats(max_urls=len(processed_urls))
            self.stats_manager.update_stats(status='scanning')
            
            # Start scanning
            results = await self.scanner.scan_multiple_urls(processed_urls, paths)
            
            # Update final status
            self.stats_manager.update_stats(status='completed')
            
            return results
            
        except Exception as e:
            self.stats_manager.update_stats(status='error')
            raise e
    
    def get_stats(self) -> str:
        """Get formatted statistics"""
        return self.stats_manager.get_formatted_output()
    
    async def run_exploitation(self, targets: List[str], exploit_type: str = 'all') -> Dict[str, Any]:
        """Run exploitation modules"""
        exploitation_results = {
            'docker_infections': 0,
            'k8s_infections': 0,
            'total_infected': 0
        }
        
        if exploit_type in ['docker', 'all']:
            # Docker exploitation would be implemented here
            pass
        
        if exploit_type in ['k8s', 'kubernetes', 'all']:
            # Kubernetes exploitation would be implemented here
            pass
        
        return exploitation_results
    
    def load_paths_from_file(self, file_path: str) -> List[str]:
        """Load scan paths from file"""
        paths = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        paths.append(line)
        except Exception as e:
            print(f"Error loading paths from {file_path}: {e}")
        
        return paths