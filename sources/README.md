# SIH26163 — Security Assessment of the World Monitor Application

> **Organization:** National Technical Research Organisation (NTRO)
> **Category:** Software · **Theme:** Smart Automation
> **Deadline:** 30 September 2026

---

## 1. Problem Statement (Official)

**Background**
The World Monitor application is a Web/Mobile platform that provides users with real-time monitoring, analytics, and reporting features. It handles user authentication, data visualization, API communication, and role-based access controls.

As a security analyst, the task is to evaluate the application's security posture and identify vulnerabilities that could compromise the confidentiality, integrity, or availability of the system.

**Description — what you must do**
1. Identify security vulnerabilities in the application.
2. Assess the potential impact of each vulnerability.
3. Demonstrate proof-of-concept exploitation in a controlled environment.
4. Recommend remediation measures to mitigate identified risks.

**Scope**
- Authentication and session management
- Authorization and access control
- Input validation and data handling
- API security
- Client-side security controls
- Secure communication mechanisms
- Data storage and privacy protections

**Success Criteria**
- At least one valid vulnerability is identified and documented
- Evidence supports the existence of the vulnerability
- Risk and impact are clearly explained
- Practical mitigation strategies are provided

**Expected Deliverable — per vulnerability**
- Vulnerability title
- Description
- Affected component
- Severity rating (CVSS)
- Steps to reproduce
- Proof of concept (safe testing environment)
- Business impact assessment
- Remediation recommendations

**Constraints**
- Testing only on authorized systems
- No impact on production users or data
- Exploitation limited to PoC validation only
- Must comply with applicable laws, policies, and ethical hacking guidelines

---

## 2. Why This Problem Statement Matters

- **Not synthetic security theater.** The target — [`worldmonitor`](https://github.com/koala73/worldmonitor) — is a real, self-hostable open-source project (AGPL-3.0), so genuine, valid vulnerabilities are possible. Teams working on this PS have already surfaced real issues (IPC command exposure, renderer-to-sidecar trust boundary gaps, credential-injection in fetch patching) that the maintainer acknowledged in the repo's own security page.
- **Transferable, employable skill.** Structured VAPT (Vulnerability Assessment & Penetration Testing) with CVSS scoring and remediation write-ups is standard day-to-day AppSec engineering work — not a one-off hackathon gimmick.
- **NTRO's real interest** is in a reusable, automated *assessment methodology/tool*, not a single manual pentest report — build for reusability, not a one-shot script.

---

## 3. Use Case

Build a **mini automated AppSec audit platform**, reusable beyond this one app:

- **Input:** target web/mobile app (source code + running instance)
- **Output:** structured vulnerability report — findings, evidence, CVSS scores, PoCs, remediation — both machine-readable (JSON) and human-readable (PDF/HTML executive report)
- **Real-world analog:** a scaled-down version of Burp Suite Enterprise / Qualys WAS / Rapid7 InsightAppSec, purpose-built and explainable for a hackathon judge audience.

---

## 4. Feasibility — Should You Take This PS or Switch?

**Overall: High feasibility**, with real caveats.

### Why it's tractable
- Success only requires **one** valid, well-documented vulnerability — realistically achievable against most non-trivial apps (missing rate limiting, verbose errors, weak session handling, CORS misconfig, missing security headers, IDOR, etc.)
- Target is open-source and self-hostable — no waiting on NTRO for sandbox access
- Off-the-shelf tooling (OWASP ZAP, Nuclei, Semgrep) automates most discovery, freeing your team to focus on orchestration/reporting — the part that actually differentiates a submission

### Risks to weigh
- **Judged by people with real AppSec background.** Shallow "ran ZAP, pasted output" submissions are easy to spot. Differentiation requires real engineering: SAST+DAST correlation, deduplication, automated CVSS scoring, PoC generation.
- **Crowded PS.** At least 7+ public GitHub repos already exist specifically for SIH26163 (team names include Threat Lens/SUDARSHAN, Sentinel Trinity, Watchtower, Aegis, Sentinel projects). Most converge on "SAST+DAST+CVSS+PDF report." You need a distinguishing angle.
- **Legal/ethical guardrails are non-negotiable.** Scan only your own locally self-hosted instance — never worldmonitor.app or any live deployment.
- **Scope discipline matters.** The PS's assumed threat model (seeded admin/user/viewer accounts, BOLA, privilege escalation) doesn't map cleanly onto how World Monitor's self-hosted mode actually works in some configs (no login system). Recon before committing to an attack plan.

### Verdict
- **Take it** if your team has (or wants to build) real AppSec/DevSecOps skills — it's honest, well-scoped, and has genuine real-world credibility.
- **Skip it** if your team's strength is ML/data-science/mobile-app-building and nobody wants to touch security tooling — a skills mismatch is the actual risk here, not the PS itself.

---

## 5. Recommended Tech Stack

| Layer | Suggested Tools | Why |
|---|---|---|
| Target | Self-hosted `worldmonitor` (Docker/npm, localhost only) | The sanctioned target |
| SAST (source scan) | Semgrep, or SonarQube for JS/TS | Fast, strong OWASP Top 10 / CWE coverage |
| DAST (running-app scan) | OWASP ZAP | Most widely used free/open-source dynamic scanner; strong on broken access control |
| API security | Nuclei (templates), Postman/Newman | Directly targets the "API security" scope item |
| Orchestration | Python (FastAPI) gluing SAST+DAST output, deduplicating findings, mapping to CWE/OWASP | Main engineering differentiator |
| Severity scoring | CVSS 3.1 calculator (automatable, first.org spec) | PS explicitly requires CVSS ratings |
| Evidence / PoC capture | Playwright/Selenium — scripted reproduction + screenshots/video | Satisfies "steps to reproduce + PoC" safely |
| Storage | PostgreSQL / SQLite | Findings + evidence metadata |
| Reporting | Jinja2/WeasyPrint → PDF, or React dashboard | PS wants an "executive report" |
| Dashboard (optional) | React + Vite | Matches the target's own stack — nice narrative symmetry for the demo |

---

## 6. Where the Data Comes From

- **The application itself:** clone [`worldmonitor`](https://github.com/koala73/worldmonitor) from GitHub, self-host locally (`npm install && npm run dev`, or Docker) — becomes your live DAST target and SAST source tree. This is the "attached dataset" referenced by the official PS.
- **Findings dataset:** generated by you, by running your pipeline against your local instance — you are not downloading a pre-made vulnerability dataset.
- **Reference taxonomies** (inputs, not data): OWASP Top 10:2021, CWE Top 25, CVSS 3.1 spec — used to classify and score findings.
- **Practice targets** (optional, before pointing at the real app): OWASP Juice Shop, WebGoat, DVWA — standard, legal, intentionally-vulnerable apps used in published DAST research for scanner validation.

---

## 7. Working Demonstration Plan (Day-by-Day)

1. **Recon & scoping (Day 1)** — self-host worldmonitor, map real attack surface (auth flow or its absence, API endpoints via Protocol Buffer/HTTP contracts, client-side storage, third-party feeds). Verify assumptions against the PS's assumed threat model rather than trusting it blindly.
2. **Baseline automated scans (Day 1–2)** — Semgrep over source, ZAP baseline + active scan against the local instance, Nuclei against exposed API routes.
3. **Manual triage (Day 2–3)** — deduplicate scanner output, discard false positives. This step is what separates real analysis from raw tool noise.
4. **PoC development (Day 3–4)** — for top 3–5 findings, script safe, reproducible demonstrations (e.g., Playwright script showing an IDOR or missing auth check) with screenshots/logs as evidence. Never destructive actions.
5. **CVSS scoring + business impact (Day 4)** — score each finding; describe realistic attacker outcomes (data exposure, spoofed telemetry, dashboard DoS) tied to what World Monitor actually does.
6. **Report + dashboard generation (Day 5)** — auto-generate the PDF executive report and a live findings dashboard.
7. **Demo script for judges:** run the orchestration pipeline end-to-end against the local target → live PoC of one finding → generated report. A "click one button, get a full VAPT report" narrative reads as genuine "Smart Automation," not a manual ZAP run.

---

## 8. Research Papers & Further Reading

- Qadir, Waheed, Khanum & Jehan (2025). *Comparative evaluation of approaches & tools for effective security testing of Web applications.* PeerJ Computer Science. Empirically tests 75 real web apps with 4 SAST + 5 DAST tools, mapped to OWASP Top 10:2021 / CWE Top 25:2023.
  https://peerj.com/articles/cs-2821.pdf

- *A methodology for evaluating DAST scanners* (2025). Springer, 2025. Compares ZAP, Wapiti, w3af, Codename SCNR against OWASP Juice Shop and VulnerableApp.
  https://link.springer.com/article/10.1007/s10207-025-01054-8

- *A Novel VAPT Algorithm: Enhancing Web Application Security Through OWASP Top 10 Optimization* (2023). arXiv:2311.10450.
  https://arxiv.org/pdf/2311.10450

- *Do I really need all this work to find vulnerabilities? An empirical case study comparing vulnerability detection techniques on a Java application.* arXiv:2208.01595. Walks through the practical SAST/DAST workflow (setup → run → triage false positives → report).
  https://arxiv.org/pdf/2208.01595

- Doupé, Cova & Vigna — evaluation of eleven black-box web vulnerability scanners, introducing the WackoPicko benchmark app (referenced in the Springer 2025 paper above). Found effective crawling is as important as detection technique, and entire vulnerability classes remain hard for scanners to catch.

- OWASP Testing Guide v4 / OWASP Top 10:2021 / CWE Top 25 — normative references judges will expect you to cite for classification and severity.

- FIRST.org CVSS 3.1 Specification Document — scoring methodology reference.

---

## 9. Reference Target

- **World Monitor (upstream repo):** https://github.com/koala73/worldmonitor
- License: AGPL-3.0-only (non-commercial self-hosting and forking permitted with attribution)
- Quick start:
  ```bash
  git clone https://github.com/koala73/worldmonitor.git
  cd worldmonitor
  npm install
  npm run dev
  ```
  Runs locally with no environment variables required for basic operation.

---

### ⚠️ Ethical Note
All testing described here must be performed **only** against your own locally self-hosted instance of World Monitor — never against `worldmonitor.app` or any other live/production deployment. Exploitation is PoC-only; no destructive, data-exfiltrating, or denial-of-service actions against real users or systems.
