# Spike-Chilli App Catalog — the custom Softaculous

`templates.json` is a **Portainer App Templates** catalog curated for this NAS. Load
it into Portainer (Settings → App Templates → URL) per `../deploy/portainer/README.md`,
then Portainer's **App Templates** page becomes a one-click installer.

## What's in it (MVP)
- **Multi-container (compose)** — WordPress+MariaDB, Nextcloud+MariaDB
  (`stacks/*.yml`). WordPress here is the same pattern as the mirror sites.
- **Single-container (one-click)** — Uptime Kuma, Vaultwarden, Nginx Proxy Manager,
  Dockge, IT-Tools, Homepage.
- Category **"Spike-Chilli"** tags the items most relevant to this setup (WordPress,
  reverse proxy for `*.spikechilli.local`, dashboard).

## Roadmap (see ../PLAN.md E3/E5)
- Add the 4 mirror stacks (wp-main, wp-gbr, invoiceninja, spiritof) + Piwigo as
  catalog entries wired to their compose.
- Grow the common-app set; add a search/discovery step (Docker Hub / curated index).

## Rules
- **No secrets in templates** — only images + env placeholders the user fills at
  install time. Passwords default to `change-me` and must be changed.
- Stackfiles are fetched by Portainer over git, so the repo (or a NAS-hosted copy)
  must be reachable — see the deploy README's public/NAS options.
