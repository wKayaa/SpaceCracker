import os
import json
import csv
import datetime
from .config import Config
from typing import Dict, Any, List

class ReportWriter:
    def __init__(self, config: Config):
        self.config = config
        os.makedirs(config.outputs.directory, exist_ok=True)
    
    def write_reports(self, results: Dict[str, Any]):
        """Write reports in all configured formats"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if "json" in self.config.outputs.formats:
            self._write_json_report(results, timestamp)
            
        if "txt" in self.config.outputs.formats:
            self._write_txt_report(results, timestamp)
            
        if "csv" in self.config.outputs.formats:
            self._write_csv_report(results, timestamp)
    
    def _write_json_report(self, results: Dict[str, Any], timestamp: str):
        """Write JSON report"""
        filename = os.path.join(
            self.config.outputs.directory,
            f"spacecracker_results_{timestamp}.json"
        )
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"JSON report written to: {filename}")
    
    def _write_txt_report(self, results: Dict[str, Any], timestamp: str):
        """Write human-readable text report"""
        filename = os.path.join(
            self.config.outputs.directory,
            f"spacecracker_results_{timestamp}.txt"
        )
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("SPACECRACKER SCAN RESULTS\n")
            f.write("="*80 + "\n\n")
            
            # Metadata
            metadata = results.get("metadata", {})
            f.write(f"Started: {metadata.get('started_at', 'Unknown')}\n")
            f.write(f"Finished: {metadata.get('finished_at', 'Unknown')}\n")
            f.write(f"Targets: {metadata.get('targets', 0)}\n")
            f.write(f"Modules: {', '.join(metadata.get('modules', []))}\n\n")
            
            # Summary
            summary = results.get("summary", {})
            f.write("SUMMARY\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Findings: {summary.get('total_findings', 0)}\n")
            f.write(f"Errors: {summary.get('errors', 0)}\n\n")
            
            # Severity breakdown
            severity_counts = summary.get("by_severity", {})
            f.write("Severity Breakdown:\n")
            for severity in ["Critical", "High", "Medium", "Low"]:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    f.write(f"  {severity}: {count}\n")
            f.write("\n")
            
            # Detailed findings
            findings = results.get("findings", [])
            if findings:
                f.write("DETAILED FINDINGS\n")
                f.write("="*40 + "\n\n")
                
                # Group by severity
                for severity in ["Critical", "High", "Medium", "Low"]:
                    severity_findings = [
                        f for f in findings 
                        if f.get("severity") == severity
                    ]
                    
                    if severity_findings:
                        f.write(f"{severity.upper()} SEVERITY FINDINGS ({len(severity_findings)})\n")
                        f.write("-"*50 + "\n")
                        
                        for i, finding in enumerate(severity_findings, 1):
                            f.write(f"{i}. {finding.get('title', 'Unknown')}\n")
                            f.write(f"   Target: {finding.get('target', 'Unknown')}\n")
                            f.write(f"   Module: {finding.get('module_id', 'Unknown')}\n")
                            f.write(f"   Category: {finding.get('category', 'Unknown')}\n")
                            f.write(f"   Confidence: {finding.get('confidence', 0):.1%}\n")
                            f.write(f"   Description: {finding.get('description', 'No description')}\n")
                            f.write(f"   Recommendation: {finding.get('recommendation', 'No recommendation')}\n")
                            f.write("\n")
            
            # Errors
            errors = results.get("errors", [])
            if errors:
                f.write("ERRORS\n")
                f.write("="*40 + "\n")
                for error in errors:
                    f.write(f"- {error}\n")
        
        print(f"Text report written to: {filename}")
    
    def _write_csv_report(self, results: Dict[str, Any], timestamp: str):
        """Write CSV report"""
        filename = os.path.join(
            self.config.outputs.directory,
            f"spacecracker_results_{timestamp}.csv"
        )
        
        findings = results.get("findings", [])
        
        with open(filename, 'w', newline='') as f:
            if findings:
                fieldnames = [
                    'timestamp', 'module_id', 'target', 'severity', 'title',
                    'category', 'confidence', 'short_description'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for finding in findings:
                    writer.writerow({
                        'timestamp': results.get("metadata", {}).get("started_at", ""),
                        'module_id': finding.get('module_id', ''),
                        'target': finding.get('target', ''),
                        'severity': finding.get('severity', ''),
                        'title': finding.get('title', ''),
                        'category': finding.get('category', ''),
                        'confidence': finding.get('confidence', 0),
                        'short_description': finding.get('description', '')[:100]
                    })
        
        print(f"CSV report written to: {filename}")