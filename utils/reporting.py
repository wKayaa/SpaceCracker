#!/usr/bin/env python3
"""
Reporting Module
Generates comprehensive reports in JSON and TXT formats
"""

import json
import os
from datetime import datetime
import logging
from pathlib import Path

class Reporter:
    """Generates comprehensive scan reports"""
    
    def __init__(self, output_dir="results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def generate_reports(self, results):
        """Generate all report formats"""
        if not results:
            self.logger.info("No results to report")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate JSON report
        json_file = self.output_dir / f"spacecracker_results_{timestamp}.json"
        self._generate_json_report(results, json_file)
        
        # Generate TXT report
        txt_file = self.output_dir / f"spacecracker_results_{timestamp}.txt"
        self._generate_txt_report(results, txt_file)
        
        # Generate summary report
        summary_file = self.output_dir / f"spacecracker_summary_{timestamp}.txt"
        self._generate_summary_report(results, summary_file)
        
        # Generate CSV report for validated secrets
        csv_file = self.output_dir / f"spacecracker_secrets_{timestamp}.csv"
        self._generate_csv_report(results, csv_file)
        
        self.logger.info(f"Reports generated in {self.output_dir}")
        
    def _generate_json_report(self, results, filename):
        """Generate detailed JSON report"""
        try:
            report_data = {
                'metadata': {
                    'scan_timestamp': datetime.now().isoformat(),
                    'total_results': len(results),
                    'generator': 'SpaceCracker',
                    'version': '1.0.0'
                },
                'statistics': self._calculate_statistics(results),
                'results': results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
                
            self.logger.info(f"JSON report saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            
    def _generate_txt_report(self, results, filename):
        """Generate human-readable text report"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("="*80 + "\n")
                f.write("SPACECRACKER SCAN RESULTS\n")
                f.write("="*80 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Results: {len(results)}\n\n")
                
                # Statistics
                stats = self._calculate_statistics(results)
                f.write("STATISTICS\n")
                f.write("-"*40 + "\n")
                
                f.write(f"Severity Breakdown:\n")
                for severity, count in stats['severity_breakdown'].items():
                    f.write(f"  {severity.title()}: {count}\n")
                    
                f.write(f"\nModule Breakdown:\n")
                for module, count in stats['module_breakdown'].items():
                    module_name = module.replace('_', ' ').title()
                    f.write(f"  {module_name}: {count}\n")
                    
                f.write(f"\nValidated Secrets: {stats['validated_secrets']}\n")
                f.write(f"CVE Vulnerabilities: {stats['cve_vulnerabilities']}\n")
                f.write(f"Exposed Files: {stats['exposed_files']}\n\n")
                
                # Detailed results
                f.write("DETAILED RESULTS\n")
                f.write("="*80 + "\n\n")
                
                # Group by severity
                for severity in ['critical', 'high', 'medium', 'low']:
                    severity_results = [r for r in results if r.get('severity') == severity]
                    if not severity_results:
                        continue
                        
                    f.write(f"{severity.upper()} SEVERITY FINDINGS ({len(severity_results)})\n")
                    f.write("-"*50 + "\n")
                    
                    for i, result in enumerate(severity_results, 1):
                        f.write(f"\n[{i}] {result.get('type', 'Unknown').replace('_', ' ').title()}\n")
                        f.write(f"    URL: {result.get('url', 'N/A')}\n")
                        f.write(f"    Module: {result.get('module', 'Unknown').replace('_', ' ').title()}\n")
                        f.write(f"    Status: {result.get('status', 'N/A')}\n")
                        
                        # Add specific details
                        if result.get('cve_id'):
                            f.write(f"    CVE: {result['cve_id']}\n")
                            
                        if result.get('secrets'):
                            f.write(f"    Secrets Found: {len(result['secrets'])}\n")
                            
                        if result.get('validated_secrets'):
                            f.write(f"    Validated Secrets: {len(result['validated_secrets'])}\n")
                            for secret in result['validated_secrets'][:3]:  # Show first 3
                                service = secret['validation'].get('service', 'Unknown')
                                f.write(f"      - {service}\n")
                                
                        if result.get('files'):
                            f.write(f"    Files Exposed: {len(result['files'])}\n")
                            
                        if result.get('findings'):
                            total_findings = sum(len(findings) for findings in result['findings'].values())
                            f.write(f"    JS Findings: {total_findings}\n")
                            
                    f.write("\n" + "="*80 + "\n")
                    
            self.logger.info(f"TXT report saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error generating TXT report: {e}")
            
    def _generate_summary_report(self, results, filename):
        """Generate executive summary report"""
        try:
            stats = self._calculate_statistics(results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("SPACECRACKER EXECUTIVE SUMMARY\n")
                f.write("="*50 + "\n")
                f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # High-level statistics
                f.write("KEY METRICS:\n")
                f.write(f"• Total Findings: {len(results)}\n")
                f.write(f"• Critical Vulnerabilities: {stats['severity_breakdown'].get('critical', 0)}\n")
                f.write(f"• High-Risk Findings: {stats['severity_breakdown'].get('high', 0)}\n")
                f.write(f"• Validated Secrets: {stats['validated_secrets']}\n")
                f.write(f"• CVE Vulnerabilities: {stats['cve_vulnerabilities']}\n\n")
                
                # Risk assessment
                risk_level = self._assess_risk_level(stats)
                f.write(f"OVERALL RISK LEVEL: {risk_level}\n\n")
                
                # Top findings
                high_risk_results = [r for r in results if r.get('severity') in ['critical', 'high']]
                if high_risk_results:
                    f.write("TOP PRIORITY FINDINGS:\n")
                    for i, result in enumerate(high_risk_results[:5], 1):
                        result_type = result.get('type', 'Unknown').replace('_', ' ').title()
                        url = result.get('url', 'N/A')
                        f.write(f"{i}. {result_type} - {url}\n")
                        
                f.write(f"\nRecommendations:\n")
                recommendations = self._generate_recommendations(stats, results)
                for rec in recommendations:
                    f.write(f"• {rec}\n")
                    
            self.logger.info(f"Summary report saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")
            
    def _generate_csv_report(self, results, filename):
        """Generate CSV report for validated secrets"""
        try:
            import csv
            
            validated_secrets = []
            for result in results:
                if result.get('validated_secrets'):
                    for secret in result['validated_secrets']:
                        validated_secrets.append({
                            'URL': result.get('url', ''),
                            'Target': result.get('base_target', ''),
                            'Module': result.get('module', ''),
                            'Service': secret['validation'].get('service', ''),
                            'Secret Type': secret['secret'].get('type', ''),
                            'Valid': secret['validation'].get('valid', False),
                            'Additional Info': str(secret['validation'].get('note', ''))
                        })
                        
            if validated_secrets:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['URL', 'Target', 'Module', 'Service', 'Secret Type', 'Valid', 'Additional Info']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for secret in validated_secrets:
                        writer.writerow(secret)
                        
                self.logger.info(f"CSV report saved: {filename}")
            else:
                self.logger.info("No validated secrets to export to CSV")
                
        except Exception as e:
            self.logger.error(f"Error generating CSV report: {e}")
            
    def _calculate_statistics(self, results):
        """Calculate scan statistics"""
        stats = {
            'total_results': len(results),
            'severity_breakdown': {},
            'module_breakdown': {},
            'validated_secrets': 0,
            'cve_vulnerabilities': 0,
            'exposed_files': 0,
            'unique_targets': set()
        }
        
        for result in results:
            # Severity breakdown
            severity = result.get('severity', 'unknown')
            stats['severity_breakdown'][severity] = stats['severity_breakdown'].get(severity, 0) + 1
            
            # Module breakdown
            module = result.get('module', 'unknown')
            stats['module_breakdown'][module] = stats['module_breakdown'].get(module, 0) + 1
            
            # Validated secrets
            if result.get('validated_secrets'):
                stats['validated_secrets'] += len(result['validated_secrets'])
                
            # CVE vulnerabilities
            if result.get('cve_id'):
                stats['cve_vulnerabilities'] += 1
                
            # Exposed files
            if result.get('files'):
                stats['exposed_files'] += len(result['files'])
                
            # Unique targets
            if result.get('base_target'):
                stats['unique_targets'].add(result['base_target'])
                
        stats['unique_targets'] = len(stats['unique_targets'])
        return stats
        
    def _assess_risk_level(self, stats):
        """Assess overall risk level"""
        critical_count = stats['severity_breakdown'].get('critical', 0)
        high_count = stats['severity_breakdown'].get('high', 0)
        validated_secrets = stats['validated_secrets']
        
        if critical_count > 0 or validated_secrets > 5:
            return "CRITICAL"
        elif high_count > 3 or validated_secrets > 2:
            return "HIGH"
        elif high_count > 0 or validated_secrets > 0:
            return "MEDIUM"
        else:
            return "LOW"
            
    def _generate_recommendations(self, stats, results):
        """Generate security recommendations"""
        recommendations = []
        
        if stats['severity_breakdown'].get('critical', 0) > 0:
            recommendations.append("Immediately address all critical vulnerabilities")
            
        if stats['validated_secrets'] > 0:
            recommendations.append("Rotate all exposed and validated credentials immediately")
            
        if stats['cve_vulnerabilities'] > 0:
            recommendations.append("Apply security patches for identified CVE vulnerabilities")
            
        if stats['exposed_files'] > 0:
            recommendations.append("Secure exposed file directories and review access controls")
            
        # Check for specific vulnerability types
        git_exposures = [r for r in results if r.get('module') == 'git_scanner']
        if git_exposures:
            recommendations.append("Remove exposed version control directories (.git, .svn)")
            
        js_exposures = [r for r in results if r.get('module') == 'js_scanner' and r.get('findings')]
        if js_exposures:
            recommendations.append("Review JavaScript files for hardcoded secrets and sensitive information")
            
        if not recommendations:
            recommendations.append("Continue regular security monitoring and assessments")
            
        return recommendations