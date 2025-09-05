import threading
import queue
import time
from typing import List, Dict, Any, Optional
from .rate_limiter import RateLimiter
from .config import Config
from .registry import ModuleRegistry
from .stats_manager import StatsManager

class ScanRunner:
    """Orchestrates the scanning process with multiple modules"""
    
    def __init__(self, config: Config):
        self.config = config
        self.rate_limiter = RateLimiter(
            config.rate_limit.requests_per_second,
            config.rate_limit.burst
        )
        self.registry = ModuleRegistry()
        self.stats_manager: Optional[StatsManager] = None
        
    def run_scan(self, targets: List[str], show_stats: bool = True) -> Dict[str, Any]:
        """Run scan against multiple targets"""
        # Initialize stats manager
        if show_stats:
            self.stats_manager = StatsManager(total_targets=len(targets))
            self.stats_manager.update_stats(
                total_urls=len(targets),
                threads=self.config.threads,
                timeout=30,  # Default timeout
                status="running"
            )
            self.stats_manager.start_display()
        
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
        
        # Stop stats display
        if self.stats_manager:
            self.stats_manager.update_stats(status="completed")
            self.stats_manager.stop_display()
            
            # Print final hits if any
            for finding in results["findings"]:
                if finding.get('validation', {}).get('valid'):
                    hit_report = self.stats_manager.format_hit_report(finding)
                    print(f"\n{hit_report}\n")
        
        return results
    
    def _worker_thread(self, work_queue: queue.Queue, result_queue: queue.Queue):
        """Worker thread that processes scan jobs"""
        while True:
            try:
                target, module_id = work_queue.get(timeout=1)
                
                # Rate limiting
                self.rate_limiter.acquire()
                
                # Update stats
                if self.stats_manager:
                    self.stats_manager.update_stats(
                        current_target=target,
                        checked_urls=1
                    )
                
                # Create module instance
                module = self.registry.create_module(module_id, self.config)
                
                if module:
                    try:
                        # Run module (Note: converting async to sync for now)
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        start_time = time.time()
                        result = loop.run_until_complete(
                            module.run(target, self.config, {})
                        )
                        response_time = time.time() - start_time
                        
                        # Update response time in findings
                        for finding in result.get('findings', []):
                            finding['response_time'] = response_time
                        
                        result_queue.put(result)
                        
                        # Update stats with findings
                        if self.stats_manager and result.get('findings'):
                            valid_findings = [f for f in result['findings'] if f.get('validation', {}).get('valid')]
                            if valid_findings:
                                self.stats_manager.update_stats(hits=len(valid_findings))
                                
                                # Update findings by service
                                findings_by_service = {}
                                for finding in valid_findings:
                                    service = finding.get('service', 'unknown')
                                    findings_by_service[service] = findings_by_service.get(service, 0) + 1
                                self.stats_manager.update_stats(findings_by_service=findings_by_service)
                        
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