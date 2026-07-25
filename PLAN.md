# nas-web-cpanel — plan of record

**v0.1 (2026-07-24)** · Status: MVP build (autonomous). Decision: docs/RESEARCH.md.
Owner: Nick. Autonomous protocol: `../spike-chilli-network/decisions/autonomous-cc-protocol.md`.

## Goal
A working **app/package manager for the DS1522+** — manage the NAS installations and
one-click-install packages — delivered by adopting **Portainer CE** as the engine and
building a **curated Spike-Chilli app catalog** (Nick's personal Softaculous), plus an
optional thin dashboard. LAN-only, self-hosted, no licence.

## Locked decisions
- **LD1** Engine = Portainer CE (containerised on DSM). Not a from-scratch clone.
- **LD2** Softaculous-equivalent = a curated Portainer **App Templates** catalog
  (`catalog/templates.json`) — the tailored, owned deliverable.
- **LD3** Alternatives documented for later migration: 1Panel (richer store),
  CasaOS/Cosmos. Engine is swappable.
- **LD4** No secrets in the repo/catalog; per-service pattern + dedicated DSM users.
- **LD5** DSM/container operations are Nick's (one HALT before he first runs anything
  on the box); CC authors + commits + pushes.

## Milestones (agile epics → the GitHub board)
- **E1 Engine** — Portainer deploy compose + DSM runbook so Nick can stand it up.
  *(this repo delivers the files; bring-up is Nick's HALT-gated action.)*
- **E2 Catalog (the custom Softaculous)** — curated `templates.json`: common
  self-host apps (one-click) + a "Spike-Chilli Mirror" category (WordPress+DB etc.).
  Self-contained stackfiles under `catalog/stacks/`.
- **E3 Mirror integration** — the 4 mirror stacks (wp-main, wp-gbr, invoiceninja,
  spiritof) + Piwigo as catalog entries, wired to their compose.
- **E4 Panel (optional custom UI)** — thin FastAPI+HTMX dashboard over the Docker
  API: list stacks, status, start/stop, logs; later "install from catalog".
- **E5 Search** — discover packages (Docker Hub / curated index) to add to the catalog.
- **E6 Docs + handoff** — one runbook from zero → working manager on the DS1522+.
- **E7 Portainer setup & branding** — operationalise the running engine (see §7b).
  All of E7 rolls up to portfolio epic **E8** (this whole repo).

## 7b. E7 — Portainer setup & branding backlog

Now that Portainer is deployed and the public catalog loads, these operationalise it.
Grouped; each is a board item (#6). Config/branding is E7.1.

**Branding & UX**
- **E7.1 Branding (config):** custom logo + UI theme/accent + login banner to the
  Spike-Chilli identity (CE supports logo + theme; full whitelabel is Business Ed.).
- **E7.2 UX:** default dashboard view, hide unused features, sensible list densities.

**Networking — the subdomain goal**
- **E7.3 Reverse proxy:** deploy Nginx Proxy Manager (in the catalog) or DSM reverse
  proxy → give every app `<app>.spikechilli.local` instead of ports.
- **E7.4 Portainer hostname + real cert:** `portainer.spikechilli.local` with a proper
  cert (replace the self-signed 9443).

**Access & security**
- **E7.5 Admin hardening:** strong pw, session timeout, disable anonymous access.
- **E7.6 Users/teams + RBAC:** scoped access (e.g. a read-only/Martina account) if wanted.
- **E7.7 Registries:** Docker Hub auth (avoid pull rate limits) + GHCR (for the panel image).

**Stacks & operations**
- **E7.8 Deploy mirror stacks:** bring up wp-main, wp-gbr, invoiceninja, spiritof, piwigo
  as Portainer stacks + restore captured data per each runbook.
- **E7.9 Config backup:** Portainer settings backup + schedule.
- **E7.10 Update strategy:** container image updates (Watchtower or manual) + notifications.
- **E7.11 Stack webhooks:** redeploy-on-push for the app stacks.
- **E7.12 Limits + healthchecks:** per-stack resource limits and health checks.

**Growth / future**
- **E7.13 Extra endpoints:** Portainer agents on other hosts (the Macs; **Proxmox VMs**
  when that lands — ties to the hypervisor concept parked for later).
- **E7.14 Alerting:** stack-down notifications → Uptime Kuma / control-hub.
- **E7.15 Ship the custom App Panel** as a managed stack (GHCR image).

## Definition of "working version" (48h target)
Portainer deployable via `deploy/portainer/` + the curated `catalog/templates.json`
loaded → Nick can one-click-install apps from his own catalog. That is a working
app/package manager. E4 panel is a bonus built over the autonomous wakeups.

## Sequencing / autonomous loop
Runs alongside the mirror captures (separate work). Each wakeup: advance one E1–E6
slice, commit, update PROGRESS.md + the board, reschedule. HALT before instructing
Nick to run anything destructive/live on DSM.
