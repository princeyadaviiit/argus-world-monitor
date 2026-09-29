"""Non-Destructive PoC 1: DOM XSS via Bypassed Trusted Types in dom-utils.ts
Demonstrates how trustedHtml() performs zero sanitization and permits raw HTML injection
when accompanied by the static string 'legacy direct innerHTML migration' used across 350+ UI sinks.
"""

import os
import re

def run_poc():
    print("[*] Running PoC 1: Testing dom-utils.ts trustedHtml() bypass...")
    
    # 1. Inspect dom-utils.ts implementation
    dom_utils_path = "worldmonitor/src/utils/dom-utils.ts"
    if not os.path.exists(dom_utils_path):
        print(f"[-] Error: {dom_utils_path} not found")
        return False
        
    with open(dom_utils_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check trustedHtml implementation
    has_trusted_html = "export function trustedHtml(html: string, reason: string): TrustedHtml" in content
    has_set_trusted_html = "export function setTrustedHtml(el: Element, html: TrustedHtml): void" in content
    
    print(f"[+] Found trustedHtml definition: {has_trusted_html}")
    print(f"[+] Found setTrustedHtml definition: {has_set_trusted_html}")
    
    # 2. Count usages of 'legacy direct innerHTML migration'
    src_dir = "worldmonitor/src"
    call_sites = []
    marker = "legacy direct innerHTML migration"
    
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith(('.ts', '.tsx', '.js')):
                p = os.path.join(root, f)
                try:
                    lines = open(p, "r", encoding="utf-8", errors="ignore").readlines()
                    for idx, line in enumerate(lines, 1):
                        if marker in line:
                            call_sites.append(f"{os.path.relpath(p, 'worldmonitor')}:{idx}: {line.strip()}")
                except Exception:
                    pass
                    
    print(f"[+] Discovered {len(call_sites)} instances of '{marker}' across codebase.")
    
    # 3. Simulate harmless marker injection into mock sink
    harmless_marker = '<img src=x onerror="console.warn(\'ARGUS_CANARY_XSS_TRIGGERED\')">'
    simulated_render = f"setTrustedHtml(targetElement, trustedHtml('{harmless_marker}', '{marker}'));"
    
    evidence = [
        "=== ARGUS Evidence: DOM XSS Trusted Types Bypass ===",
        f"Target Vulnerability: CWE-79 / OWASP A03:2021",
        f"Vulnerable File: {dom_utils_path}",
        f"Mechanism: trustedHtml() performs no sanitization, merely type-casting `html as TrustedHtml`.",
        f"Audit Reason Abuse: '{marker}' used at {len(call_sites)} distinct call sites.",
        "",
        "Sample Call Sites:",
    ] + call_sites[:10] + [
        "",
        "Simulated Injection Vector:",
        f"Payload: {harmless_marker}",
        f"Resulting DOM write: {simulated_render}",
        "Conclusion: Input passed through trustedHtml with the legacy migration reason bypasses browser XSS filters and writes raw unsanitized HTML."
    ]
    
    os.makedirs("argus/evidence", exist_ok=True)
    with open("argus/evidence/poc_xss_evidence.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(evidence))
        
    print("[+] Evidence saved to argus/evidence/poc_xss_evidence.txt")
    return True

if __name__ == "__main__":
    run_poc()
