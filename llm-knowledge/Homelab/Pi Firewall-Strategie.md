---
type: strategie
tags: [homelab, raspberry-pi, firewall, sicherheit, docker]
status: lebend
updated: 2026-11-27
---

# Firewall-Strategie für den Pi

Grundsatz: **Nur die Ports öffnen, die offen sein müssen.** Jeder Dienst, der nach außen erreichbar ist, muss bewusst eingetragen sein. Nichts wird „mal eben für Debugging“ geöffnet und dann vergessen.

## Ist-Stand (2026-11-27, Befund)

- Auf dem Pi konnte ich keine aktive Firewall bestätigen. `ufw` und `nft`/`iptables` sind ohne Passwort nicht lesbar. Das muss einmal lokal geprüft werden: `sudo ufw status verbose`.
- Viele Dienste lauschen auf **allen Interfaces** (`0.0.0.0` und `[::]`):
  - 22 SSH, 53 und 853 AdGuard, 80 und 443, 111 rpcbind, 3000, 3552, 8000, 9443 Portainer, 19999 netdata, 61208 glances, 5900 VNC
  - UDP 5353 (mDNS), UDP 51671 und 35788 (unbekannt)
- Docker-Container, die Ports veröffentlichen, umgehen `ufw`. Das ist der häufigste Fehler bei Heimservern.
- Am Router (FRITZ!Box) ist nicht dokumentiert, ob Portfreigaben oder UPnP aktiv sind.

Vor allem diese Punkte sind kritisch: VNC (5900) und rpcbind (111) brauchen zur Zeit niemand, netdata, glances und Portainer sind Verwaltungsoberflächen.

### IPv6 (wichtig)
- Der Pi hat eine **öffentliche IPv6-Adresse** (`2001:9e8:…`), die auf `eth0` liegt. IPv6 hat kein NAT. Der einzige Schutz ist dann die Firewall der FRITZ!Box, und die ist nicht geprüft.
- Alle Dienste lauschen auf `[::]`, also auch auf IPv6.
- `ufw` muss IPv6 ebenfalls abdecken (`IPV6=yes` in `/etc/default/ufw`). Die Regeln gelten sonst nur für IPv4.
- Test: Von außerhalb des Heimnetzes (Handy im Mobilfunk, WLAN aus) die IPv6-Adresse auf offene Ports prüfen, z. B. mit `nmap -6` oder einem Online-Portscan.

## Strategie

### 1. Standard: alles zu, Ausnahmen explizit
- Eingehend: Standard **deny**.
- Ausgehend: Standard allow (Updates, Let's Encrypt, Backups brauchen das).
- Jede Freigabe hat einen Eintrag im Port-Register (unten), mit Zweck und Begründung.

### 2. Nur das öffentliche Minimum nach außen
- Das Internet sieht höchstens **einen** Port: 443 (Traefik). Für Let's Encrypt brauchst du dank DNS-01 **keinen** Port 80 mehr.
- Standardmäßig ist **kein** Dienst aus dem Internet erreichbar. Zugriff von unterwegs läuft über WireGuard (FRITZ!Box).
- Wenn 443 nicht öffentlich sein muss, bleibt auch das zu. Dann ist der Pi nur über WireGuard erreichbar.

### 3. Interne Dienste nur im Docker-Netz
- Datenbanken (Postgres, Redis/Valkey) bekommen **kein** `ports:`. Sie sind nur für ihren Stack erreichbar.
- Web-Dienste hinter Traefik nutzen `expose:` oder nur Labels, nicht `ports:`. Der Zugriff läuft über Traefik.
- Ausnahme: AdGuard braucht Port 53 für das Heimnetz. Das ist ein bewusst geöffneter Port, nur LAN.

### 4. Docker und die Firewall
Docker schreibt eigene iptables-Regeln und umgeht damit `ufw`. Ein `ports: "8080:8080"` ist also auch dann offen, wenn `ufw` es verbietet.

Vorgehen:
- **Ports nur an eine Adresse binden:** `ports: "127.0.0.1:8080:8080"` oder bei LAN-Diensten `"192.168.178.52:8080:8080"`. Dann ist der Dienst nur lokal erreichbar.
- **Regeln in der Kette `DOCKER-USER`** setzen. Diese Kette wird vor Docker-Regeln ausgewertet. Sie ist der richtige Ort für Filter auf veröffentlichte Ports.
- Alternative: Helfer wie `ufw-docker` ergänzen `ufw` um passende Regeln. Vorher prüfen, ob das zur Docker-Version passt.
- Ergebnis prüfen: Nach jeder Änderung von außen und innen testen, nicht nur `ufw status` lesen.

### 5. Dienste mit Verwaltungsoberfläche
- Portainer, AdGuard-UI, netdata, glances: **nicht** direkt veröffentlichen. Nur über Traefik mit Zugriffsbeschränkung (IP-Allowlist, Basic Auth oder Forward Auth) oder nur über WireGuard.
- VNC (5900): abschalten, wenn nicht gebraucht. Falls nötig, nur über WireGuard.

### 6. Dienste ohne Nutzen abschalten
- rpcbind (111) und NFS: aktuell inaktiv, rpcbind kann deaktiviert werden.
- Avahi/mDNS (5353): nur nötig, wenn Dienste per `.local` gefunden werden. Sonst abschalten.
- Unbekannte Ports (51671, 35788 UDP): herausfinden, dann entscheiden.

### 7. Router (FRITZ!Box)
- **UPnP ausschalten**. Sonst können Geräte selbst Portfreigaben anlegen.
- Keine Portfreigaben für den Pi anlegen. Ausnahme ist nur WireGuard, und auch das bewusst.
- Im Router prüfen, welche Freigaben existieren: Heimnetz → Freigaben.

### 8. Kontrolle gegen das „Vergessen“
- **Port-Register:** Jeder veröffentlichte Port steht in der Tabelle unten. Neue Ports nur mit Eintrag.
- **Regelmäßige Prüfung:** Monatlich `ss -tulpn` auf dem Pi ausführen und mit dem Register vergleichen.
- **Automatische Warnung:** Uptime Kuma kann einen Port-Check für Ports auf dem Pi machen. Wenn ein unbekannter Port auftaucht, fällt das schnell auf. Für einen Check auf unbekannte Ports reicht ein Nmap-Scan im Heimnetz einmal im Monat.
- **Von außen testen:** Einmal im Quartal Handy im Mobilfunknetz (WLAN aus) oder ein Online-Portscan auf deine öffentliche IP. Das zeigt, was wirklich erreichbar ist.
- **Compose-Prüfung vor Änderungen:** Vor jedem `docker compose up` in den Compose-Dateien nach `ports:` suchen. Jedes Ergebnis ohne Register-Eintrag ist ein Fehler.

## Port-Register

Stand: 2026-11-27. Ziel: alle Einträge auf „geschlossen“ oder „nur LAN/WireGuard“.

| Port | Dienst | Ziel | Maßnahme |
|---|---|---|---|
| 22/tcp | SSH | nur LAN und WireGuard | ufw-Regel, Schlüssel statt Passwort |
| 53/tcp+udp | AdGuard DNS | nur LAN | ufw-Regel auf LAN-Subnetz |
| 853/tcp | AdGuard DoT | nur LAN, falls benötigt | prüfen, ob gebraucht |
| 80/tcp | Traefik HTTP | geschlossen | Nach Traefik-Umstellung nicht mehr nötig |
| 443/tcp | Traefik HTTPS | nur LAN/WireGuard, bei Bedarf öffentlich | Entscheidung offen |
| 111/tcp+udp | rpcbind | geschlossen | deaktivieren |
| 3000/tcp | unbekannt (Arcane?) | nur über Traefik oder LAN | identifizieren |
| 3552/tcp | unbekannt | nur über Traefik oder LAN | identifizieren |
| 5900/tcp | VNC | geschlossen | abschalten, wenn nicht gebraucht |
| 8000/tcp | Paperless (vermutlich) | nur über Traefik | `ports:` durch `expose:` ersetzen |
| 9443/tcp | Portainer | nur über Traefik/WireGuard | Zugriff beschränken |
| 19999/tcp | netdata | nur LAN | Binding auf LAN-IP |
| 61208/tcp | glances | nur LAN | Binding auf LAN-IP |
| 5353/udp | mDNS | nur LAN, sonst aus | Avahi prüfen |
| 51671/udp, 35788/udp | unbekannt | identifizieren | prüfen |
| 4317/tcp, 8125/udp | OpenTelemetry/StatsD | nur lokal | bereits lokal, ok |
| 2283/tcp | Immich (geplant) | nur über Traefik | nicht veröffentlichen |
| 9000/tcp | Mealie (geplant) | nur über Traefik | nicht veröffentlichen |
| 3001/tcp | Uptime Kuma (geplant) | nur über Traefik | nicht veröffentlichen |

## Umsetzungsreihenfolge

1. **Lokal prüfen:** `sudo ufw status verbose` und `sudo ss -tulpn` auf dem Pi. Danach Register abgleichen.
2. **FRITZ!Box:** UPnP aus, Freigaben prüfen und entfernen.
3. **Ungenutzte Dienste abschalten:** VNC, rpcbind, ggf. Avahi.
4. **ufw aktivieren** mit Standard deny eingehend. Erst SSH-Regel für LAN und WireGuard setzen, dann aktivieren, damit du dich nicht aussperrst.
5. **Docker-Ports umstellen:** Bindings auf LAN-IP oder 127.0.0.1, interne Dienste auf `expose:`.
6. **Traefik einführen,** dann die Dienste umstellen und Port 80 schließen.
7. **Test:** Von innen (LAN), von WireGuard und von außen (Handy im Mobilfunknetz) prüfen. Nur die erwarteten Ports dürfen antworten.
8. **Monatliche Routine** eintragen, z. B. als Uptime-Kuma-Erinnerung oder Kalendereintrag.

## Warnungen

- SSH nie zuerst sperren, bevor die Regel für LAN/WireGuard aktiv ist. Sonst sperrst du dich selbst aus. Vorher eine zweite Sitzung offen halten.
- `ufw` allein reicht bei Docker nicht. Immer den Test von außen durchführen.
- Eine Freigabe „nur kurz zum Testen“ bekommt sofort einen Eintrag im Register und einen Termin zum Entfernen.

## Verweise

- [[Pi Setup-Übersicht]]
- [[Pi Reverse Proxy]]
- [[Pi Uptime Kuma]]
