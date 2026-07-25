# Research + decision — a cPanel + Softaculous equivalent for the DS1522+

Date: 2026-07-24 · Author: CC (autonomous) · Status: **DECIDED** (see §4).
Question posed by Nick: *"Is there an existing item that enables this, or must it be
custom built?"* — and if custom, create the project and build it.

## 1. What Nick actually wants (the two halves)
- **cPanel half** — a management surface for the NAS installations: see/start/stop
  apps, logs, resources, one screen.
- **Softaculous half** — search for, add, and **one-click install** packages/apps
  onto the server from a catalog.
Constraints: runs on a **Synology DS1522+** (DSM 7.2, Container Manager), LAN-only,
self-hosted, no per-server licence, must coexist with the per-service docker pattern
this portfolio already uses.

## 2. Existing tools surveyed (2026)

| Tool | Management | App store / one-click | Runs on DSM Container Manager? | Notes |
|---|---|---|---|---|
| **1Panel** | ✅ strong (Docker, DBs, websites, backups) | ✅ **built-in app store, 165+ apps** | ~ (designed to manage a Linux host; container-on-DSM less proven) | The single closest match to *cPanel+Softaculous*, Docker-native, open-source |
| **Portainer CE** | ✅ excellent (containers, stacks, registries) | ✅ **App Templates** (one-click, and **custom template URLs**) | ✅ **very well-proven on DSM** (many guides) | Battle-tested containerised install; template catalog is curatable |
| **CasaOS** | ✅ friendly | ✅ polished app store, one-click | ~ (an OS-overlay; runs in Docker but wants more of the host) | Best consumer app-store UX |
| **Cosmos** | ✅ + reverse-proxy/auth/SSO/HTTPS | ✅ app store, auto HTTPS per app | ~ | Adds security/proxy layer; newer |
| **Dockge** | ✅ compose-stack manager (lovely) | ❌ no store | ✅ proven on DSM | Great for editing/running compose, no catalog |
| **CapRover / Cloudron** | ✅ PaaS | ✅ one-click apps | Cloudron wants own OS; CapRover Docker/Swarm | More devops/PaaS-shaped |
| **aaPanel / VestaCP** | ✅ classic cPanel-style | ✅ (VestaCP literally bundles Softaculous) | ✗ (want their own LAMP host, not DSM Docker) | Traditional panels, not Docker-native |
| DSM Container Manager (built-in) | basic | ✗ | n/a | What Nick has today; not enough |

## 3. Finding
**A from-scratch clone is NOT required.** Several mature, open-source tools already
deliver both halves. Reinventing container orchestration + an app store would be
wasteful and could not reach their quality/robustness in 48 h. The honest engineering
call is **adopt an existing engine**; the only real gap is that none arrives
*pre-curated to Nick's server* — his mirror stacks (wp-main, wp-gbr, invoiceninja,
spiritof, piwigo) and the portfolio's per-service conventions (dedicated DSM user,
`<app>.spikechilli.local`, LaCie/NAS paths).

## 4. DECISION (2026-07-24)
**Adopt-and-tailor, not build-from-scratch.**

1. **Engine = Portainer CE**, deployed as a container on the DS1522+. Rationale:
   the most-proven containerised install on DSM, strong management, and it accepts a
   **custom App Templates URL** — so its one-click catalog is fully curatable. Lowest
   risk to reach "working in 48 h".
2. **The custom build (the tailored deliverable) = a curated "Spike-Chilli App
   Catalog"** — a Portainer-compatible `templates.json` pre-loaded with Nick's own
   mirror stacks + a set of common self-host apps, giving him a **personal
   Softaculous** inside Portainer. This is the genuinely additive, owned piece.
3. **Optional custom panel (`app/`)** — a thin FastAPI+HTMX dashboard unifying the
   view of the mirror sites (reusing control-hub patterns), built incrementally over
   the autonomous wakeups. Backed by the Docker Engine API; it delegates heavy
   lifting to Portainer/Docker rather than reimplementing it.
4. **Documented alternatives to migrate to later:** **1Panel** (richer built-in app
   store — evaluate a container-on-DSM install), CasaOS/Cosmos (nicer store UX).
   Kept in `deploy/` notes so switching engines is a small step.

### Why this still honours "build me something"
Nick gets an owned, tailored artifact (the curated catalog + optional panel) AND a
genuinely working app/package manager in 48 h — on a robust foundation instead of a
fragile scratch build. If Nick prefers a pure all-in-one, the research points cleanly
to 1Panel/CasaOS; this decision is transparent so he can redirect on check-in.

## 5. Sources
- Portainer on Synology DSM 7: https://oneuptime.com/blog/post/2026-03-20-portainer-synology-nas-dsm7/view
- Portainer vs CasaOS: https://oneuptime.com/blog/post/2026-03-20-portainer-vs-casaos-home-server/view
- 1Panel (open-source cPanel/Plesk alternative): https://www.opensourcealternatives.to/item/1panel
- Cosmos vs CasaOS vs Umbrel: https://cloudzy.com/blog/cosmos-cloud-vs-casaos-vs-umbrel/
- Portainer vs Cosmos: https://cloudzy.com/blog/portainer-vs-cosmos-cloud/
- Synology container mgmt tools (Marius Hosting): https://mariushosting.com/synology-best-docker-containers-to-manage-containers/
- Softaculous alternatives: https://alternativeto.net/software/softaculous
