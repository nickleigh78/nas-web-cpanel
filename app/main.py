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

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

try:
    import docker
    _client = docker.from_env()
except Exception as exc:  # noqa: BLE001 - surface the reason in the UI instead of crashing
    _client = None
    _client_error = str(exc)
else:
    _client_error = None

app = FastAPI(title="Spike-Chilli App Panel", version="0.1.0")

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>Spike-Chilli App Panel</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body{{font-family:system-ui,sans-serif;margin:2rem;background:#0f1115;color:#e6e6e6}}
 h1{{font-size:1.4rem}} a{{color:#7aa2f7}}
 table{{border-collapse:collapse;width:100%;margin-top:1rem}}
 th,td{{text-align:left;padding:.5rem .75rem;border-bottom:1px solid #262a33}}
 .up{{color:#9ece6a}} .down{{color:#f7768e}}
 form{{display:inline}} button{{background:#262a33;color:#e6e6e6;border:1px solid #3b4048;
 border-radius:6px;padding:.25rem .6rem;cursor:pointer;margin-right:.25rem}}
 button:hover{{background:#3b4048}} .muted{{color:#8b93a1;font-size:.85rem}}
</style></head><body>
<h1>🌶️ Spike-Chilli App Panel <span class="muted">v0.1 — MVP</span></h1>
{body}
<p class="muted">Install new apps from the curated catalog in Portainer → App Templates.</p>
</body></html>"""


def _rows() -> str:
    if _client is None:
        return f'<p class="down">Docker not reachable: {html.escape(_client_error or "unknown")}.' \
               '<br>Mount <code>/var/run/docker.sock</code> into this container.</p>'
    out = ['<table><tr><th>Name</th><th>Image</th><th>State</th><th>Actions</th></tr>']
    for c in sorted(_client.containers.list(all=True), key=lambda x: x.name):
        image = c.image.tags[0] if c.image.tags else c.image.short_id
        cls = "up" if c.status == "running" else "down"
        out.append(
            f'<tr><td>{html.escape(c.name)}</td>'
            f'<td class="muted">{html.escape(image)}</td>'
            f'<td class="{cls}">{c.status}</td>'
            f'<td>'
            f'<form method="post" action="/act/{c.id}/start"><button>start</button></form>'
            f'<form method="post" action="/act/{c.id}/stop"><button>stop</button></form>'
            f'<form method="post" action="/act/{c.id}/restart"><button>restart</button></form>'
            f'<a href="/logs/{c.id}"><button type="button">logs</button></a>'
            f'</td></tr>'
        )
    out.append("</table>")
    return "".join(out)


@app.get("/", response_class=HTMLResponse)
def dashboard(_: Request) -> str:
    return PAGE.format(body=_rows())


@app.post("/act/{cid}/{action}")
def act(cid: str, action: str) -> RedirectResponse:
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
def logs(cid: str, tail: int = 200) -> str:
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


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": _client is not None, "error": _client_error}
