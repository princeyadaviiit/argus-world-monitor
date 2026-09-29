"""ARGUS Correlation Engine (SIH26163)
Deduplicates findings, correlates multi-tool signals, computes CVSS v3.1 vectors, and maps OWASP/CWE.
"""

import json
import os
from typing import List, Dict, Any
from cvss import CVSS3
from .schema import Finding, CorrelatedFinding

def load_cwe_mapping(path: str = "argus/engine/cwe_to_owasp.json") -> Dict[str, str]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def calculate_cvss(vector: str) -> tuple[float, str]:
    try:
        c = CVSS3(vector)
        scores = c.scores()
        severities = c.severities()
        return float(scores[0]), str(severities[0])
    except Exception as e:
        print(f"Error calculating CVSS for {vector}: {e}")
        return 0.0, "Unknown"

def correlate_findings(findings: List[Finding]) -> List[CorrelatedFinding]:
    cwe_map = load_cwe_mapping()
    
    # Group findings by weakness key: (cwe/rule_id, file or affected component)
    groups: Dict[str, List[Finding]] = {}
    for f in findings:
        # Normalize CWE
        cwe_clean = f.cwe.split(":")[0].strip() if f.cwe else None
        if cwe_clean and not f.owasp:
            f.owasp = cwe_map.get(cwe_clean)
            
        group_key = f"{f.cwe or f.rule_id}::{f.file or f.url or f.affected_component}"
        groups.setdefault(group_key, []).append(f)
        
    correlated = []
    for idx, (k, items) in enumerate(groups.items(), 1):
        primary = items[0]
        tools = sorted(list({i.tool for i in items}))
        confidence = "high" if len(tools) >= 2 else ("medium" if primary.confidence == "medium" else "low")
        
        # Calculate or assign CVSS
        vector = primary.cvss_vector or "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N"
        score, severity = calculate_cvss(vector)
        
        all_evidence = []
        for it in items:
            all_evidence.extend(it.evidence)
            
        cf = CorrelatedFinding(
            id=f"ARGUS-CONFIRMED-{idx:03d}",
            key=k,
            title=primary.title,
            cwe=primary.cwe,
            owasp=primary.owasp,
            severity=severity,
            cvss_score=score,
            cvss_vector=vector,
            affected_component=primary.affected_component or primary.file or "WorldMonitor Core",
            description=primary.description,
            remediation=primary.remediation or "Apply input sanitization, strict boundary checks, and defensive controls.",
            confidence=confidence,
            tools=tools,
            evidence_count=len(all_evidence),
            findings=items,
            evidence_paths=all_evidence[:10]
        )
        correlated.append(cf)
        
    correlated.sort(key=lambda x: x.cvss_score, reverse=True)
    return correlated
