"""ARGUS Master Pipeline Runner (SIH26163)
One-command execution of Scanners -> Correlation Engine -> PoC Replay -> PDF/HTML Report.
"""

import time
from .collectors.run_all import run_scanners
from .engine.run import run as run_engine
from .poc.replay import run_all_pocs
from .report.build import build_all_reports

def main():
    start = time.time()
    print("==================================================================")
    print("      ARGUS AUTOMATED SECURITY AUDIT & REPORTING PIPELINE        ")
    print("==================================================================")
    
    print("\n>>> STEP 1: Running Scanners & Extracting Attack Surface...")
    run_scanners()
    
    print("\n>>> STEP 2: Executing Non-Destructive Proof of Concept (PoC) Suite...")
    run_all_pocs()
    
    print("\n>>> STEP 3: Normalizing Findings, Deduplication, & CVSS Scoring...")
    run_engine()
    
    print("\n>>> STEP 4: Generating Final PDF, HTML, and Markdown Reports...")
    build_all_reports()
    
    duration = time.time() - start
    print(f"\n[+] Pipeline execution finished in {duration:.2f} seconds.")
    print("[+] Outputs available in argus/out/ (report.pdf, report.html, report.md, findings.json)")

if __name__ == "__main__":
    main()
