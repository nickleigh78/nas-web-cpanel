# app/ — Spike-Chilli App Panel (custom MVP)

The optional thin dashboard (milestone E4). Single-file FastAPI app that lists Docker
containers and can start/stop/restart them, via the mounted docker socket. Portainer
+ the curated catalog remain the install engine; this is the unified glance-and-act view.

## Run it
- **On the NAS:** copy `app/` to `/volume1/docker/app-panel/`, then Container Manager
  → Project → build from `compose.yaml`. Browse `http://<nas>:8099`.
- **Locally (needs Docker):** `pip install -r requirements.txt && uvicorn main:app --port 8099`.

## Status / roadmap
- v0.1 (now): list containers + start/stop/restart + `/healthz`.
- Next (wakeups): stack grouping, logs view, "install from catalog" action, auth,
  resource stats. Tracked on the GitHub board (E4).

Read-only socket mount is used; container actions still require Docker to honour them
(start/stop/restart do). LAN-only — never expose port 8099 publicly.
