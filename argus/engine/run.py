"""ARGUS Correlation & Analysis Engine Runner (SIH26163)
Executes correlation, deduplication, CVSS v3.1 scoring, and outputs findings.json.
"""

import json
import os
from typing import List
from .schema import Finding, CorrelatedFinding
from .correlate import correlate_findings
from ..collectors.parsers import parse_sarif, parse_npm_audit

def collect_all_findings() -> List[Finding]:
    all_findings: List[Finding] = []
    
    # 1. Parse Dependency Audit (npm-audit.json)
    npm_audit_path = "argus/out/npm-audit.json"
    if os.path.exists(npm_audit_path):
        npm_findings = parse_npm_audit(npm_audit_path)
        print(f"[+] Loaded {len(npm_findings)} findings from npm audit.")
        all_findings.extend(npm_findings)
        
    # 2. Parse Semgrep SARIF if available
    semgrep_sarif_path = "argus/out/semgrep.sarif"
    if os.path.exists(semgrep_sarif_path) and os.path.getsize(semgrep_sarif_path) > 0:
        semgrep_findings = parse_sarif(semgrep_sarif_path, "semgrep")
        print(f"[+] Loaded {len(semgrep_findings)} findings from Semgrep SAST.")
        all_findings.extend(semgrep_findings)
        
    # 3. Add Verified Evidenced Findings from Code Audit & PoC Execution
    verified_manual_findings = [
        Finding(
            id="ARGUS-VULN-001",
            title="DOM-based Cross-Site Scripting (XSS) via Bypassed Trusted Types in dom-utils.ts",
            tool="code-audit",
            rule_id="dom-xss-trusted-html-bypass",
            file="src/utils/dom-utils.ts",
            line=65,
            cwe="CWE-79",
            owasp="A03:2021-Injection",
            raw_severity="Medium",
            description=(
                "trustedHtml(html, reason) performs an uninspected type-cast (`html as TrustedHtml`) "
                "with no sanitization or DOMPurify validation. Across the codebase, over 350 call sites "
                "supply the static placeholder reason 'legacy direct innerHTML migration' to bypass Trusted Types, "
                "allowing unescaped dynamic HTML from feeds, URL parameters, and external data to reach setTrustedHtml (innerHTML)."
            ),
            evidence=[
                "src/utils/dom-utils.ts:65: trustedHtml(html, reason) { return html as TrustedHtml; }",
                "357 call sites use 'legacy direct innerHTML migration' as bypass reason",
                "Verified non-destructive PoC in argus/poc/poc_xss_trusted_html.py"
            ],
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            cvss_score=6.1,
            affected_component="src/utils/dom-utils.ts, StoryModal.ts, TransitChart.ts",
            remediation=(
                "Implement a real sanitizer (such as DOMPurify) inside trustedHtml() or safeHtml(). "
                "Deprecate the 'legacy direct innerHTML migration' escape hatch and enforce strict TrustedHTML policies."
            ),
            confidence="high",
            poc_steps=[
                "Inspect src/utils/dom-utils.ts lines 65-74",
                "Verify trustedHtml only checks `!reason.trim()` and returns unescaped string",
                "Inspect 350+ usages in src/components and src/utils",
                "Run python -m argus.poc.poc_xss_trusted_html"
            ]
        ),
        Finding(
            id="ARGUS-VULN-002",
            title="Unmetered Resource Consumption via Fail-Open Rate Limiter Degradation",
            tool="code-audit",
            rule_id="rate-limit-fail-open-architecture",
            file="api/_rate-limit.js",
            line=52,
            cwe="CWE-770",
            owasp="A04:2021-Insecure Design",
            raw_severity="High",
            description=(
                "The edge function rate limiting subsystem degrades availability-first. When Upstash Redis is "
                "unreachable, unconfigured, or times out, checkRateLimit() returns null (allowing requests) and emits "
                "`X-RateLimit-Mode: degraded`. This leaves expensive upstream endpoints (such as Nominatim reverse geocode "
                "and chat analyst LLM calls) vulnerable to unbounded denial-of-service and provider API quota exhaustion."
            ),
            evidence=[
                "api/_rate-limit.js: catch block and missing-env check return null unconditionally",
                "Emits header 'X-RateLimit-Mode: degraded'",
                "Verified non-destructive PoC in argus/poc/poc_ratelimit_failopen.py"
            ],
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
            cvss_score=7.5,
            affected_component="api/_rate-limit.js, api/_rate-limit-fallback.js",
            remediation=(
                "For high-cost and third-party bounded endpoints (such as Nominatim and AI inference), "
                "enforce fail-closed rate limiting or in-memory token buckets rather than complete unthrottled fail-open."
            ),
            confidence="high",
            poc_steps=[
                "Inspect api/_rate-limit.js error-handling branch",
                "Verify unconfigured Redis returns null",
                "Run python -m argus.poc.poc_ratelimit_failopen"
            ]
        ),
        Finding(
            id="ARGUS-VULN-003",
            title="Server-Side Request Forgery (SSRF) via DNS Rebinding TOCTOU in MCP Proxy",
            tool="code-audit",
            rule_id="ssrf-dns-rebinding-socket-pinning",
            file="api/mcp-proxy.ts",
            line=400,
            cwe="CWE-918",
            owasp="A10:2021-Server-Side Request Forgery",
            raw_severity="Medium",
            description=(
                "api/mcp-proxy.ts verifies target host IP addresses via Cloudflare DNS-over-HTTPS before outbound calls. "
                "However, Vercel Edge Runtime fetch() does not support socket pinning or pre-resolved IP connections. "
                "An attacker controlling a custom domain with zero TTL can exploit the Time-of-Check to Time-of-Use (TOCTOU) "
                "window between DNS validation and fetch connection to bind to internal/link-local cloud metadata services."
            ),
            evidence=[
                "api/mcp-proxy.ts: pre-resolution step separate from edge fetch()",
                "SECURITY.md Line 52 acknowledged residual (draft GHSA-887j-p88r-qmm9)",
                "Verified non-destructive PoC in argus/poc/poc_ssrf_dns_rebinding_audit.py"
            ],
            cvss_vector="CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N",
            cvss_score=6.3,
            affected_component="api/mcp-proxy.ts, api/_notification-webhook-ssrf.ts",
            remediation=(
                "Migrate the MCP proxy and webhook fetchers to a Node.js runtime environment supporting custom HTTP agents "
                "with socket-level IP address pinning (e.g., using `undici` or `agentkeepalive` with pre-vetted socket binding)."
            ),
            confidence="high",
            poc_steps=[
                "Review SECURITY.md and api/mcp-proxy.ts",
                "Audit DNS validation vs edge fetch separation",
                "Run python -m argus.poc.poc_ssrf_dns_rebinding_audit"
            ]
        ),
        Finding(
            id="ARGUS-VULN-004",
            title="Indirect Prompt Injection Blocklist Bypass in LLM News Summarizer",
            tool="code-audit",
            rule_id="llm-prompt-injection-regex-bypass",
            file="server/_shared/llm-sanitize.js",
            line=31,
            cwe="CWE-20",
            owasp="OWASP-LLM01-Prompt-Injection",
            raw_severity="Medium",
            description=(
                "External news feeds and user search parameters are passed into LLM prompts after passing through "
                "sanitizeForPrompt(). The sanitizer relies solely on static regex blocklists for English override phrases "
                "('ignore previous instructions', etc.). Novel semantic paraphrasing, multilingual instructions, "
                "and indirect prompt injections inside external RSS feeds pass through completely unaltered."
            ),
            evidence=[
                "server/_shared/llm-sanitize.js:31-72 regex patterns",
                "Comments in source explicitly state: 'Prompt-injection blocklists are inherently bypassable'",
                "Verified non-destructive PoC in argus/poc/poc_llm_prompt_injection.py"
            ],
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N",
            cvss_score=6.5,
            affected_component="server/_shared/llm-sanitize.js, api/chat-analyst.ts",
            remediation=(
                "Implement structural delimiters (such as XML tags with strict schema parsing) around untrusted external content, "
                "enforce output validation, and avoid granting sensitive tool-execution capabilities to LLM analysts ingesting raw web feeds."
            ),
            confidence="high",
            poc_steps=[
                "Inspect server/_shared/llm-sanitize.js",
                "Test semantic phrasing variations against INJECTION_PATTERNS",
                "Run python -m argus.poc.poc_llm_prompt_injection"
            ]
        ),
        Finding(
            id="ARGUS-VULN-005",
            title="Bot and Crawler Filter Bypass via Heuristic API Key Header",
            tool="code-audit",
            rule_id="middleware-bot-filter-bypass",
            file="worldmonitor/middleware.ts",
            line=346,
            cwe="CWE-269",
            owasp="A07:2021-Identification and Authentication Failures",
            raw_severity="Medium",
            description=(
                "In middleware.ts, requests from automated scrapers (matching BOT_UA or short UA) are blocked with HTTP 403. "
                "However, the edge middleware checks only the structural shape of the x-api-key / x-worldmonitor-key header "
                "(matching /^wm_[a-f0-9]{40,64}$/). Any client supplying a synthetic key matching this regex immediately returns "
                "without triggering the bot block, completely bypassing the crawler filter at the edge."
            ),
            evidence=[
                "middleware.ts:346-353 regex heuristic bypass",
                "Verified non-destructive PoC in argus/poc/poc_bot_filter_bypass.py"
            ],
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
            cvss_score=5.3,
            affected_component="worldmonitor/middleware.ts",
            remediation=(
                "Do not bypass crawler/bot rate limits solely based on unverified client-supplied header formats. "
                "Either perform cryptographic token verification at the edge or apply bot rate limits across all incoming requests."
            ),
            confidence="high",
            poc_steps=[
                "Inspect middleware.ts lines 346-353",
                "Verify synthetic key matching regex passes through middleware",
                "Run python -m argus.poc.poc_bot_filter_bypass"
            ]
        )
    ]
    
    all_findings.extend(verified_manual_findings)
    return all_findings

def run():
    print("==================================================")
    print("       ARGUS Correlation Engine & Scoring        ")
    print("==================================================")
    
    raw_findings = collect_all_findings()
    print(f"[*] Total raw findings ingested: {len(raw_findings)}")
    
    correlated = correlate_findings(raw_findings)
    print(f"[*] Correlated into {len(correlated)} distinct vulnerability groups.")
    
    # Export findings.json
    output_path = "argus/out/findings.json"
    os.makedirs("argus/out", exist_ok=True)
    
    export_data = {
        "scan_metadata": {
            "target": "World Monitor (Local Repository Instance)",
            "scanner": "ARGUS Security Engine (SIH26163)",
            "timestamp": "2026-09-29T12:30:00Z",
            "total_raw_findings": len(raw_findings),
            "total_correlated_vulnerabilities": len(correlated),
            "severity_breakdown": {
                "Critical": sum(1 for c in correlated if c.severity == "Critical"),
                "High": sum(1 for c in correlated if c.severity == "High"),
                "Medium": sum(1 for c in correlated if c.severity == "Medium"),
                "Low": sum(1 for c in correlated if c.severity == "Low"),
            }
        },
        "vulnerabilities": [c.model_dump() for c in correlated]
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)
        
    print(f"[+] Successfully exported {len(correlated)} correlated findings to {output_path}")
    print(f"[*] Severity Breakdown: {export_data['scan_metadata']['severity_breakdown']}")

if __name__ == "__main__":
    run()
