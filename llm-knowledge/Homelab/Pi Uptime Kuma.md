---
type: projekt
tags: [homelab, raspberry-pi, monitoring, uptime-kuma]
status: geplant
updated: 2026-11-27
---

# Uptime Kuma auf dem Pi

Ziel: Aktive Überwachung der Dienste und Backups mit Benachrichtigung bei Ausfall. netdata zeigt Verläufe, meldet aber nichts aktiv. Uptime Kuma füllt diese Lücke, außerdem fehlt bisher eine Erfolgsüberwachung für die Backups.

Hinweis: Uptime Kuma läuft auf dem Pi, der überwacht wird. Fällt der Pi ganz aus, kommt auch keine Meldung. Dafür braucht es einen externen Check, z. B. über den Hetzner-Server oder einen Dienst wie UptimeRobot, der von außen pingt. Das ist offen, siehe unten.

## Ausgangslage

- Dienste auf dem Pi: Paperless (Webserver, Port 8000 vermutlich), AdGuard (DNS 53, DoT 853), Portainer (9443), netdata (19999), glances (61208), SSH (22)
- Geplant: Immich (Port 2283 Standard), Hetzner-Backup
- Backups: aktuell `backup-paperless.sh` per Cron um 3:00, bisher ohne Erfolgsüberwachung
- Port 3001 (Uptime Kuma Standard) ist frei. Port 3000 ist bereits belegt.

## Zielbild

- Uptime Kuma als Docker-Container, Daten in einem Bind-Mount unter `~/apps/uptime-kuma/data`
- HTTP-, Port- und DNS-Checks für alle Dienste
- Push-Monitore für Backups: Das Skript meldet nach erfolgreichem Lauf an eine Push-URL. Bleibt die Meldung aus, gibt es einen Alarm.
- Benachrichtigung über den gewählten Kanal
- Zugriff lokal und per WireGuard (FRITZ!Box)

## Monitore (Vorschlag)

| Monitor | Typ | Ziel | Intervall |
|---|---|---|---|
| Paperless | HTTP | `http://<pi>:8000` | 60 s |
| Immich | HTTP | `http://<pi>:2283` | 60 s, nach Phase 2 |
| AdGuard | HTTP | Web-UI `http://<pi>:3000`? | 60 s, Port prüfen |
| Portainer | HTTP | `https://<pi>:9443` | 300 s |
| netdata | HTTP | `http://<pi>:19999` | 300 s |
| Mealie | HTTP | `http://<pi>:9000` | 300 s, nach Einrichtung |
| SSH | Port | `<pi>:22` | 60 s |
| DNS | DNS | AdGuard über `<pi>:53` | 60 s |
| Backup Paperless (alt) | Push | täglich 3:00 | 26 h Toleranz |
| Backup Paperless (restic) | Push | täglich 4:00 | 26 h Toleranz |
| Backup Hetzner | Push | nach `restic copy` | 26 h Toleranz |
| Backup-Check | Push | monatlich `restic check` | 35 Tage Toleranz |

Hinweis: Die Port-Angaben für AdGuard-UI und die Dienste hinter 80/443 sind noch nicht gesichert. Vor dem Einrichten prüfen.

## Push-Integration in das Backup-Skript

Am Ende des Skripts, nur bei Erfolg:

```sh
curl -fsS -m 10 "$UPTIME_KUMA_PUSH_URL" > /dev/null
```

Der Push-URL-Wert liegt in der Umgebung oder in einer Datei mit chmod 600, nicht im Skript selbst. Dann ist die Information nicht versehentlich in Notizen oder Logs sichtbar.

## Benachrichtigung

Offen: Welcher Kanal?
- **ntfy:** einfach, self-hosted oder öffentlich, gut für Push aufs Handy
- **Telegram:** kostenlos, braucht einen Bot
- **E-Mail:** funktioniert, aber langsamer und weniger direkt

## Phasen

### Phase 0 – Vorbereitung
- [ ] Benachrichtigungskanal wählen
- [ ] Ports der Dienste prüfen (AdGuard-UI, Dienste hinter 80/443)

### Phase 1 – Installation
- [ ] Compose-Eintrag für `louislam/uptime-kuma` mit Bind-Mount anlegen
- [ ] Container starten, Admin-Konto mit starkem Passwort anlegen
- [ ] Zugriff nur lokal, nicht ins Internet freigeben

### Phase 2 – Monitore
- [ ] HTTP-, Port- und DNS-Checks wie in der Tabelle anlegen
- [ ] Benachrichtigung testen (Monitor kurz pausieren oder Fehler simulieren)

### Phase 3 – Backup-Pushes
- [ ] Push-Monitore für die Backups anlegen
- [ ] Push-Aufruf in das alte und das neue Backup-Skript einbauen
- [ ] Testen: Lauf erfolgreich, Monitor grün. Lauf absichtlich fehlschlagen lassen, Alarm prüfen.

### Phase 4 – Externer Check
- [ ] Entscheiden, wer den Pi von außen überwacht (z. B. Hetzner-Server, UptimeRobot oder Uptime Kuma auf einem zweiten Gerät)

### Phase 5 – Pflege
- [ ] Uptime Kuma selbst aktualisieren (Image-Tag prüfen)
- [ ] Monatlich Berichte prüfen, Fehlalarme anpassen

## Offene Entscheidungen

- Benachrichtigungskanal (ntfy, Telegram, E-Mail)
- Externer Check: wer überwacht den Pi, wenn er komplett ausfällt?
- Soll Uptime Kuma auch Immich und Hetzner-Backups überwachen, sobald diese laufen? (Vorschlag: ja)

## Verweise

- [[Pi Setup-Übersicht]]
- [[Pi Backup-Migration Restic]]
