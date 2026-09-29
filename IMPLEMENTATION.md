# ARGUS: Implementation Guide (SIH26163)

Step-by-step plan to build and demo ARGUS against a **locally hosted** copy of World Monitor.

> **Rule zero:** test only your own local instance (`localhost`). Never scan `worldmonitor.app` or any live deployment. PoCs must be non-destructive.

---

## 0. What you are building

```
Target (local World Monitor)
   -> Scan engines (Semgrep, Gitleaks, OSV, ZAP, Nuclei, Playwright, LLM probes)
   -> Correlation engine (normalise, dedupe, confirm, map OWASP/CWE, CVSS)
   -> Outputs (findings.json, PDF report, dashboard, evidence folder)
```

**Minimum viable demo (must work before anything else):** one command runs the scans, produces `findings.json`, and generates a PDF with at least one evidenced vulnerability.

---

## 1. Team roles (4 people)

| Role | Owns |
|---|---|
| A. Scanner lead | Steps 3-4: run tools, save raw output |
| B. Backend lead | Steps 5-6: correlation engine, CVSS, database |
| C. PoC / security lead | Steps 4, 7: recon, manual triage, PoC scripts, evidence |
| D. Report + UI lead | Steps 8-9: PDF report, dashboard, demo script |

If you are 2-3 people, merge A+C and B+D.

---

## 2. Setup (Day 1, first 2 hours)

**Prerequisites:** Git, Node.js 20+, Python 3.11+, Docker, a Linux/macOS/WSL2 shell.

```bash
# 2.1 Get the target
git clone https://github.com/koala73/worldmonitor.git target/worldmonitor
cd target/worldmonitor
npm install
npm run dev            # opens on http://localhost:3000 (no env vars needed)
```

Check whether the API routes respond locally (open the browser dev tools, Network tab). The app uses Vercel Edge Functions for its API; if `/api/...` calls fail under `npm run dev`, read the repo docs for the local API option (for example `vercel dev`). Record what works: this defines your real attack surface.

```bash
# 2.2 Project skeleton
mkdir -p argus/{collectors,engine,poc,report,dashboard,out,evidence}
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pydantic jinja2 weasyprint cvss playwright requests
playwright install chromium

# 2.3 Install scanners
pip install semgrep
# Gitleaks, OSV-Scanner, Nuclei: install from their GitHub releases or package manager
# OWASP ZAP: run via Docker (see step 4)
```

**Checkpoint:** target loads in the browser; `semgrep --version` works.

---

## 3. Recon (Day 1, 2-3 hours)

Goal: an honest map of what actually exists. Do not assume the PS's roles/BOLA model applies.

1. Read `README.md`, `SECURITY.md`, `package.json`, the `api/` (edge functions), `proto/` (API contracts) and `src-tauri/` folders.
2. List every HTTP endpoint (from the proto/OpenAPI files) into `out/endpoints.csv`: method, path, auth needed?, takes a URL/param?, returns user data?
3. Note trust boundaries: browser to edge function, edge function to third-party sources, renderer to Tauri sidecar (desktop only).
4. Note where content from third-party feeds is rendered in the UI, and where it is sent to an AI summariser.
5. Read `SECURITY.md` "in scope" list. It names edge-function SSRF/injection/auth bypass, key leakage, Tauri IPC, sidecar auth and dependency issues. Also note that some IPC/sidecar/fetch-patch issues were **already disclosed**, so a duplicate finding will not stand out. Aim for new, evidenced ones.

**Deliverable:** `out/attack_surface.md` (table of endpoints + boundaries). This feeds the attack-surface graph in the report.

---

## 4. Run the scanners (Day 1-2)

Save every raw output in `argus/out/` (never edit raw files).

```bash
cd target/worldmonitor

# SAST: source code
semgrep scan --config p/owasp-top-ten --config p/typescript --config p/javascript \
  --sarif -o ../../argus/out/semgrep.sarif .

# Secrets in repo history
gitleaks detect --source . --report-format sarif --report-path ../../argus/out/gitleaks.sarif

# Dependencies
npm audit --json > ../../argus/out/npm-audit.json
osv-scanner scan source -r . --format sarif > ../../argus/out/osv.sarif   # flags vary by version

# DAST baseline (target running on :3000). On Windows/macOS use host.docker.internal instead of localhost
docker run --rm --network host -v "$(pwd)/../../argus/out:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t http://localhost:3000 -J zap-baseline.json -r zap-baseline.html

# Template-based checks (misconfig, exposures)
nuclei -u http://localhost:3000 -severity low,medium,high,critical -jsonl -o ../../argus/out/nuclei.jsonl
```

Optional deeper step: ZAP **active scan** (authorised, local only) on the API paths you listed in recon.

**Checkpoint:** five or more raw files in `argus/out/`.

---

## 5. Test the seven PS scope areas (manual + scripted)

Use recon to decide what applies. Mark each row *tested / not applicable (why)*.

| Scope area | What to check in World Monitor | Where to look |
|---|---|---|
| Authentication and session | Is there a login at all? How is the API key (`wm_...`) sent and stored? Token lifetime and storage | Client code, API key handling, network tab |
| Authorization / access control | Are any endpoints usable without a key that should need one? Do premium routes enforce the key server-side? | Edge functions, API responses with/without key |
| Input validation | Which endpoints take URLs or free-text params? Do they validate and allow-list? Are feed contents escaped before rendering? | Edge functions that fetch external URLs; UI code using `innerHTML` |
| API security | Rate limiting, verbose errors, CORS policy, excessive data in responses | Response headers, error bodies, repeated requests (low volume) |
| Client-side controls | CSP, security headers, secrets in the built bundle, dangerous DOM sinks | Built assets, `index.html` headers, Semgrep hits |
| Secure communication | HSTS, TLS on deployed config, mixed content, fetch interceptors that attach tokens | Headers, Tauri/sidecar code |
| Data storage and privacy | What goes to localStorage/IndexedDB, logs, third-party calls | Browser storage, source |

**LLM feature check (OWASP LLM Top 10):** if the app summarises third-party news with an AI model, test whether text inside a feed item can steer the summary (prompt injection). Use a harmless marker instruction and a local mock feed you control; never a real feed.

---

## 6. Correlation engine (Day 2-3)

**6.1 Common finding schema** (`engine/schema.py`)

```python
from pydantic import BaseModel
from typing import Optional, List

class Finding(BaseModel):
    id: str
    title: str
    tool: str                # semgrep | zap | nuclei | gitleaks | osv | manual
    rule_id: str
    file: Optional[str] = None
    url: Optional[str] = None
    line: Optional[int] = None
    cwe: Optional[str] = None       # e.g. "CWE-79"
    owasp: Optional[str] = None     # e.g. "A03:2021"
    raw_severity: str
    description: str
    evidence: List[str] = []
```

**6.2 Parsers:** one function per tool in `collectors/` that reads its raw file and returns `List[Finding]`. SARIF (Semgrep, Gitleaks, OSV) shares one parser; ZAP and Nuclei need their own.

**6.3 Dedupe + cross-tool confirmation** (`engine/correlate.py`)

```python
def key(f):            # same weakness at same place
    return (f.cwe or f.rule_id, f.file or f.url)

def correlate(findings):
    groups = {}
    for f in findings:
        groups.setdefault(key(f), []).append(f)
    out = []
    for k, items in groups.items():
        tools = {i.tool for i in items}
        confidence = "high" if len(tools) >= 2 else "medium" if items[0].tool == "manual" else "low"
        out.append({"key": k, "findings": items, "tools": sorted(tools), "confidence": confidence})
    return out
```

Then improve the key (map ZAP alert IDs and Semgrep rule IDs to CWE) and optionally cluster near-duplicates with text similarity (see reference 5 in the deck).

**6.4 OWASP / CWE mapping:** a small lookup table `cwe_to_owasp.json` (CWE-79 -> A03, CWE-918 -> A10, CWE-770 -> A04, CWE-942 -> A05, CWE-522 -> A02, CWE-1104 -> A06, ...).

**6.5 CVSS 3.1:** for each confirmed finding, choose the vector by hand (Person C), then compute with the `cvss` package:

```python
from cvss import CVSS3
c = CVSS3("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N")
print(c.scores(), c.severities())
```

Explain each metric in one line in the report. Do not inflate C/I/A beyond what the PoC shows.

**6.6 API + storage:** FastAPI endpoints `POST /scan`, `GET /findings`, `GET /report`; SQLite table for findings and evidence paths.

**Checkpoint:** running `python -m argus.engine.run` outputs `findings.json` from the raw files.

---

## 7. Triage and PoC (Day 3-4)

1. **Triage (mandatory):** open every candidate. Check that untrusted input truly reaches a dangerous sink or that the missing control really matters. Drop false positives and write a one-line reason.
2. **Confirm with a second signal** (code + runtime, or two tools) before building a PoC.
3. **Write a minimal, non-destructive PoC** per finding, saved in `argus/poc/<id>/`:
   - a Playwright or `curl` script that shows the behaviour on `localhost`,
   - expected output,
   - screenshot / HAR saved in `argus/evidence/<id>/`.
4. **Safe-PoC rules:**
   - SSRF: make the server call **a canary listener you run on localhost**, never internal or external systems.
   - XSS / injection: use a harmless marker string and show it is reflected/executed in your own browser session.
   - Rate limiting: send a small, bounded number of requests (for example 30-50), not a flood.
   - Never extract data, persist, or degrade the service.
5. Fill the finding template (title, description, affected component, CVSS, steps, PoC, impact, remediation) in `findings.json`.

**Checkpoint:** at least one finding with all 8 fields and evidence. Aim for 3-5.

### Candidate vulnerabilities to test first (hypotheses, not confirmed findings)

| # | Candidate | OWASP / CWE | How to confirm locally |
|---|---|---|---|
| 1 | SSRF in edge functions that accept a URL/host | A10 / CWE-918 | Point at your localhost canary; check allow-list logic in code |
| 2 | DOM XSS from feed/news content | A03 / CWE-79 | Semgrep `innerHTML` hits + browser test with a mock feed item |
| 3 | No rate limiting on public API | A04 / CWE-770 | Bounded burst, observe no throttling/429 |
| 4 | Permissive CORS / missing headers | A05 / CWE-942 | Header inspection with ZAP/curl |
| 5 | API key/token exposure in client | A02, A07 / CWE-522 | Search built bundle and storage |
| 6 | Prompt injection through feeds into AI | OWASP LLM01 | Mock feed + harmless marker instruction |
| 7 | Vulnerable dependencies | A06 / CWE-1104 | `npm audit` / OSV, check if reachable |
| 8 | Tauri IPC / sidecar trust | A01, A05 / CWE-269 | Code review of `src-tauri` capabilities (partly known already) |

Some of these may not exist. That is fine: report what the evidence shows, including hardening gaps, and mark not-found areas as tested.

---

## 8. Report generation (Day 4)

1. Jinja2 template `report/report.html.j2` with: executive summary (scope, method, counts by severity), findings (one block per finding using the 8 fields), coverage table (7 scope areas), attack-surface diagram, appendix (tools and versions).
2. Render with WeasyPrint: `weasyprint report.html report.pdf`.
3. Keep the report black-and-white and short; put full evidence in the `evidence/` folder.

---

## 9. Dashboard (Day 4-5, only after steps 1-8 work)

React + Vite: a table of findings (filter by severity/OWASP), a finding detail page (PoC steps, evidence, fix), and a coverage matrix. Read data from `findings.json` or the FastAPI endpoint. Skip fancy charts; judges care about evidence.

---

## 10. One-command demo (Day 5)

```bash
# Makefile
demo:
	docker compose up -d target        # local World Monitor
	python -m argus.collectors.run_all # semgrep, gitleaks, osv, zap, nuclei
	python -m argus.engine.run         # normalise, dedupe, confirm, score
	python -m argus.poc.replay         # replays saved PoCs, captures evidence
	python -m argus.report.build       # PDF + findings.json
```

**Demo script (5 minutes):**
1. Show the architecture slide, then run `make demo` (pre-record a backup video).
2. Show raw scanner output vs. correlated findings (noise reduction).
3. Open one finding: PoC replay, screenshot, CVSS vector, fix.
4. Open the PDF report and the coverage table.
5. Point to the scalability path: change the target config, plug into CI.

---

## 11. Timeline (36-hour software edition; adjust to the real schedule)

| Hours | Work |
|---|---|
| 0-3 | Setup, recon, attack-surface map |
| 3-8 | All scanners run, raw outputs saved |
| 8-16 | Correlation engine, schema, CVSS, database |
| 16-24 | Manual triage, PoCs, evidence |
| 24-30 | Report generator, dashboard |
| 30-34 | One-command demo, rehearsal, backup video |
| 34-36 | Feature freeze, final report, submission |

For the **idea PPT stage** (before the hackathon) you only need the slides. Steps above are for the build round.

---

## 12. Submission checklist (idea PPT)

- [ ] Exactly 6 slides (title slide + the 5 template slides); "Important Instructions" slide removed
- [ ] Replace `[Team Name]` (every slide) and `[Team ID]` (title slide) with portal values
- [ ] Exported as **PDF** (the portal accepts only PDF)
- [ ] All references open correctly
- [ ] Vulnerability table labelled as hypotheses until you have real scan results

---

## 13. Ethics and safety

- Local, self-hosted target only. No production systems, no real user data.
- PoC only: no data theft, persistence, or denial of service.
- If you find a real vulnerability, follow the project's `SECURITY.md` (private reporting, no public issues).
- Keep all scripts inside your repo; do not publish exploit tooling against third parties.
