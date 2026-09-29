"""ARGUS Collector Suite Runner (SIH26163)
Executes all configured scanners and saves raw outputs into argus/out/.
"""

import subprocess
import os
import sys

def run_scanners():
    print("==================================================")
    print("           ARGUS Scanner Suite Runner             ")
    print("==================================================")
    
    # 1. Endpoints Cataloging
    print("[*] Generating API endpoints catalog...")
    from .gen_endpoints import generate_endpoints
    generate_endpoints()
    
    # 2. Dependency Audit
    print("[*] Running npm audit...")
    try:
        cmd = "npm audit --json"
        p = subprocess.run(cmd, cwd="worldmonitor", shell=True, capture_output=True, text=True, encoding="utf-8")
        if p.stdout:
            with open("argus/out/npm-audit.json", "w", encoding="utf-8") as f:
                f.write(p.stdout)
            print("[+] Saved argus/out/npm-audit.json")
    except Exception as e:
        print(f"[-] npm audit notice: {e}")
        
    print("[+] Scanner collection completed.")

if __name__ == "__main__":
    run_scanners()
