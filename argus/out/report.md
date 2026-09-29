# ARGUS Security Assessment Final Report (SIH26163)

**Target:** World Monitor (Local Self-Hosted Instance)  
**Date:** 2026-09-29T12:30:00Z  
**Evaluation Standards:** OWASP Top 10 (2021), OWASP LLM Top 10, CWE, CVSS v3.1  

---

## 1. Executive Summary

This comprehensive security assessment was performed against a locally cloned, self-hosted deployment of **World Monitor** following the **ARGUS Implementation Guide (SIH26163)**. The audit combined static code analysis (Semgrep), dependency composition analysis (npm audit), secret scanning, architectural threat modeling, and 5 non-destructive Proofs of Concept (PoCs).

- **Total HTTP Endpoints Audited:** 166
- **Total Ingested Raw Findings:** 14
- **Correlated Unique Vulnerabilities:** 12
- **Severity Breakdown:**
  - 🔴 **High:** 1
  - 🟡 **Medium:** 11
  - 🔵 **Low / Info:** 0

---

## 2. Seven Problem Statement Scope Areas Coverage Table

| Scope Area | Status | Key Mechanism & Observations |
|---|---|---|
| **1. Authentication & Session** | Tested (Hardened / Edge Bypass) | Clerk JWTs & Pro API keys (`wm_*`) enforced at gateway; desktop uses OS Keychain (Credential Manager). Middleware contains regex heuristic bypass (ARGUS-VULN-005). |
| **2. Authorization & Access Control** | Tested (Hardened) | 137 unauthenticated discovery/feed routes; 29 authenticated Pro routes. Pro entitlement checks cryptographically verified against Convex DB. |
| **3. Input Validation** | **Vulnerable** (DOM XSS / SSRF) | 357 call sites bypass Trusted Types via `trustedHtml()` with placeholder migration reasons. SSRF protected by 428-domain allowlist, but residual DNS rebinding TOCTOU exists in MCP proxy. |
| **4. API Security** | **Vulnerable** (Fail-Open DoS) | Rate limiting via Upstash Redis **fails open** when Redis is unreachable or times out (`X-RateLimit-Mode: degraded`), leaving downstream APIs unthrottled. |
| **5. Client-Side Controls** | Tested (Hardened / DOM Sinks) | CSP restricts inline scripts; UI sinks bypassed by `setTrustedHtml`. |
| **6. Secure Communication** | Tested (Hardened) | HSTS / HTTPS enforced. Tauri IPC sidecar uses CSPRNG `LOCAL_API_TOKEN` with 5-minute TTL. |
| **7. Data Storage & Privacy** | Tested (Hardened) | No secrets stored in `localStorage` (only UI filters/preferences). Desktop secrets stored in OS keychain. |
| **8. AI Security (OWASP LLM01)** | **Vulnerable** (Prompt Injection) | LLM prompt sanitizer relies solely on static regex blocklist; semantic and indirect prompt injections in feeds pass unaltered into AI context. |

---

## 3. High-Priority Evidenced Vulnerabilities

### ARGUS-CONFIRMED-009: Unmetered Resource Consumption via Fail-Open Rate Limiter Degradation
- **Severity:** High (CVSS v3.1: **7.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`)
- **Weakness Mapping:** `CWE-770` | `A04:2021-Insecure Design`
- **Affected Component:** `api/_rate-limit.js, api/_rate-limit-fallback.js`
- **Confidence:** LOW (Confirmed via code-audit)

**Description:**  
The edge function rate limiting subsystem degrades availability-first. When Upstash Redis is unreachable, unconfigured, or times out, checkRateLimit() returns null (allowing requests) and emits `X-RateLimit-Mode: degraded`. This leaves expensive upstream endpoints (such as Nominatim reverse geocode and chat analyst LLM calls) vulnerable to unbounded denial-of-service and provider API quota exhaustion.

**Remediation:**  
For high-cost and third-party bounded endpoints (such as Nominatim and AI inference), enforce fail-closed rate limiting or in-memory token buckets rather than complete unthrottled fail-open.

**Evidence:**  
- `api/_rate-limit.js: catch block and missing-env check return null unconditionally`
- `Emits header 'X-RateLimit-Mode: degraded'`
- `Verified non-destructive PoC in argus/poc/poc_ratelimit_failopen.py`

---

### ARGUS-CONFIRMED-001: @vitest/mocker: Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-22` | `N/A`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package @vitest/mocker (range: >=2.1.0 <4.1.11) has vulnerability: Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock. See advisory: https://github.com/advisories/GHSA-82fw-gwwq-j7x9

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: @vitest/mocker`
- `Advisory: https://github.com/advisories/GHSA-82fw-gwwq-j7x9`
- `Dependency: vitest`
- `Advisory: https://github.com/advisories/GHSA-82fw-gwwq-j7x9`

---

### ARGUS-CONFIRMED-002: image-size: image-size: JXL and HEIF parsers allow denial of service through infinite loops
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-835` | `N/A`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package image-size (range: >=1.2.0 <=2.0.2) has vulnerability: image-size: JXL and HEIF parsers allow denial of service through infinite loops. See advisory: https://github.com/advisories/GHSA-5p2g-fcmc-qvqq

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: image-size`
- `Advisory: https://github.com/advisories/GHSA-5p2g-fcmc-qvqq`
- `Dependency: image-size`
- `Advisory: https://github.com/advisories/GHSA-w3rx-r6r6-pgpr`

---

### ARGUS-CONFIRMED-003: ip-address: ip-address: Address6.isLinkLocal() recognizes fe80::/64 rather than fe80::/10, allowing SSRF and trust-boundary bypass to on-link hosts
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-697` | `N/A`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package ip-address (range: <=10.5.0) has vulnerability: ip-address: Address6.isLinkLocal() recognizes fe80::/64 rather than fe80::/10, allowing SSRF and trust-boundary bypass to on-link hosts. See advisory: https://github.com/advisories/GHSA-rpw4-54j3-4h4q

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: ip-address`
- `Advisory: https://github.com/advisories/GHSA-rpw4-54j3-4h4q`

---

### ARGUS-CONFIRMED-004: ip-address: ip-address: no classifier recognizes the NAT64 local-use range 64:ff9b:1::/48, allowing SSRF and trust-boundary bypass
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-918` | `A10:2021-Server-Side Request Forgery`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package ip-address (range: >=10.2.0 <=10.5.0) has vulnerability: ip-address: no classifier recognizes the NAT64 local-use range 64:ff9b:1::/48, allowing SSRF and trust-boundary bypass. See advisory: https://github.com/advisories/GHSA-2vr4-cq9g-pvrc

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: ip-address`
- `Advisory: https://github.com/advisories/GHSA-2vr4-cq9g-pvrc`

---

### ARGUS-CONFIRMED-005: stream-json: stream-json: pick/ignore/filter/replace filters are O(depth²) on nested input — small crafted JSON blocks the event loop for seconds→minutes (DoS)
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-407` | `N/A`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package stream-json (range: <=3.4.0) has vulnerability: stream-json: pick/ignore/filter/replace filters are O(depth²) on nested input — small crafted JSON blocks the event loop for seconds→minutes (DoS). See advisory: https://github.com/advisories/GHSA-528h-pc64-c93x

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: stream-json`
- `Advisory: https://github.com/advisories/GHSA-528h-pc64-c93x`

---

### ARGUS-CONFIRMED-006: undici: undici vulnerable to Denial of Service via unhandled error in WebSocket permessage-deflate decompression
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-248` | `N/A`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package undici (range: >=7.28.0 <7.29.1) has vulnerability: undici vulnerable to Denial of Service via unhandled error in WebSocket permessage-deflate decompression. See advisory: https://github.com/advisories/GHSA-3wwx-pv8p-q78v

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: undici`
- `Advisory: https://github.com/advisories/GHSA-3wwx-pv8p-q78v`

---

### ARGUS-CONFIRMED-007: uuid: uuid: Missing buffer bounds check in v3/v5/v6 when buf is provided
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-787` | `N/A`
- **Affected Component:** `package.json`
- **Confidence:** MEDIUM (Confirmed via npm-audit)

**Description:**  
Package uuid (range: <11.1.1) has vulnerability: uuid: Missing buffer bounds check in v3/v5/v6 when buf is provided. See advisory: https://github.com/advisories/GHSA-w5hq-g745-h8pq

**Remediation:**  
Apply input sanitization, strict boundary checks, and defensive controls.

**Evidence:**  
- `Dependency: uuid`
- `Advisory: https://github.com/advisories/GHSA-w5hq-g745-h8pq`

---

### ARGUS-CONFIRMED-011: Indirect Prompt Injection Blocklist Bypass in LLM News Summarizer
- **Severity:** Medium (CVSS v3.1: **6.5** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-20` | `OWASP-LLM01-Prompt-Injection`
- **Affected Component:** `server/_shared/llm-sanitize.js, api/chat-analyst.ts`
- **Confidence:** LOW (Confirmed via code-audit)

**Description:**  
External news feeds and user search parameters are passed into LLM prompts after passing through sanitizeForPrompt(). The sanitizer relies solely on static regex blocklists for English override phrases ('ignore previous instructions', etc.). Novel semantic paraphrasing, multilingual instructions, and indirect prompt injections inside external RSS feeds pass through completely unaltered.

**Remediation:**  
Implement structural delimiters (such as XML tags with strict schema parsing) around untrusted external content, enforce output validation, and avoid granting sensitive tool-execution capabilities to LLM analysts ingesting raw web feeds.

**Evidence:**  
- `server/_shared/llm-sanitize.js:31-72 regex patterns`
- `Comments in source explicitly state: 'Prompt-injection blocklists are inherently bypassable'`
- `Verified non-destructive PoC in argus/poc/poc_llm_prompt_injection.py`

---

### ARGUS-CONFIRMED-010: Server-Side Request Forgery (SSRF) via DNS Rebinding TOCTOU in MCP Proxy
- **Severity:** Medium (CVSS v3.1: **6.3** - `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N`)
- **Weakness Mapping:** `CWE-918` | `A10:2021-Server-Side Request Forgery`
- **Affected Component:** `api/mcp-proxy.ts, api/_notification-webhook-ssrf.ts`
- **Confidence:** LOW (Confirmed via code-audit)

**Description:**  
api/mcp-proxy.ts verifies target host IP addresses via Cloudflare DNS-over-HTTPS before outbound calls. However, Vercel Edge Runtime fetch() does not support socket pinning or pre-resolved IP connections. An attacker controlling a custom domain with zero TTL can exploit the Time-of-Check to Time-of-Use (TOCTOU) window between DNS validation and fetch connection to bind to internal/link-local cloud metadata services.

**Remediation:**  
Migrate the MCP proxy and webhook fetchers to a Node.js runtime environment supporting custom HTTP agents with socket-level IP address pinning (e.g., using `undici` or `agentkeepalive` with pre-vetted socket binding).

**Evidence:**  
- `api/mcp-proxy.ts: pre-resolution step separate from edge fetch()`
- `SECURITY.md Line 52 acknowledged residual (draft GHSA-887j-p88r-qmm9)`
- `Verified non-destructive PoC in argus/poc/poc_ssrf_dns_rebinding_audit.py`

---

### ARGUS-CONFIRMED-008: DOM-based Cross-Site Scripting (XSS) via Bypassed Trusted Types in dom-utils.ts
- **Severity:** Medium (CVSS v3.1: **6.1** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`)
- **Weakness Mapping:** `CWE-79` | `A03:2021-Injection`
- **Affected Component:** `src/utils/dom-utils.ts, StoryModal.ts, TransitChart.ts`
- **Confidence:** LOW (Confirmed via code-audit)

**Description:**  
trustedHtml(html, reason) performs an uninspected type-cast (`html as TrustedHtml`) with no sanitization or DOMPurify validation. Across the codebase, over 350 call sites supply the static placeholder reason 'legacy direct innerHTML migration' to bypass Trusted Types, allowing unescaped dynamic HTML from feeds, URL parameters, and external data to reach setTrustedHtml (innerHTML).

**Remediation:**  
Implement a real sanitizer (such as DOMPurify) inside trustedHtml() or safeHtml(). Deprecate the 'legacy direct innerHTML migration' escape hatch and enforce strict TrustedHTML policies.

**Evidence:**  
- `src/utils/dom-utils.ts:65: trustedHtml(html, reason) { return html as TrustedHtml; }`
- `357 call sites use 'legacy direct innerHTML migration' as bypass reason`
- `Verified non-destructive PoC in argus/poc/poc_xss_trusted_html.py`

---

### ARGUS-CONFIRMED-012: Bot and Crawler Filter Bypass via Heuristic API Key Header
- **Severity:** Medium (CVSS v3.1: **5.3** - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`)
- **Weakness Mapping:** `CWE-269` | `A07:2021-Identification and Authentication Failures`
- **Affected Component:** `worldmonitor/middleware.ts`
- **Confidence:** LOW (Confirmed via code-audit)

**Description:**  
In middleware.ts, requests from automated scrapers (matching BOT_UA or short UA) are blocked with HTTP 403. However, the edge middleware checks only the structural shape of the x-api-key / x-worldmonitor-key header (matching /^wm_[a-f0-9]{40,64}$/). Any client supplying a synthetic key matching this regex immediately returns without triggering the bot block, completely bypassing the crawler filter at the edge.

**Remediation:**  
Do not bypass crawler/bot rate limits solely based on unverified client-supplied header formats. Either perform cryptographic token verification at the edge or apply bot rate limits across all incoming requests.

**Evidence:**  
- `middleware.ts:346-353 regex heuristic bypass`
- `Verified non-destructive PoC in argus/poc/poc_bot_filter_bypass.py`

---

