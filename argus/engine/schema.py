"""ARGUS Security Finding Schema (SIH26163)
Standardized schema across SAST, DAST, SCA, Secret scanning, and Manual Verification.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Finding(BaseModel):
    id: str
    title: str
    tool: str  # semgrep | zap | nuclei | gitleaks | osv | npm-audit | manual | code-audit
    rule_id: str
    file: Optional[str] = None
    url: Optional[str] = None
    line: Optional[int] = None
    cwe: Optional[str] = None  # e.g. "CWE-79"
    owasp: Optional[str] = None  # e.g. "A03:2021"
    raw_severity: str  # Critical | High | Medium | Low | Info
    description: str
    evidence: List[str] = Field(default_factory=list)
    cvss_vector: Optional[str] = None
    cvss_score: Optional[float] = None
    cvss_severity: Optional[str] = None
    affected_component: Optional[str] = None
    remediation: Optional[str] = None
    confidence: Optional[str] = "medium"  # high | medium | low
    poc_steps: Optional[List[str]] = Field(default_factory=list)
    status: Optional[str] = "confirmed"  # confirmed | triage | false-positive

class CorrelatedFinding(BaseModel):
    id: str
    key: str
    title: str
    cwe: Optional[str] = None
    owasp: Optional[str] = None
    severity: str
    cvss_score: float
    cvss_vector: str
    affected_component: str
    description: str
    remediation: str
    confidence: str
    tools: List[str]
    evidence_count: int
    findings: List[Finding]
    poc_file: Optional[str] = None
    evidence_paths: List[str] = Field(default_factory=list)
