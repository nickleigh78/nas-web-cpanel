# nas-web-cpanel — autonomous progress ledger

Resume: read top-to-bottom. Autonomous build via scheduled wakeups; commit each slice.

## 2026-07-24 — session 0 (project creation)
- **Research done** (docs/RESEARCH.md): surveyed 1Panel, Portainer, CasaOS, Cosmos,
  Dockge, CapRover, Cloudron, aaPanel/VestaCP. **Decision: adopt Portainer CE + build
  a curated catalog** (not a from-scratch clone). Transparent so Nick can redirect.
- **Scaffolded**: CLAUDE/CONTEXT/README/PLAN/.gitignore.
- **E1 Engine**: `deploy/portainer/` compose + DSM runbook (bring-up = Nick's HALT).
- **E2 Catalog**: `catalog/templates.json` (8 apps: WordPress+DB, Nextcloud+DB,
  Uptime-Kuma, Vaultwarden, NPM, Dockge, IT-Tools, Homepage) + `catalog/stacks/*.yml`.
- **E4 Panel MVP seed**: `app/` FastAPI dashboard (list + start/stop/restart) +
  Dockerfile + compose.
- **Alternatives**: `deploy/ALTERNATIVES.md` (1Panel/CasaOS/Cosmos).
- **GitHub repo:** https://github.com/nickleigh78/nas-web-cpanel (private).
- **Agile board (Project #6):** https://github.com/users/nickleigh78/projects/6 —
  12 items across E1–E6 (4 already [DONE] this session).

## 2026-07-24 — tick 1 (E3 done)
- Captures pulse: Track C running (1.0 GB), monitor watching, R1 held, no completion
  signal yet — all nominal, no coordination action needed.
- **E3 DONE**: added 5 "Spike-Chilli Mirror" catalog entries (wp-main, wp-gbr,
  invoiceninja, spiritof, piwigo) + 3 new stackfiles. Catalog now 13 templates.
  Committed 703c539, board item marked DONE.
- Next tick: E4 panel — logs view (then basic auth, install-from-catalog).

## 2026-07-24 — tick 2 (E4 logs view)
- Captures pulse: Track C running (1.1 GB, slow/latency-bound), monitor watching,
  R1 held, no completion signal — nominal, no action.
- **E4 logs view DONE**: `/logs/{cid}` page (tail + timestamps, refresh) + per-row
  logs button. Committed 68ed5f0, board updated. Stack grouping deferred (new slice).
- Next tick: E4 basic auth.

## 2026-07-24 — tick 3: LOOP PAUSED (weekly usage ~95%)
- Nick flagged ~95% weekly usage; the autonomous wakeups had stopped firing (limit
  pauses scheduled execution). **Loop stopped** to preserve remaining budget — Nick
  decides when to spend more. Resume point below.
- Captures pulse: Track C running (1.3 GB), monitor watching, R1 held, no completion
  signal — nominal.
- **IMPORTANT:** the captures + trackc-monitor.sh are independent OS processes — they
  keep running and consume ZERO Claude credits. Track C → "restart R1" coordination
  still works with the loop off.
- **Resume point:** next build slice = E4 basic auth, then E4 install-from-catalog,
  E4 stack grouping, E5 search, E6 runbook. To resume the loop, re-run the tick prompt
  and re-arm ScheduleWakeup. Done so far: E1 files, E2 catalog, E3 mirror entries,
  E4 logs view.

## 2026-07-24 — WATCHDOG MODE (dev paused until weekly reset Sun 2026-07-26 06:00 AEST)
- Repo renamed nas-app-panel → **nas-web-cpanel** (GitHub, dir, board #6, portfolio
  map, STATUS, mirror PLAN — all refs updated).
- Nick at ~95% weekly usage; reset Sun 2026-07-26 ~06:00 AEST. **All dev PAUSED.**
  Priority = ensure Track C capture completes + the R1/Sonnet handoff fires, on
  minimal budget.
- Loop switched to a cheap watchdog: each tick runs `~/SiteCapture/watchdog-tick.sh`
  (keeps trackc-monitor.sh alive; the monitor itself restarts Track C + signals
  completion at ZERO Claude cost — capture finishes even if my budget runs out).
  Tick = 1 bash + 1 reschedule (3600s). Stops on VERDICT=COMPLETE.
- Track C at 3.4 GB and climbing (into the big app trees).
- **Resume dev after the reset:** next dev slice = E4 basic auth → install-from-catalog
  → stack grouping → E5 search → E6 runbook. Done: E1, E2, E3, E4 logs view.

## 2026-07-26 — Portainer LIVE + catalog loaded (post-reset, dev resumed)
- **Portainer deployed on the DS1522+** via Container Manager (compose staged by CC
  over SSH at /volume1/docker/portainer/). Fixed: docker.sock mounted read-write (the
  `:ro` would have blocked all installs); resolved the DSM "Web Station web portal"
  auto-enable that was causing 404s (disable it — Portainer serves its own UI on 9443).
  Admin user created. Reachable at https://<nas>:9443.
- **Repo made PUBLIC** so the App Templates URL works, then **sanitized**: replaced the
  cPanel account DB names with generic placeholders and squashed history (the `ciqndvoj`
  username is not in any public commit). Nick set the App Templates URL to the raw
  catalog. HALT-1 (first live-box action) is now CLEARED — Portainer is running.
- **E7 Portainer setup & branding backlog** scoped (PLAN §7b) + added to board #6.
- Dev loop resumed post-reset (30-min cadence): E4 basic auth next.
- Capture side: Track C effectively complete (6.1 GB); R1 gallery resumed + self-
  completing via r1-monitor (see piwigo-local/R1-PROGRESS.md).

## HALT ledger
- **HALT-1 (pending):** before Nick runs anything on the DS1522+ (deploy Portainer /
  the panel). Nothing on the box yet — repo + docs only. First live action is Nick's,
  per the deploy runbook.

## Next slices (per wakeup) — E3, E4+, E5, E6
- E3: add the 4 mirror stacks + Piwigo to the catalog (wired to their compose).
- E4: panel — stack grouping, logs view, "install from catalog", basic auth.
- E5: search/discovery (Docker Hub / curated index) to add packages.
- E6: single zero→working runbook; verify the catalog loads in Portainer.
- Ongoing: keep watching the mirror captures (separate work) and coordinate R1.

## Open questions for Nick (non-blocking)
- Repo visibility: **private** by default. For the simplest catalog load, either make
  it public or host `catalog/` on a NAS web path (deploy runbook Option A/B).
- Prefer the all-in-one **1Panel** instead of Portainer+catalog? Redirect anytime.
