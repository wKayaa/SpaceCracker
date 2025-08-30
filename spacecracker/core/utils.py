import datetime
from typing import List, Dict, Any

def severity_order(s: str):
    """Get numeric severity order"""
    ranks = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    return ranks.get(s, 1)

def format_timestamp(ts=None):
    """Format timestamp for output"""
    if ts is None:
        ts = datetime.datetime.now()
    return ts.strftime("%Y-%m-%d %H:%M:%S")

def deduplicate_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate findings based on id"""
    seen = set()
    deduped = []
    
    for finding in findings:
        finding_id = finding.get('id', '')
        if finding_id not in seen:
            seen.add(finding_id)
            deduped.append(finding)
    
    return deduped