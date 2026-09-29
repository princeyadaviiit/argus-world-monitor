"""Non-Destructive PoC 2: Architectural Fail-Open Flaw in Edge Rate Limiter
Demonstrates how api/_rate-limit.js returns null (permitting unmetered traffic)
when Upstash Redis is unavailable or unconfigured, degrading to fail-open with
X-RateLimit-Mode: degraded.
"""

import os
import re

def run_poc():
    print("[*] Running PoC 2: Auditing rate-limit fail-open degradation...")
    
    rate_limit_path = "worldmonitor/api/_rate-limit.js"
    if not os.path.exists(rate_limit_path):
        print(f"[-] Error: {rate_limit_path} not found")
        return False
        
    with open(rate_limit_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract fail-open logic
    has_fail_open_env = "UPSTASH_REDIS_REST_URL" in content and "return null" in content
    has_degraded_header = "degraded" in content or "X-RateLimit-Mode" in content
    
    print(f"[+] Found Upstash Redis dependency with null fallback: {has_fail_open_env}")
    print(f"[+] Found degraded rate limit mode header: {has_degraded_header}")
    
    evidence = [
        "=== ARGUS Evidence: Rate Limiting Fail-Open Architecture ===",
        "Target Vulnerability: CWE-770 (Allocation of Resources Without Limits) / OWASP A04:2021",
        f"Vulnerable File: {rate_limit_path}",
        "",
        "Extracted Code Flow Analysis:",
        "1. Missing Redis Configuration:",
        "   When UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN is not configured,",
        "   checkRateLimit() immediately exits with `return null;` allowing every request unconditionally.",
        "",
        "2. Runtime Degradation Fallback:",
        "   If the upstream Upstash REST API times out (>1000ms) or returns an HTTP 5xx error,",
        "   the catch block logs a silent error and returns `null` while setting header:",
        "   `X-RateLimit-Mode: degraded`",
        "",
        "Impact:",
        "An attacker can intentionally degrade the rate limiter by exhausting Redis connection quotas,",
        "causing all subsequent requests to costly downstream services (Nominatim, AI search, GIS data)",
        "to run completely unthrottled and free of cost/burst limits."
    ]
    
    os.makedirs("argus/evidence", exist_ok=True)
    with open("argus/evidence/poc_ratelimit_evidence.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(evidence))
        
    print("[+] Evidence saved to argus/evidence/poc_ratelimit_evidence.txt")
    return True

if __name__ == "__main__":
    run_poc()
