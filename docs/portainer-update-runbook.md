# Portainer update runbook — guidance only, NOT for autonomous execution

**Status:** authored 2026-08-16 (post-renumber sweep, Block E). **Performing this update is a
Nick-only action** — Portainer manages every stack on the NAS (piwigo, the 4 hosting mirrors, the
media-automation *arr stack), so a botched update has portfolio-wide blast radius. This doc is
guidance to make that update safe and fast when Nick chooses to do it; nothing here should be run
autonomously.

## Current → target

- **Current:** Portainer CE `2.21.5`, pinned in `deploy/portainer/compose.yaml`, deployed at
  `/volume1/docker/portainer/` on the DS1522+.
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
   - Smoke-test the curated catalog (App Templates still loads/lists the 13 templates) and the
     custom FastAPI panel (list/logs/start-stop still function) — these are the two things most
     likely to break on an API/schema change (see the version-jump note above).
5. **Rollback if anything's wrong:** revert the image tag in `compose.yaml` to `2.21.5`,
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
