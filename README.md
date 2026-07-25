# nas-web-cpanel

A **cPanel + Softaculous equivalent for the Synology DS1522+** — manage the NAS app
installations and one-click-install packages from a curated catalog. Sibling repo in
the Spike & Chilli Home Network project family (E8).

## The decision (see [docs/RESEARCH.md](docs/RESEARCH.md))
This does **not** need a from-scratch clone. Mature tools already do it. So:
**adopt Portainer CE** as the engine (proven on DSM, management + custom one-click
app templates) and **build the tailored piece** — a curated *Spike-Chilli App Catalog*
(your personal Softaculous) — plus an optional thin dashboard.

## Layout
- **[docs/RESEARCH.md](docs/RESEARCH.md)** — research + the build-vs-adopt decision.
- **[PLAN.md](PLAN.md)** — milestones (E1–E6) / agile board source. **[PROGRESS.md](PROGRESS.md)** — autonomous ledger.
- **[deploy/portainer/](deploy/portainer/)** — stand up the engine on DSM (your action).
- **[catalog/](catalog/)** — the curated one-click app catalog (the custom Softaculous).
- **[app/](app/)** — optional thin custom dashboard (MVP; grown over the autonomous run).
- **[deploy/ALTERNATIVES.md](deploy/ALTERNATIVES.md)** — 1Panel / CasaOS / Cosmos if you want to switch engines.

## "Working version" — what to expect
Deploy Portainer (`deploy/portainer/`), load `catalog/templates.json` → you have a
working app/package manager: browse the catalog, one-click install. The custom `app/`
dashboard is a bonus. **Your part:** the DSM/Container-Manager actions (create the
project, bring it up) — each is documented as a runbook.

## Build model
Autonomous CC build (scheduled wakeups) with a committed `PROGRESS.md`; one HALT
before any live-box action. NAS/DSM operations are Nick's; CC authors code + docs.
