---
type: projekt
tags: [homelab, raspberry-pi, backup, restic, paperless]
status: geplant
updated: 2026-11-27
---

# Pi Backup-Migration: rclone-Export → Restic

Ziel: Das bestehende nächtliche Paperless-Export-Backup (rclone sync nach `grive-crypt`) durch ein Restic-Repository ersetzen. Gewinn: Snapshots mit Versionierung, Deduplizierung, Integritätsprüfung, flexible Aufbewahrung und Sicherung von Postgres-Dump plus Konfiguration statt nur des Exports.

## Ausgangslage (Stand 2026-11-27)

- Host: Raspberry Pi (`raspberrypi`, Debian aarch64), Zugriff über Host-Alias `pi` in `ssh-pi.conf`.
- Systemplatte: SSD (`/dev/sda2`, ext4), 201 GB frei.
- Paperless-Stack unter `~/apps/paperless`:
  - Bind-Mounts: `data`, `media`, `consume`, `export`
  - Docker-Volumes: `paperless_pgdata`, `paperless_media`, `paperless_data`, `paperless_redisdata`
- Aktuelles Backup: Cron `0 3 * * *` → `~/bin/backup-paperless.sh`
  - `document_exporter` → `~/apps/paperless/export`
  - `rclone sync` nach `grive-crypt:paperless-backups/<datum>`
  - Aufbewahrung: letzte 3 Datumsordner
  - Log: `~/backups/paperless-backup.log`
- Beobachtung: Im Remote liegt bisher nur `2026-11-27/`. Die Aufbewahrung ist also noch nicht im Betrieb getestet.
- Tools: `rclone` v1.60.1 vorhanden, `restic` fehlt.
- Verfügbare rclone-Remotes: `gdrive`, `grive-crypt`, `grive-safe`.

## Zielbild

- Restic-Repository auf `grive-crypt`, z. B. `rclone:grive-crypt:restic-paperless`.
- Jeder Lauf: Snapshot aus
  - Postgres-Dump (`pg_dumpall` per `docker compose exec`), kein Roh-Kopieren des Volumes
  - Medien, `data`, `consume`, Compose-Dateien
  - Redis wird nicht gesichert (Cache/Queue)
- Aufbewahrung: `--keep-daily 7 --keep-weekly 4 --keep-monthly 6`, `prune` wöchentlich.

## Phasen

### Phase 0 – Vorbereitung
- [ ] `restic` installieren (`sudo apt install restic`, Passwort nötig, vom Nutzer einzugeben)
- [ ] Restic-Passwort in `~/.config/restic/paperless.pass` (chmod 600) ablegen
- [ ] Restic-Passwort zusätzlich im Passwortmanager sichern. Ohne Passwort sind alle Backups unbrauchbar.

### Phase 1 – Repository
- [ ] `restic -r rclone:grive-crypt:restic-paperless init`
- [ ] Erster Testlauf manuell, bevor automatisiert wird

### Phase 2 – Backup-Skript
- [ ] Skript schreiben: Dump in Staging-Verzeichnis, `restic backup` mit Tag `paperless`, danach `forget --prune` (wöchentlich)
- [ ] Logging und Fehlerausgabe festlegen

### Phase 3 – Parallelbetrieb (1–2 Wochen)
- [ ] Neuer Cron um 4:00, alter bleibt um 3:00
- [ ] Täglich prüfen, dass beide Logs „erfolgreich“ zeigen

### Phase 4 – Restore-Test (wichtigster Schritt)
- [ ] `restic restore latest --target /tmp/restore-test`
- [ ] Dump in temporären Postgres-Container einspielen
- [ ] Paperless daneben auf eigenem Port starten
- [ ] Prüfen: Dokumentenanzahl, Metadaten, einzelne PDFs öffnen

### Phase 5 – Umschalten
- [ ] Alten Cron-Eintrag auskommentieren (nicht löschen)
- [ ] Alten Ordner `paperless-backups` im Remote erst nach einigen Wochen entfernen

### Phase 6 – Laufender Betrieb
- [ ] Erfolgsüberwachung, z. B. Uptime Kuma Push-Check
- [ ] Monatlich `restic check`

## Offene Entscheidungen
- Remote: `grive-crypt` oder zusätzlich `grive-safe` für eine zweite Kopie?
- Neuer Backup-Zeitpunkt: 4:00 vorgeschlagen.
- Erst Test-Repository oder direkt das Ziel-Repository?
