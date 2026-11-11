# Portainer update runbook — guidance only, NOT for autonomous execution

**Status:** authored 2026-08-16 (post-renumber sweep, Block E). **Performing this update is a
Nick-only action** — Portainer manages every stack on the NAS (piwigo, the 4 hosting mirrors, the
media-automation *arr stack), so a botched update has portfolio-wide blast radius. This doc is
guidance to make that update safe and fast when Nick chooses to do it; nothing here should be run
autonomously.

## Current → target

> **Update history:** `2.21.5` -> `2.39.6` (2026-08-16) -> `2.45.1` (2026-09-21) -> `2.45.3` (2026-11-11). Keep this line
> current when you bump — the "Current" value below went stale once already.

- **Current (as of 2026-09-21, pre-update):** Portainer CE `2.39.6`, pinned in
  `deploy/portainer/compose.yaml`, deployed at `/volume1/docker/portainer/` on the DS1522+.
- **NOTE — there are TWO live LTS lines.** Checked 2026-09-21: `2.39.8` (2026-09-16) is maintenance
  on the older LTS line, and `2.45.1` (2026-09-17) is the current LTS. **Both carried the same
  critical CVE fixes** (CVE-2026-39821 et al. via kubectl 1.37.0 + Alpine/Go bumps), so a security
  need alone does not force the bigger jump — check which line you are on before assuming "newest =
  required". `2.45.1` additionally hardens SSRF in Helm chart resolution and Git operations, and its
  release notes state **no breaking changes / no deprecations**. `2.39.8` additionally fixes an
  updater health-check bug that could skip rollback on a failed upgrade.
- **Target:** the current **LTS** release is the safer default for a box this many other stacks
  depend on (STS moves faster, more surface for a regression to hit something live). Check
  [docs.portainer.io/release-notes](https://docs.portainer.io/release-notes) for the exact current
  LTS tag before updating — versions move; don't hardcode a number here that will go stale. As of
  this writing the LTS track was at `2.39.x`; STS was well ahead at `2.44.x`. **Do not jump straight
  to the newest STS on a production-adjacent box** — prefer the LTS unless a specific STS feature is
  needed.
- 2.21.5 → current LTS is a large multi-version jump. Skim the release notes for breaking changes
  between the two (auth changes, API changes any custom tooling depends on, deprecated
  environment/template formats) before updating — don't assume "it'll just work" across that many
  versions. The curated catalog (`catalog/templates.json`) and the custom FastAPI panel are the
  two things most likely to be sensitive to a Portainer API/template-schema change; smoke-test both
  after.

## Deployment shape (matters for the backup step)

This install mounts its data as a **bind mount** (`./data:/data`, i.e.
`/volume1/docker/portainer/data`), **not** a named Docker volume — simpler to back up than the
generic "`docker run --rm -v portainer_data:/data ... tar`" pattern most Portainer docs show; a
plain file copy of that directory is a complete backup.

## Procedure

1. **Backup the data directory** — from an NAS SSH session (or DSM File Station):
   ```sh
   cd /volume1/docker/portainer
   tar czf /volume1/docker/portainer-data-backup-$(date +%Y%m%d-%H%M).tar.gz data/
   ```
   Verify the archive is non-trivial in size and lists the expected files
   (`tar tzf <archive> | head`) before proceeding — a 0-byte or empty backup is worse than no
   backup (false confidence).
2. **Bump the image tag** in `deploy/portainer/compose.yaml` (`image: portainer/portainer-ce:<new-tag>`)
   and commit that change to this repo — keeps source-of-truth in sync with what's actually deployed
   (this sweep's whole reason for existing was source/live drift; don't recreate that problem here).
3. **Pull + recreate** (Portainer only — every other stack keeps running, this doesn't touch them):
   ```sh
   cd /volume1/docker/portainer
   docker compose pull
   docker compose up -d
   ```
   `restart: unless-stopped` + the bind-mounted `./data` means this recreates only the Portainer
   container itself; the Docker socket mount means it can still see and manage every other running
   container/stack throughout — nothing else needs to be touched or restarted.
4. **Verify:**
   - UI reachable at `https://<nas-ip>:9443`, login works, update banner/version number reflects the
     new tag.
   - Every existing stack still shows as running in the Stacks list (spot-check piwigo, the 4
     hosting mirrors, media-automation) — Portainer re-discovers running containers from the Docker
     daemon on start, it doesn't need to "redeploy" them.
   - Smoke-test the curated catalog (App Templates still loads/lists the templates) — the thing
     most likely to break on an API/template-schema change (see the version-jump note above).
   - **The `app/` FastAPI panel is NOT DEPLOYED** (checked 2026-09-21: no `/volume1/docker/nas-web-cpanel`
     directory, no such container — it is still the "optional thin panel, built incrementally"
     described in CONTEXT.md). Earlier revisions of this runbook listed it as a smoke test, which
     sent a reader hunting for a UI that does not exist. Re-add it here **only once it is actually
     deployed**.
5. **Rollback if anything's wrong:** revert the image tag in `compose.yaml` to the **previous**
   pinned version (see the update-history line at the top — as of 2026-09-21 that is `2.39.6`),
   `docker compose up -d` again. The old version reads the same bind-mounted `data/` directory —
   Portainer's own internal DB migrations are the main rollback risk (a newer version may have
   migrated the DB schema forward in a way the old binary can't read). If `docker compose up -d`
   with the old tag doesn't come up clean, restore the tarball from step 1 over `data/` before
   retrying (stop the container first, extract, restart).

## What NOT to do

- Don't delete or recreate the `data/` bind mount — that's the entire Portainer config/state
  (users, endpoints, stack definitions, the catalog config).
- Don't update any *other* stack's image tags in the same pass "while you're in there" — one change
  at a time, so a problem is attributable.
- Don't skip the pre-update backup because "it's just a bind mount, it's fine" — the backup is what
  makes the rollback path in step 5 actually work if a DB migration goes wrong.

**Performing this runbook = Block 9 territory (Nick's call), listed in the post-renumber sweep's
final HALT report.**

---

## Run log — 2026-09-21: 2.39.6 -> 2.45.1 LTS

Performed by Nick over WireGuard from the MacBook (away from home); CC verified via the API from
NLMacMiniM1. Target chosen: **2.45.1 LTS** (over the lower-risk 2.39.8) for the SSRF hardening,
accepting the 6-minor jump because the release notes declare no breaking changes.

Pre-flight facts confirmed before touching anything:
- Repo copy and the live `/volume1/docker/portainer/compose.yaml` were **byte-identical**
  (md5 `4d8cc93010bab0220149195a6f8e3be8`) — no source/live drift to reconcile first.
- Version was already **pinned** (not `:latest`), so the bump is an explicit, reviewable edit.
- Data is a **bind mount** (`./data` -> `/volume1/docker/portainer/data`, 1.1 MB, `portainer.db`),
  so a plain `tar` of the directory is a complete backup.

**Reminder of what this update does NOT do:** it does not touch, restart or affect any other stack
or container. Portainer is a management UI holding `docker.sock`; the Docker daemon runs the
containers and keeps running them while Portainer is down. On restart Portainer re-discovers
running containers from the daemon — it does not need to redeploy anything. The blast radius of a
bad Portainer update is *Portainer's own DB*, which is why step 1 (backup) is the load-bearing step.

**Post-update result (2.45.1 verified):** Portainer reports `2.45.1` and — critically — the
**InstanceID is unchanged** (`c52baaf4-...`), meaning 2.45.1 migrated the existing DB rather than
initialising a fresh one. Every other service kept serving throughout (prowlarr/qbittorrent/sonarr/
radarr/lidarr/piwigo/mealie + both WordPress mirrors via their FQDNs), confirming that a Portainer
update does not touch other stacks. **Curated catalog: PASSED** — App Templates lists the catalog
(AdGuard Home, Dockge, Gitea, Homarr, Homepage, Immich, InvoiceNinja v5, IT-Tools, Jellyfin,
Nextcloud+MariaDB, ...). **FastAPI panel: N/A — not deployed** (see step 4).

**Also confirmed in the Stacks view:** `qbittorrent-nordvpn` shows all 7 containers (gluetun healthy,
flaresolverr/lidarr/prowlarr/qbittorrent/radarr/sonarr running) — including **prowlarr**, which had
been recreated that day with `docker run` + replicated compose labels. The labels worked: Portainer
groups it in the stack rather than orphaning it. To return it to genuine Compose management, a FULL
stack redeploy is required (that resolves `service:gluetun` correctly because gluetun is in the
operation set) — but that recreates gluetun and therefore briefly drops the whole stack, so treat it
as maintenance-window work, not routine.

---

## Run log — 2026-11-11: 2.45.1 -> 2.45.3 LTS

Nick ran steps 1 and 3 in Terminal on the NAS (`sudo`, with the docker binary at `/usr/local/bin/docker`). The Helm
session on NLMacMiniM1 staged step 2 (`dacaa73`). The NAS SFTP path mapping refused `scp` to `/volume1/...`, so the
file went over as `ssh … 'cat > /volume1/docker/portainer/compose.yaml'`; repo and live md5 matched (`a12af8d6…`)
before the pull.

- **Release check:** 2.45.3 (21 Oct) is the current LTS. Its one breaking change: it no longer trusts
  eMudhra/emSign certificates (CVE-2026-111943). We use no OAuth/LDAP, and we pull from Docker Hub, lscr.io and
  ghcr.io, so there was no impact. 2.45.2 has no deprecations.
- **Backup:** `/volume1/docker/portainer-data-backup-20261111-2233.tar.gz` (222K). A second copy, `-2234`, came
  from a repeat after a mistyped sudo password.
- **Result:** `/api/status` reports `2.45.3`. The **InstanceID is unchanged** (`c52baaf4-…`), so the DB was migrated
  and not re-initialised. All FQDNs served afterwards: the five *arr/qbit, portainer, piwigo, invoices, spiritof,
  mealie, kitchen and hub.
- **Not caused by the update:** `nickleigh-info` (:8081) and `gbr` (:8082) gave intermittent 503s and no-replies
  for a few minutes at ~22:36. They were stable at 200 by ~22:40. This overlapped a nickleigh-info-local session
  starting the T20 InvoiceNinja work, so that session checks it.

