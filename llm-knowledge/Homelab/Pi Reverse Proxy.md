---
type: projekt
tags: [homelab, raspberry-pi, traefik, https, letsencrypt, reverse-proxy]
status: geplant
updated: 2026-11-27
---

# Reverse Proxy mit HTTPS auf dem Pi

Ziel: Alle Dienste über HTTPS mit gültigem Let's-Encrypt-Zertifikat erreichen, ohne offene Ports ins Internet. Gewählt: **Traefik** mit DNS-01-Challenge.

## Entscheidung

- **Traefik** statt Nginx Proxy Manager. Begründung:
  - Routing steht als Labels in der jeweiligen Compose-Datei, dadurch versionierbar und zusammen mit dem Dienst nachvollziehbar.
  - Keine Konfiguration in einer Datenbank, das vereinfacht Restore und Umzug.
  - Bei acht bis zehn Diensten ist der Mehraufwand gering.
- **NPM wäre die Alternative**, wenn du lieber mit einer Web-Oberfläche arbeitest und keine Labels pflegen willst.

## Warum DNS-01

- HTTP-01 braucht Port 80 aus dem Internet. Das soll nicht sein.
- DNS-01 beweist den Domain-Besitz über einen DNS-Eintrag. Die Dienste bleiben intern, die Zertifikate werden trotzdem gültig.
- Wildcard-Zertifikate (`*.deine-domain.de`) sind nur über DNS-01 möglich.

## Voraussetzungen

- Eigene Domain, bei einem Anbieter, der von Traefik (lego) unterstützt wird
- API-Token des DNS-Anbieters mit Schreibrecht nur auf die Zone
- Port 443 im Heimnetz erreichbar, Ports 80/443 nicht ins Internet weitergeleitet
- AdGuard als lokaler DNS-Server, der die Subdomains auf den Pi auflöst

## Zielbild

- Traefik-Container mit Entrypoints `web` (Port 80, nur Redirect auf HTTPS) und `websecure` (Port 443)
- Zertifikat-Resolver `letsencrypt` mit DNS-01 über den Provider der Domain
- Docker-Provider, Labels pro Dienst, `exposedByDefault=false`
- Docker-Zugriff über `tecnativa/docker-socket-proxy` statt direkt über den Socket
- Speicher für Zertifikate: `acme.json` mit chmod 600, im restic-Backup enthalten
- Dashboard nur intern erreichbar, ohne öffentlichen Zugang
- Lokale DNS-Auflösung in AdGuard: Rewrite `*.deine-domain.de` → IP des Pi

## Dienste, die umgestellt werden

| Dienst | Aktuell | Ziel-URL | Hinweis |
|---|---|---|---|
| Mealie | `http://<pi>:9000` | `https://mealie.<domain>` | zuerst umstellen, geringes Risiko |
| Uptime Kuma | `http://<pi>:3001` | `https://status.<domain>` | danach Monitore anpassen |
| Paperless | `http://<pi>:8000` | `https://paperless.<domain>` | Port vorher bestätigen |
| Immich | (geplant, 2283) | `https://immich.<domain>` | bei Einrichtung direkt über Traefik |
| Portainer | `https://<pi>:9443` | `https://portainer.<domain>` | Zugriff zusätzlich einschränken |
| AdGuard-UI | Port unklar | `https://adguard.<domain>` | Port vorher bestätigen |
| netdata, glances | 19999, 61208 | optional | nur intern |

Hinweis: Mealie und Uptime Kuma sind in dieser Notiz mit ihren Standardports eingetragen. Der tatsächliche Stand ist vor dem Umstellen zu prüfen.

## Phasen

### Phase 0 – Vorbereitung
- [ ] Domain festlegen, DNS-Anbieter ermitteln
- [ ] Prüfen, ob der DNS-Anbieter in der Traefik-Dokumentation für DNS-01 steht
- [ ] API-Token mit minimalem Recht anlegen (nur die Zone), in einer Datei mit chmod 600 ablegen, nicht im Compose-Eintrag
- [ ] Ports der offenen Dienste prüfen (AdGuard-UI, Dienste hinter 80/443)

### Phase 1 – Traefik installieren
- [ ] Compose-Eintrag mit festem Versions-Tag (keine `latest`-Tags)
- [ ] Socket-Proxy mit Leserechten einrichten
- [ ] `acme.json` anlegen, chmod 600
- [ ] Traefik starten, Logs auf Fehler prüfen
- [ ] Testdienst (z. B. `whoami`) mit Label anbinden und Zertifikat prüfen

### Phase 2 – AdGuard
- [ ] DNS-Rewrite `*.<domain>` auf die IP des Pi anlegen
- [ ] Auflösung von außen und innen testen (Heimnetz und WireGuard)

### Phase 3 – Dienste umstellen
- [ ] Mealie zuerst, dann Uptime Kuma
- [ ] Danach Paperless, Portainer und AdGuard-UI
- [ ] Immich direkt mit HTTPS aufsetzen
- [ ] Alte HTTP-Ports nach Umstellung schließen, die Dienste nur noch über Traefik erreichbar machen

### Phase 4 – Monitoring und Backup
- [ ] Uptime-Kuma-Monitore auf HTTPS-Adressen umstellen
- [ ] Zertifikatsablauf in Uptime Kuma überwachen (Option für Zertifikat-Check)
- [ ] `acme.json` ins restic-Backup aufnehmen

### Phase 5 – Pflege
- [ ] Traefik-Version manuell aktualisieren, Release-Notes lesen
- [ ] Zertifikatserneuerung einmal im Quartal prüfen

## Sicherheit

- Dashboard nicht öffentlich, am besten nur über WireGuard erreichbar
- Socket-Proxy statt direktem Docker-Socket
- Standardmäßig keine Dienste exponieren (`exposedByDefault=false`)
- Admin-Oberflächen (Portainer, AdGuard) mit eigener Authentifizierung und, wenn möglich, Zugriffsbeschränkung
- API-Token nie in Logs oder Notizen im Klartext

## Offene Entscheidungen

- Welche Domain und welcher DNS-Anbieter? Davon hängt das Plugin ab.
- Traefik oder NPM? Entschieden: Traefik, falls du das anders willst, passe die Notiz an.
- Sollen Dienste auch von außerhalb des Heimnetzes über HTTPS erreichbar sein, oder nur über WireGuard?

## Verweise

- [[Pi Setup-Übersicht]]
- [[Pi Uptime Kuma]]
- [[Pi Mealie]]
- [[Pi Backup-Migration Restic]]
