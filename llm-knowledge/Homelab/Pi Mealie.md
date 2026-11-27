---
type: projekt
tags: [homelab, raspberry-pi, mealie, rezepte, docker]
status: geplant
updated: 2026-11-27
---

# Mealie auf dem Pi

Ziel: Selbstgehosteter Rezeptmanager (Rezepte importieren, Wochenplan, Einkaufsliste). Läuft als Docker-Container auf dem Pi, eingebunden in Backup und Monitoring.

## Ausgangslage

- Port 9000 (Mealie Standard) ist frei. Belegt sind 80, 443, 3000, 3552, 8000, 9443, 19999, 61208 und weitere.
- Ressourcen: Mealie ist leicht, RAM und CPU sind kein Engpass. Die Last kommt eher von Immich-ML, falls du das später aktivierst.
- Backup: Mealie hat eine eigene Backup-Funktion in den Einstellungen (ZIP-Export). Die kannst du zusätzlich nutzen.

## Zielbild

- Container `ghcr.io/mealie-recipes/mealie` mit festem Versions-Tag, nicht `:latest`
- Daten unter `~/apps/mealie/data` als Bind-Mount
- Zugriff lokal und über WireGuard (FRITZ!Box)
- Kein Port nach außen. Falls du es später öffentlich brauchst, über den Reverse Proxy mit TLS.
- Backup: Datenverzeichnis per restic, zusätzlich die Mealie-Backup-ZIPs
- Monitoring: HTTP-Check auf Port 9000 in Uptime Kuma

## Compose-Eintrag (Vorschlag)

Die genauen Variablen vor dem Einrichten im Mealie-Doku-Stand prüfen.

- `BASE_URL`: Adresse, mit der du Mealie aufrufst (lokal oder per Hostname)
- `TZ=Europe/Berlin`
- `ALLOW_SIGNUP=false` nach dem ersten Konto, damit sich niemand fremdes registriert
- Admin-Konto mit starkem Passwort, nicht im Compose-Eintrag im Klartext

## Backup-Integration

- Die Mealie-Datenbank ist standardmäßig SQLite. Im laufenden Betrieb nicht einfach die Datei kopieren, weil sie dabei inkonsistent werden kann. Zwei saubere Wege:
  1. Mealie-eigenes Backup über die Oberfläche oder API, das ZIP dann per restic sichern.
  2. Kurz den Container stoppen, Datenverzeichnis sichern, Container wieder starten.
- Empfehlung: Variante 1 für den täglichen Lauf, Variante 2 nur als seltenen Komplett-Snapshot. Das passt zum Ablauf im restic-Skript.
- Entsprechend in der restic-Migration: Pfad `~/apps/mealie` ergänzen, plus Mealie-Backup-Verzeichnis.

## Phasen

### Phase 0 – Vorbereitung
- [ ] Mealie-Doku auf aktuelle Version und Variablen prüfen
- [ ] Port 9000 bestätigen (frei)
- [ ] Entscheiden: SQLite (Standard, reicht für wenige Nutzer) oder PostgreSQL. Empfehlung: SQLite.

### Phase 1 – Installation
- [ ] Compose-Eintrag mit festem Tag anlegen
- [ ] Container starten, erstes Konto anlegen, danach `ALLOW_SIGNUP=false`
- [ ] Testimport eines Rezepts per URL

### Phase 2 – Backup
- [ ] Mealie-Backup in den Einstellungen aktivieren oder manuell auslösen
- [ ] Ordner `~/apps/mealie` und Mealie-Backups in das restic-Skript aufnehmen
- [ ] Restore-Test: Backup in eine Test-Instanz einspielen

### Phase 3 – Monitoring
- [ ] HTTP-Monitor auf `http://<pi>:9000` in Uptime Kuma anlegen

### Phase 4 – Pflege
- [ ] Versionsupdates manuell prüfen, Release-Notes lesen (Breaking Changes möglich)

## Offene Entscheidungen

- Nur für dich oder auch für andere Haushaltsmitglieder? Dann mehrere Konten, eventuell Gruppen.
- Soll Mealie von außen erreichbar sein (Reverse Proxy und TLS) oder nur über WireGuard?

## Verweise

- [[Pi Setup-Übersicht]]
- [[Pi Backup-Migration Restic]]
- [[Pi Uptime Kuma]]
