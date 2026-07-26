# RUNBOOK — nothing → a working app manager on the DS1522+

One pass from an empty NAS to a working app/package manager (Portainer + your curated
catalog), plus optional extras. **Live-box steps are yours to run** (marked ▶ NICK); this
repo only authors the files. Cross-refs: [`deploy/portainer/README.md`](../deploy/portainer/README.md) ·
[`catalog/README.md`](../catalog/README.md) · [`app/README.md`](../app/README.md) ·
[`deploy/ALTERNATIVES.md`](../deploy/ALTERNATIVES.md).

## 1. Deploy the engine — Portainer  ▶ NICK
1. File Station → create `/volume1/docker/portainer/` + a `data/` subfolder.
2. Copy `deploy/portainer/compose.yaml` in. **The docker socket must be read-write**
   (`/var/run/docker.sock:/var/run/docker.sock`, no `:ro`) or Portainer can't deploy anything.
3. Container Manager → **Project → Create** → path `/volume1/docker/portainer/` → Build/Up.
   - ⚠️ If DSM offers a **"Web Station web portal"**, leave it **unchecked** — it proxies as
     HTTP and 404s (Portainer serves its own HTTPS on 9443).
4. Browse **`https://<nas-ip>:9443`**, create the admin user within ~2 min, → "Get Started" →
   manage the **local** environment. Container management now works (the "cPanel" half).

## 2. Load your catalog — the one-click installer (Softaculous half)  ▶ NICK
Portainer → **Settings → App Templates** → URL:
```
https://raw.githubusercontent.com/nickleigh78/nas-web-cpanel/main/catalog/templates.json
```
(The repo is public + sanitized — no account identifiers.) **App Templates** now lists your
apps, including the **Spike-Chilli Mirror** category.

## 3. Smoke test — install a common app  ▶ NICK
App Templates → **Uptime Kuma** → Deploy (default port 3001). Wait for it to show **running** in
Containers, browse `http://<nas-ip>:3001`. If that works, the installer path is proven.

## 4. Bring up a mirror app (the site rebuild)  ▶ NICK
The 5 mirror apps (WP-main, WP-GBR, InvoiceNinja, spiritof, Piwigo) deploy from the
**Spike-Chilli Mirror** catalog category. Each template brings up an **empty stack shell**;
you then **restore the captured data**:
1. Deploy the stack from App Templates (fill the pre-set env — DB name/port).
2. Restore per the app's runbook in **`../nickleigh-info-local/stacks/<app>/README.md`**
   (seed files from the Track C capture, import the DB dump, URL-rewrite). Piwigo restore =
   `../piwigo-local` PLAN "RESTORE INTEGRATION" (17 GB gallery + `ciqndvoj_piwi514` dump).
   Hard rules: WordPress → `wp search-replace` (serialized-safe); InvoiceNinja → carry the
   captured `.env` APP_KEY verbatim + `MAIL_MAILER=log`; spiritof → PHP 5.6 vs 7.4 check.

## 5. Optional — the custom panel  ▶ NICK
A branded glance-and-act dashboard over your stacks (grouped by compose project, CPU/mem,
logs, Docker Hub search). Deploy `app/` (`/volume1/docker/app-panel/`, Container Manager
Project). **Set `PANEL_PASS`** in its env to enable auth before it's reachable. Browse
`http://<nas-ip>:8099`. See `app/README.md`.

## 6. Optional — hostnames via reverse proxy  ▶ NICK
Give every app `<app>.spikechilli.nickleigh.info` (FQDN) instead of a port. Deploy the NPM
stack and follow **`deploy/reverse-proxy/HOSTNAMES.md`** (authored in E7.3). Note: the FQDN
supersedes `.spikechilli.local` mDNS in the VLAN rollout.

## Order of operations (quick)
Portainer (1) → catalog (2) → smoke test (3) → mirror apps + restore (4) → panel (5) →
reverse proxy (6). Steps 1–3 give a working manager in ~15 min; 4–6 are the rebuild + polish.

## If you'd rather an all-in-one
`deploy/ALTERNATIVES.md` — **1Panel** (richer built-in store) or CasaOS, evaluated as
drop-in-later engines; the catalog concept carries over.
