# Engine alternatives (documented for later)

The engine is deliberately swappable (LD3). If the curated-catalog-on-Portainer
approach ever feels limiting, these are the drop-in-later options — the catalog
concept (curated one-click apps) carries over to each.

## 1Panel — richest built-in store (closest single-tool to cPanel+Softaculous)
- Open-source Docker-native control panel: websites, DBs, containers, backups, and a
  **built-in App Store (165+ apps)**. Conceptually the nearest match to what Nick
  described in one tool.
- Caveat: designed to manage a Linux host; a container-on-DSM install is **less
  proven** than Portainer's. Evaluate before committing (spin up in a VM/Container
  Manager, confirm socket + app-store behaviour on DSM 7.2).
- https://www.opensourcealternatives.to/item/1panel

## CasaOS — best consumer app-store UX
- Friendly home-server overlay with a polished one-click app store + file manager.
- Caveat: wants to own more of the host than a plain container; fine for a dedicated
  box, more intrusive on a NAS already running DSM.

## Cosmos — app store + security/reverse-proxy/SSO
- App store plus automatic HTTPS, SSO/2FA in front of any app. Good if per-app auth
  + public exposure become the pain point (not a current goal — LAN-only).

## Why Portainer was chosen now
Most-proven **containerised** install on DSM 7.2, strong management, and a **custom
App Templates URL** so the one-click catalog is fully ours to curate — lowest risk to
"working in 48h" without taking over the NAS. See ../docs/RESEARCH.md §4.
