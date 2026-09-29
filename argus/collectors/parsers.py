"""ARGUS Parsers & Collectors (SIH26163)
Normalizes outputs from Semgrep SARIF, npm audit, secret scanner, and manual code audits.
"""

import json
import os
from typing import List, Dict, Any, Optional
from ..engine.schema import Finding

def parse_sarif(sarif_path: str, tool_name: str = "semgrep") -> List[Finding]:
    findings = []
    if not os.path.exists(sarif_path):
        return findings
    
    try:
        with open(sarif_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for run in data.get("runs", []):
            rules = {r.get("id"): r for r in run.get("tool", {}).get("driver", {}).get("rules", [])}
            
            for result in run.get("results", []):
                rule_id = result.get("ruleId", "unknown-rule")
                rule = rules.get(rule_id, {})
                message = result.get("message", {}).get("text", "")
                
                # Extract file and line
                loc = result.get("locations", [{}])[0].get("physicalLocation", {})
                file_uri = loc.get("artifactLocation", {}).get("uri", "")
                line_no = loc.get("region", {}).get("startLine", 1)
                
                # Severity
                level = result.get("level", "warning")
                severity_map = {
                    "error": "High",
                    "warning": "Medium",
                    "note": "Low",
                    "none": "Info"
                }
                raw_severity = severity_map.get(level, "Medium")
                
                # CWE mapping from rule tags or properties
                cwe = None
                tags = rule.get("properties", {}).get("tags", [])
                for t in tags:
                    if "CWE-" in t.upper():
                        cwe = t.upper().strip()
                        break
                        
                finding = Finding(
                    id=f"{tool_name}-{rule_id}-{len(findings)+1}",
                    title=rule.get("shortDescription", {}).get("text", rule_id),
                    tool=tool_name,
                    rule_id=rule_id,
                    file=file_uri,
                    line=line_no,
                    cwe=cwe,
                    raw_severity=raw_severity,
                    description=message or rule.get("help", {}).get("text", "No description"),
                    evidence=[f"Location: {file_uri}:{line_no}"]
                )
                findings.append(finding)
    except Exception as e:
        print(f"Error parsing SARIF from {sarif_path}: {e}")
        
    return findings

def parse_npm_audit(audit_path: str) -> List[Finding]:
    findings = []
    if not os.path.exists(audit_path):
        return findings
        
    try:
        with open(audit_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        vulns = data.get("vulnerabilities", {})
        for pkg, info in vulns.items():
            severity = info.get("severity", "moderate").capitalize()
            via = info.get("via", [])
            for item in via:
                if isinstance(item, dict):
                    title = item.get("title", f"Vulnerable dependency {pkg}")
                    url = item.get("url", "")
                    cwe_list = item.get("cwe", [])
                    cwe = cwe_list[0] if cwe_list else "CWE-1104"
                    
                    finding = Finding(
                        id=f"npm-audit-{pkg}-{len(findings)+1}",
                        title=f"{pkg}: {title}",
                        tool="npm-audit",
                        rule_id=f"npm-{item.get('source', pkg)}",
                        file="package.json",
                        url=url,
                        cwe=cwe,
                        raw_severity=severity if severity in ["Critical", "High", "Medium", "Low"] else "Medium",
                        description=f"Package {pkg} (range: {item.get('range', 'unknown')}) has vulnerability: {title}. See advisory: {url}",
                        evidence=[f"Dependency: {pkg}", f"Advisory: {url}"]
                    )
                    findings.append(finding)
    except Exception as e:
        print(f"Error parsing npm audit from {audit_path}: {e}")
        
    return findings
