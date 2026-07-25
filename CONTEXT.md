# nas-web-cpanel — Claude Code context

Project: Spike & Chilli Home Network
Epic: E8 Applications & Services
Role: A **cPanel + Softaculous equivalent for the DS1522+** — manage the NAS app
  installations and one-click-install packages from a curated catalog. Promoted
  2026-07-24 from the D8 decision in `../nickleigh-info-local`.
Parent planning: ../spike-chilli-network/instructions/master-doc.md
Plan-of-record: PLAN.md · Research + the build-vs-adopt decision: docs/RESEARCH.md
Phase/Status: **MVP build (autonomous)** — decision made (adopt Portainer engine +
  build a curated Spike-Chilli catalog + optional thin panel). See PROGRESS.md.

## The decision in one line
Do NOT reinvent cPanel/Softaculous. **Adopt Portainer CE** (proven on DSM,
management + custom app-template catalog) and **build the tailored piece**: a curated
Portainer-compatible app catalog (`catalog/templates.json`) = Nick's personal
Softaculous; plus an optional thin dashboard (`app/`). Full reasoning: docs/RESEARCH.md.

## Repo layout
- `deploy/portainer/` — compose + runbook to stand up the engine on DSM (Nick's action).
- `catalog/` — the curated app catalog (templates.json + stackfiles) — the custom deliverable.
- `app/` — optional thin FastAPI+HTMX panel (built incrementally over wakeups).
- `docs/RESEARCH.md` — research + decision. `PLAN.md` — milestones/agile. `PROGRESS.md` — ledger.

## Conventions (inherited)
Per-service pattern: `/volume1/docker/<service>/` + compose + gitignored `.env` +
dedicated no-shell DSM user + `<service>.spikechilli.local`. LAN-only. No secrets in
git or in the catalog. NAS/DSM container operations are Nick's; CC authors files,
commits, pushes, and (for the panel) writes code.

Remotes: **GitHub** `github.com/nickleigh78/nas-web-cpanel` (agile PM lives here).
Sensitive data stays off GitHub (catalog carries no secrets — only images + env
placeholders).
