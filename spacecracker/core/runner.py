import threading
import queue
import time
from typing import List, Dict, Any
from .rate_limiter import RateLimiter
from .config import Config
from .registry import ModuleRegistry

class ScanRunner:
    """Orchestrates the scanning process with multiple modules"""
    
    def __init__(self, config: Config):
        self.config = config
        self.rate_limiter = RateLimiter(
            config.rate_limit.requests_per_second,
            config.rate_limit.burst
        )
        self.registry = ModuleRegistry()
        
    def run_scan(self, targets: List[str]) -> Dict[str, Any]:
        """Run scan against multiple targets"""
        results = {
            "metadata": {
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "targets": len(targets),
                "modules": self.config.modules,
                "version": "0.1.0"
            },
            "findings": [],
            "errors": []
        }
        
        # Create thread pool for concurrent scanning
        work_queue = queue.Queue()
        result_queue = queue.Queue()
        
        # Add work items to queue
        for target in targets:
            for module_id in self.config.modules:
                work_queue.put((target, module_id))
        
        # Start worker threads
        threads = []
        for i in range(self.config.threads):
            thread = threading.Thread(
                target=self._worker_thread,
                args=(work_queue, result_queue)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all work to complete
        work_queue.join()
        
        # Collect results
        while not result_queue.empty():
            try:
                result = result_queue.get_nowait()
                if result.get("findings"):
                    results["findings"].extend(result["findings"])
                if result.get("errors"):
                    results["errors"].extend(result["errors"])
            except queue.Empty:
                break
        
        # Update metadata
        results["metadata"]["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        results["summary"] = self._calculate_summary(results)
        
        return results
    
    def _worker_thread(self, work_queue: queue.Queue, result_queue: queue.Queue):
        """Worker thread that processes scan jobs"""
        while True:
            try:
                target, module_id = work_queue.get(timeout=1)
                
                # Rate limiting
                self.rate_limiter.acquire()
                
                # Create module instance
                module = self.registry.create_module(module_id, self.config)
                
                if module:
                    try:
                        # Run module (Note: converting async to sync for now)
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        result = loop.run_until_complete(
                            module.run(target, self.config, {})
                        )
                        result_queue.put(result)
                        
                        loop.close()
                        
                    except Exception as e:
                        error_result = {
                            "module_id": module_id,
                            "target": target,
                            "findings": [],
                            "errors": [f"Module execution failed: {str(e)}"]
                        }
                        result_queue.put(error_result)
                else:
                    error_result = {
                        "module_id": module_id,
                        "target": target,
                        "findings": [],
                        "errors": [f"Module {module_id} not found"]
                    }
                    result_queue.put(error_result)
                
                work_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                print(f"Worker thread error: {e}")
                work_queue.task_done()
    
    def _calculate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        findings = results.get("findings", [])
        
        severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for finding in findings:
            severity = finding.get("severity", "Low")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            "total_findings": len(findings),
            "by_severity": severity_counts,
            "errors": len(results.get("errors", []))
        }