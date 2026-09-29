"""ARGUS PoC Replay Runner (SIH26163)
Executes all safe, non-destructive proofs of concept and generates evidence logs.
"""

from .poc_xss_trusted_html import run_poc as run_poc1
from .poc_ratelimit_failopen import run_poc as run_poc2
from .poc_llm_prompt_injection import run_poc as run_poc3
from .poc_bot_filter_bypass import run_poc as run_poc4
from .poc_ssrf_dns_rebinding_audit import run_poc as run_poc5

def run_all_pocs():
    print("==================================================")
    print("     ARGUS Non-Destructive PoC Replay Suite      ")
    print("==================================================")
    
    results = {}
    pocs = [
        ("PoC 1 (DOM XSS via trustedHtml bypass)", run_poc1),
        ("PoC 2 (Rate Limiter Fail-Open Architecture)", run_poc2),
        ("PoC 3 (LLM Prompt Injection Blocklist Bypass)", run_poc3),
        ("PoC 4 (Middleware Bot Filter Header Bypass)", run_poc4),
        ("PoC 5 (SSRF DNS Rebinding & Socket Pinning)", run_poc5),
    ]
    
    for name, runner in pocs:
        try:
            success = runner()
            results[name] = "PASSED (Vulnerability Evidenced)" if success else "FAILED"
        except Exception as e:
            results[name] = f"ERROR: {e}"
            
    print("\n---------------- PoC Execution Summary ----------------")
    for name, status in results.items():
        print(f"[*] {name}: {status}")
    print("-------------------------------------------------------\n")

if __name__ == "__main__":
    run_all_pocs()
