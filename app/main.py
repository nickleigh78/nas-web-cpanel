"""
Spike-Chilli App Panel — MVP dashboard (E4 seed).

A thin, single-file FastAPI app that lists Docker containers and can
start/stop/restart them. Talks to the Docker Engine via the mounted socket
(/var/run/docker.sock). The heavy app-store/install work is delegated to Portainer
+ the curated catalog (see ../catalog/); this panel is the unified read/act view.

Run locally against a Docker host, or as a container on the NAS (see compose.yaml).
Intentionally dependency-light and incremental — grown over the autonomous wakeups.
"""
from __future__ import annotations

import html
import json as _json
import os
import secrets as _secrets
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

try:
    import docker
    _client = docker.from_env()
except Exception as exc:  # noqa: BLE001 - surface the reason in the UI instead of crashing
    _client = None
    _client_error = str(exc)
else:
    _client_error = None

app = FastAPI(title="Spike-Chilli App Panel", version="0.1.0")

# --- Basic auth (E4). Enforced only when PANEL_PASS is set; LAN-only dev otherwise. ---
_PANEL_USER = os.environ.get("PANEL_USER", "admin")
_PANEL_PASS = os.environ.get("PANEL_PASS")
_basic = HTTPBasic(auto_error=False)


def require_auth(credentials: HTTPBasicCredentials | None = Depends(_basic)) -> None:
    """No-op until PANEL_PASS is set — set it before exposing the panel."""
    if not _PANEL_PASS:
        return
    ok = (
        credentials is not None
        and _secrets.compare_digest(credentials.username, _PANEL_USER)
        and _secrets.compare_digest(credentials.password, _PANEL_PASS)
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Spike-Chilli App Panel</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>🌶️</text></svg>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 :root{{--bg:#0b1119;--panel:#111b27;--panel2:#0d151f;--border:#22303f;--text:#e6edf3;
  --muted:#8b98a8;--accent:#26c6de;--up:#3fb950;--warn:#d29922;--down:#f85149;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
 *{{box-sizing:border-box}} a{{color:var(--accent)}}
 body{{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.5}}
 .wrap{{max-width:940px;margin:0 auto;padding:1.5rem 1.1rem}}
 header.top{{display:flex;align-items:baseline;gap:.6rem;margin-bottom:1.2rem;
  border-bottom:1px solid var(--border);padding-bottom:.8rem}}
 header.top h1{{font-size:1.2rem;margin:0}}
 .v{{color:var(--muted);font-size:.78rem;font-family:var(--mono)}}
 .top form.search{{margin-left:auto}}
 .top input{{font:inherit;font-size:.8rem;background:var(--panel2);color:var(--text);
  border:1px solid var(--border);border-radius:7px;padding:.35rem .6rem;min-width:180px}}
 .top input:focus{{outline:2px solid var(--accent);border-color:var(--accent)}}
 .live{{font-family:var(--mono);font-size:.72rem;color:var(--up);
  animation:pulse 2s ease-in-out infinite;text-shadow:0 0 6px var(--up)}}
 @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
 .stack-head h2{{text-shadow:0 0 7px rgba(38,198,222,.35)}}
 button:hover{{box-shadow:0 0 8px rgba(38,198,222,.35)}}
 .tile:hover{{box-shadow:0 0 12px rgba(38,198,222,.14)}}
 .pill.up{{box-shadow:0 0 8px rgba(63,185,80,.18)}}
 @media(prefers-reduced-motion:reduce){{.live{{animation:none}}}}
 .stack{{background:var(--panel);border:1px solid var(--border);border-radius:11px;
  margin:0 0 1rem;overflow:hidden}}
 .stack-head{{display:flex;align-items:center;justify-content:space-between;gap:.6rem;
  padding:.7rem .9rem;background:var(--panel2);border-bottom:1px solid var(--border)}}
 .stack-head h2{{font-size:.92rem;margin:0;font-family:var(--mono);color:var(--accent)}}
 .pill{{font-size:.72rem;font-family:var(--mono);padding:.18rem .55rem;border-radius:999px;
  border:1px solid var(--border)}}
 .pill.up{{color:var(--up)}} .pill.warn{{color:var(--warn)}} .pill.down{{color:var(--down)}}
 .tiles{{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin-bottom:1rem}}
 .tile{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;text-align:center}}
 .tn{{font-size:1.4rem;font-weight:700;font-family:var(--mono)}} .tn.up{{color:var(--up)}} .tn.down{{color:var(--down)}}
 .tl{{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
 td.m{{white-space:nowrap;font-size:.74rem}} .bar{{display:inline-block;width:48px;height:7px;background:var(--panel2);
  border-radius:4px;overflow:hidden;vertical-align:middle;margin-right:.3rem}}
 .bar .fill{{display:block;height:100%;background:var(--accent)}} .bar.mid .fill{{background:var(--warn)}} .bar.hi .fill{{background:var(--down)}}
 @media(max-width:640px){{.tiles{{grid-template-columns:repeat(2,1fr)}}}}
 table{{width:100%;border-collapse:collapse}}
 td{{padding:.5rem .9rem;border-bottom:1px solid var(--panel2);font-size:.85rem;vertical-align:middle}}
 tr:last-child td{{border-bottom:none}}
 td.svc{{font-family:var(--mono)}}
 td.img{{font-family:var(--mono);font-size:.76rem;color:var(--muted)}}
 .state{{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--mono);font-size:.78rem}}
 .state::before{{content:"";width:8px;height:8px;border-radius:50%}}
 .state.run{{color:var(--up)}}.state.run::before{{background:var(--up)}}
 .state.stop{{color:var(--down)}}.state.stop::before{{background:var(--down)}}
 td.acts{{white-space:nowrap}} .acts form{{display:inline}}
 button{{background:#1b2836;color:var(--text);border:1px solid var(--border);border-radius:6px;
  padding:.24rem .55rem;cursor:pointer;font-size:.76rem;margin-right:.2rem}}
 button:hover{{background:#243546;border-color:var(--accent)}} .acts a button{{color:var(--accent)}}
 .muted{{color:var(--muted)}} .down{{color:var(--down)}}
 footer{{color:var(--muted);font-size:.78rem;margin-top:1.2rem;border-top:1px solid var(--border);
  padding-top:.8rem}}
</style></head><body><div class="wrap">
<header class="top"><h1><a href="/" style="color:inherit;text-decoration:none">🌶️ Spike-Chilli App Panel</a></h1><span class="v">v0.4</span><span class="live">&#9679; live</span><form class="search" method="get" action="/search"><input name="q" placeholder="&#8981; search Docker Hub&#8230;" aria-label="Search Docker Hub"></form></header>
{body}
<footer>Grouped by compose stack. Install new apps from Portainer &rarr; App Templates.</footer>
<script>if(location.pathname==="/"){{setInterval(function(){{if(!document.hidden)location.reload();}},8000);}}</script>
</div></body></html>"""


def _stats_for(c):
    """(cpu_pct, mem_pct, mem_mb) for a running container, or (None, None, None). Best-effort."""
    try:
        s = c.stats(stream=False)
        cpu, pcpu = s["cpu_stats"], s["precpu_stats"]
        cd = cpu["cpu_usage"]["total_usage"] - pcpu["cpu_usage"]["total_usage"]
        sd = cpu.get("system_cpu_usage", 0) - pcpu.get("system_cpu_usage", 0)
        ncpu = cpu.get("online_cpus") or len(cpu["cpu_usage"].get("percpu_usage") or [1])
        cpu_pct = (cd / sd) * ncpu * 100.0 if sd > 0 and cd > 0 else 0.0
        mem = s["memory_stats"]
        usage = mem.get("usage", 0) - (mem.get("stats", {}) or {}).get("inactive_file", 0)
        limit = mem.get("limit", 0) or 1
        return (round(cpu_pct, 1), round(usage / limit * 100.0, 1), round(usage / 1048576))
    except Exception:  # noqa: BLE001
        return (None, None, None)


def _bar(pct, label):
    if pct is None:
        return ""
    p = max(0.0, min(100.0, pct))
    cls = "hi" if p >= 85 else ("mid" if p >= 60 else "")
    return f'<span class="bar {cls}" title="{label} {pct}%"><span class="fill" style="width:{p:.0f}%"></span></span>'


def _groups_html() -> str:
    if _client is None:
        return (f'<p class="down">Docker not reachable: {html.escape(_client_error or "unknown")}.'
                '<br>Mount <code>/var/run/docker.sock</code> into this container.</p>')
    containers = _client.containers.list(all=True)
    if not containers:
        return '<p class="muted">No containers yet. Install apps from Portainer &rarr; App Templates.</p>'
    running_cs = [c for c in containers if c.status == "running"]
    stats: dict[str, tuple] = {}
    try:
        with ThreadPoolExecutor(max_workers=8) as ex:
            for c, r in zip(running_cs, ex.map(_stats_for, running_cs)):
                stats[c.id] = r
    except Exception:  # noqa: BLE001
        pass
    try:
        n_images = len(_client.images.list())
    except Exception:  # noqa: BLE001
        n_images = "?"
    projects = {c.labels.get("com.docker.compose.project") or "· standalone" for c in containers}
    tiles = ('<div class="tiles">'
             f'<div class="tile"><div class="tn">{len(projects)}</div><div class="tl">stacks</div></div>'
             f'<div class="tile"><div class="tn up">{len(running_cs)}</div><div class="tl">running</div></div>'
             f'<div class="tile"><div class="tn down">{len(containers) - len(running_cs)}</div><div class="tl">stopped</div></div>'
             f'<div class="tile"><div class="tn">{n_images}</div><div class="tl">images</div></div></div>')
    groups: dict[str, list] = {}
    for c in containers:
        groups.setdefault(c.labels.get("com.docker.compose.project") or "· standalone", []).append(c)
    out: list[str] = [tiles]
    for proj in sorted(groups):
        members = sorted(groups[proj],
                         key=lambda x: (x.labels.get("com.docker.compose.service") or x.name))
        running = sum(1 for c in members if c.status == "running")
        total = len(members)
        badge = "up" if running == total else ("down" if running == 0 else "warn")
        out.append(f'<section class="stack"><div class="stack-head">'
                   f'<h2>{html.escape(proj)}</h2>'
                   f'<span class="pill {badge}">{running}/{total} up</span></div><table><tbody>')
        for c in members:
            svc = c.labels.get("com.docker.compose.service") or c.name
            image = c.image.tags[0] if c.image.tags else c.image.short_id
            cls = "run" if c.status == "running" else "stop"
            cpu, mem, memmb = stats.get(c.id, (None, None, None))
            if c.status == "running":
                metrics = (f'<td class="m">{_bar(cpu, "CPU")}{cpu if cpu is not None else "&mdash;"}%</td>'
                           f'<td class="m">{_bar(mem, "MEM")}{(str(memmb) + "M") if memmb is not None else "&mdash;"}</td>')
            else:
                metrics = '<td class="m t">&mdash;</td><td class="m t">&mdash;</td>'
            out.append(
                f'<tr><td class="svc">{html.escape(svc)}</td>'
                f'<td class="img">{html.escape(image)}</td>'
                f'<td><span class="state {cls}">{html.escape(c.status)}</span></td>'
                f'{metrics}'
                f'<td class="acts">'
                f'<form method="post" action="/act/{c.id}/start"><button>start</button></form>'
                f'<form method="post" action="/act/{c.id}/stop" onsubmit="return confirm(\'Stop this container?\')"><button>stop</button></form>'
                f'<form method="post" action="/act/{c.id}/restart" onsubmit="return confirm(\'Restart this container?\')"><button>restart</button></form>'
                f'<a href="/logs/{c.id}"><button type="button">logs</button></a>'
                f'</td></tr>')
        out.append('</tbody></table></section>')
    return "".join(out)


@app.get("/", response_class=HTMLResponse)
def dashboard(_: Request, _auth: None = Depends(require_auth)) -> str:
    return PAGE.format(body=_groups_html())


@app.post("/act/{cid}/{action}")
def act(cid: str, action: str, _auth: None = Depends(require_auth)) -> RedirectResponse:
    if _client is not None and action in {"start", "stop", "restart"}:
        try:
            getattr(_client.containers.get(cid), action)()
        except Exception:  # noqa: BLE001 - best-effort; dashboard will show the result
            pass
    return RedirectResponse("/", status_code=303)


LOGS_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>logs · {name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body{{font-family:system-ui,sans-serif;margin:2rem;background:#0f1115;color:#e6e6e6}}
 a{{color:#7aa2f7}} h1{{font-size:1.1rem}}
 pre{{background:#0b0d12;border:1px solid #262a33;border-radius:8px;padding:1rem;
 overflow:auto;max-height:75vh;white-space:pre-wrap;word-break:break-word;font-size:.8rem}}
</style></head><body>
<p><a href="/">&larr; back</a> &nbsp; <a href="/logs/{cid}">&#8635; refresh</a></p>
<h1>logs · {name} <span style="color:#8b93a1">(last {tail} lines)</span></h1>
<pre>{logs}</pre></body></html>"""


@app.get("/logs/{cid}", response_class=HTMLResponse)
def logs(cid: str, tail: int = 200, _auth: None = Depends(require_auth)) -> str:
    if _client is None:
        return PAGE.format(body='<p class="down">Docker not reachable.</p>')
    tail = max(1, min(tail, 2000))
    try:
        c = _client.containers.get(cid)
        raw = c.logs(tail=tail, timestamps=True).decode("utf-8", "replace")
        name = c.name
    except Exception as exc:  # noqa: BLE001
        raw, name = f"error reading logs: {exc}", cid
    return LOGS_PAGE.format(name=html.escape(name), cid=html.escape(cid),
                            tail=tail, logs=html.escape(raw) or "(empty)")


@app.get("/search", response_class=HTMLResponse)
def search(q: str = "", _auth: None = Depends(require_auth)) -> str:
    """Search Docker Hub for images to add to the catalog. Needs outbound internet."""
    q = q.strip()
    if not q:
        return PAGE.format(body='<div class="panel"><h3>Search Docker Hub</h3>'
            '<div class="li muted">Type a query above (e.g. nextcloud, gitea, jellyfin) '
            'to find images to add to your catalog.</div></div>')
    try:
        url = "https://hub.docker.com/v2/search/repositories/?" + urllib.parse.urlencode(
            {"query": q, "page_size": 20})
        req = urllib.request.Request(url, headers={"User-Agent": "spike-chilli-app-panel"})
        with urllib.request.urlopen(req, timeout=8) as r:
            results = _json.loads(r.read().decode("utf-8")).get("results", [])
    except Exception as exc:  # noqa: BLE001
        return PAGE.format(body=f'<div class="panel"><h3>Search · {html.escape(q)}</h3>'
            f'<div class="li down">Docker Hub unreachable: {html.escape(str(exc))} '
            '(the panel container needs outbound internet).</div></div>')
    if not results:
        return PAGE.format(body=f'<div class="panel"><h3>Search · {html.escape(q)}</h3>'
            '<div class="li muted">No results.</div></div>')
    rows = []
    for it in results:
        name = it.get("repo_name") or it.get("name") or ""
        desc = (it.get("short_description") or "")[:120]
        tag = " · official" if it.get("is_official") else (" · verified" if it.get("is_automated") else "")
        rows.append(f'<tr><td class="svc">{html.escape(name)}<span class="t">{tag}</span></td>'
                    f'<td>{html.escape(desc)}</td>'
                    f'<td class="t">&#9733;{it.get("star_count", 0)}</td></tr>')
    body = (f'<div class="panel"><h3>Docker Hub &middot; &ldquo;{html.escape(q)}&rdquo; &middot; {len(results)} results</h3>'
            f'<table><thead><tr><th>Image</th><th>Description</th><th>Stars</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>'
            '<div class="li muted">To add one: put it in <code>catalog/templates.json</code> '
            '(a type:1 container or a type:3 stack), commit, then re-fetch App Templates in Portainer.</div></div>')
    return PAGE.format(body=body)


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": _client is not None, "error": _client_error}
