# Deploy Portainer on the DS1522+ (the engine)

Portainer is the management + one-click-install engine. This is a **live-box action —
Nick runs it in DSM** (CC does not operate the NAS). ~5 minutes.

## Steps (DSM 7.2, Container Manager)
1. Create the folder: File Station → `docker/portainer/` (i.e. `/volume1/docker/portainer/`).
   Add a `data/` subfolder.
2. Copy `compose.yaml` from this dir into `/volume1/docker/portainer/`.
3. Container Manager → Project → Create → point at `/volume1/docker/portainer/` →
   it reads `compose.yaml` → Build/Up.
   *(Or SSH: `cd /volume1/docker/portainer && docker compose up -d`.)*
4. Browse **https://<nas-ip>:9443**, create the admin user within a few minutes
   (Portainer locks new-admin creation after a timeout — if it locks, restart the
   container and retry).
5. Choose "Get Started" → manage the **local** Docker environment.

## Load Nick's curated catalog (the Softaculous part) — DONE 2026-07-26
Repo is **public** (sanitized — generic DB placeholders, no account username), and the
App Templates URL is set to:
`https://raw.githubusercontent.com/nickleigh78/nas-web-cpanel/main/catalog/templates.json`
Portainer → **App Templates** now shows the curated list incl. the "Spike-Chilli
Mirror" category. To refresh after catalog edits, re-save the URL in Settings.

⚠️ **Do NOT set up a "Web Station web portal"** for the Portainer project in Container
Manager — DSM auto-offers it and it causes 404s (it proxies as HTTP; Portainer is
HTTPS on 9443). Leave it unchecked; access Portainer directly on its published 9443.

## Security
- LAN-only. Do not port-forward 9443/8000.
- The Docker socket is mounted read-write — required so Portainer can create/manage
  stacks (it is the engine). Keep it LAN-only and admin-protected.

## If you'd rather a richer built-in store
See `../ALTERNATIVES.md` — 1Panel (165+ app store) and CasaOS are documented as
drop-in-later options; the catalog concept carries over.
