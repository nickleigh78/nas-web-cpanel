# Hostnames — reverse proxy (E7.3)  ▶ NICK applies

> **CORRECTION (2026-07-27, from the piwigo-local go-live): NPM does NOT work as the central
> 80/443 proxy on this DS1522+.** DSM's own nginx already owns ports 80/443 (it serves `hub` via
> Web Station), and a container can't bind them — so NPM could only run on alternate ports (app
> URLs carry a port) or awkwardly chain behind DSM. **Use DSM's built-in reverse proxy instead**
> (Control Panel → Login Portal → Advanced → Reverse Proxy) — it's already the central hostname
> router here. Pattern per app: (1) add the alias to `asset-register/inventory/dns_aliases.csv`
> and apply via `opnsense-config playbooks/08_dns_host_overrides.yml`; (2) DSM Reverse Proxy rule
> `<app>.spikechilli.nickleigh.info` HTTP:80 → the container's **LAN-IP:port** (not localhost —
> the mirror stacks bind the LAN interface only). Verified working for `piwigo` → `10.0.10.10:8085`.
> The NPM-based steps below are retained for reference only.

Give every app a name instead of a port, via **Nginx Proxy Manager (NPM)**.

## The domain — ONE variable
```
DOMAIN = spikechilli.nickleigh.info
```
Every app is **`<app>.$DOMAIN`**, matching the existing `hub.spikechilli.nickleigh.info`.
**Note:** this **FQDN supersedes the old `.spikechilli.local` mDNS names** as part of the
VLAN rollout — use the FQDN everywhere going forward. To move the whole scheme later,
change only this one value (and the DNS + NPM host list below).

## Map (proxy host → forward target)
| Hostname | Forwards to | Scheme |
|---|---|---|
| `portainer.$DOMAIN` | `<nas-ip>:9443` | **https** (Portainer is TLS) |
| `panel.$DOMAIN` | `<nas-ip>:8099` | http (custom App Panel — set PANEL_PASS) |
| `npm.$DOMAIN` | `<nas-ip>:8181` | http (NPM admin) |
| `wp-main.$DOMAIN` | `<nas-ip>:8081` | http |
| `gbr.$DOMAIN` | `<nas-ip>:8082` | http |
| `invoices.$DOMAIN` | `<nas-ip>:8083` | http |
| `spiritof.$DOMAIN` | `<nas-ip>:8084` | http |
| `piwigo.$DOMAIN` | `<nas-ip>:8085` | http (5th mirror app) |

## Steps  ▶ NICK
1. Deploy NPM: copy `compose.yaml` to `/volume1/docker/npm/`, Container Manager →
   Project → Create → Up. Admin UI at `http://<nas-ip>:8181` (default login
   `admin@example.com` / `changeme` — change it immediately).
2. **DNS:** point `*.spikechilli.nickleigh.info` (or each host above) at the NAS IP —
   add to the OPNsense Unbound host-overrides (same place `hub.` lives). A wildcard
   is simplest; per-host works too.
3. For each row: NPM → **Hosts → Proxy Hosts → Add** → Domain = the hostname,
   Forward Hostname/IP = `<nas-ip>`, Forward Port = the port, Scheme as above.
   Enable **Block Common Exploits** + **Websockets**. TLS: use an internal/self-signed
   or a wildcard cert (LAN-only; Let's Encrypt needs DNS-01 for a private name).
4. Portainer row: set scheme **https** and enable "Ignore invalid SSL" (its cert is self-signed).

After this, browse `https://piwigo.spikechilli.nickleigh.info` etc. — no ports.
