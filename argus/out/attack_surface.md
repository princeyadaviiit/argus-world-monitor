# World Monitor - Threat Model & Attack Surface Map (ARGUS Recon)

## 1. System Overview & Architecture

World Monitor (`worldmonitor`) is an OSINT intelligence dashboard aggregating global news, conflicts, markets, geocoding, flight telemetry, satellite imagery, maritime AIS, and prediction markets. It functions both as a web client deployed via Vercel Edge Functions and as a desktop application built on Tauri 2.0 (Rust backend + webview frontend).

```
[Browser / Desktop Webview Client]
       │
       ▼ (HTTPS / TLS 1.3 / Tauri IPC)
┌─────────────────────────────────────────────────────────────┐
│ Edge Gateway & Middleware (Vercel Edge / Sebuf RPC)         │
│  - Middleware: Bot gating (BOT_UA regex), .md twin routing  │
│  - CORS Policy: Dynamic origin check via _cors.js           │
│  - Auth Layer: Clerk Bearer JWTs + wm_* API keys            │
│  - Rate Limiter: Upstash Redis (Sliding window / Token)     │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
       (Outbound HTTP/RPC)             (Upstream Relays)
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│ Third-Party OSINT Providers  │ │ Railway Internal Relay      │
│  - RSS / News Feeds          │ │  - RSS bypass proxy         │
│  - Nominatim Geocoder        │ │  - Sentry / Logging relay   │
│  - OpenSky / Aviation        │ │  - Push Notifications       │
│  - Polymarket / GDELT        │ └─────────────────────────────┘
└──────────────────────────────┘
```

---

## 2. Trust Boundaries

| Boundary ID | Boundary Name | Description | Threats & Controls |
|---|---|---|---|
| **TB-1** | Browser to Edge Function | Public Internet to Vercel Edge Functions | Unauthenticated access, parameter tampering, SSRF via proxy endpoints, abuse/flooding, CORS bypass. Handled by `middleware.ts`, `_cors.js`, `_rate-limit.js`. |
| **TB-2** | Edge Function to Third-Party Services | Edge Runtime fetching external APIs, RSS feeds, Nominatim, LLM APIs | Server-Side Request Forgery (SSRF), DNS rebinding, prompt injection via untrusted content, response desync. Protected by domain allowlists (`_rss-allowed-domains.js`), IP filters (`_notification-webhook-ssrf.ts`). |
| **TB-3** | Renderer to Tauri Desktop Sidecar | Webview UI communicating with Rust Tauri IPC and local sidecar daemon | IPC privilege escalation, unauthorized local process communication. Protected by `LOCAL_API_TOKEN` CSPRNG token with 5-minute TTL, window origin restriction, OS Credential Vault. |
| **TB-4** | Client-Side Storage & DOM Rendering | Third-party feed items, summaries, and parameters rendered into HTML | DOM Cross-Site Scripting (XSS), script injection. Over 350 usages of `setTrustedHtml(..., trustedHtml(..., 'legacy direct innerHTML migration'))` bypassing static Trusted Types checks. |
| **TB-5** | Edge to Upstash Redis & Convex DB | Edge worker querying state, cache, rate limits, and entitlements | Cache poisoning, Redis credential exposure, rate limit bypass during fail-open degradation modes. |

---

## 3. Attack Surface Entry Points Summary

- **Total Discovered HTTP Endpoints:** 166
- **Unauthenticated Endpoints:** 137 (including public metrics, feeds, market proxies, and tool discovery)
- **Authenticated Endpoints:** 29 (requiring Pro key `wm_...`, Clerk JWT, or `RELAY_SHARED_SECRET`)
- **Endpoints Accepting Remote URLs / Parameters:** 52
- **Endpoints Returning User / Session Data:** 24

---

## 4. High-Value Attack Vectors

1. **Server-Side Request Forgery (SSRF) & Redirect Bypasses:**
   - Primary routes: `/api/rss-proxy`, `/api/mcp-proxy`, `/api/notification-channels`.
   - Security controls: Strict domain allowlist (428 domains) on RSS proxy, RFC-compliant private IPv4/IPv6 classification on notification webhooks. Residual risk: DNS rebinding during edge `fetch` connection window.

2. **DOM-based XSS via News & RSS Feed Ingestion:**
   - Ingestion points: `src/services/rss.ts`, `src/services/breaking-news-alerts.ts`.
   - Rendering sinks: `src/utils/dom-utils.ts` (`trustedHtml` cast bypasses audit reasons), `StoryModal.ts`, `TransitChart.ts`, `SettingsWindow.ts`.

3. **Rate Limiting & Denial of Service:**
   - `_rate-limit.js` degrades to **fail-open** if Upstash Redis credentials are unset or the service times out (`X-RateLimit-Mode: degraded`).
   - Unauthenticated high-cost endpoints: `/api/reverse-geocode`, `/api/ask`.

4. **Prompt Injection (OWASP LLM01):**
   - Routes: `/api/ask`, `/api/chat-analyst`, `src/services/summarization.ts`.
   - Threat: Malicious instructions embedded in external news feeds or headlines attempting to override analyst system instructions.

5. **Client-Side Secret & Token Storage:**
   - Web application stores state in `localStorage` and `sessionStorage`.
   - Desktop application securely leverages OS keychain (Windows Credential Manager / macOS Keychain).

6. **Outdated / Vulnerable Dependencies (OWASP A06):**
   - 28 vulnerabilities identified in dependency graph (10 High, 18 Moderate), including transitive vulnerabilities in build tools, parsers, and test runners.
