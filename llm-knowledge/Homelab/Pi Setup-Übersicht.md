---
type: uebersicht
tags: [homelab, raspberry-pi, docker, monitoring]
status: lebend
updated: 2026-11-27
---

# Raspberry Pi – Setup-Übersicht

Stand: 2026-11-27. Host `raspberrypi` (Raspberry Pi OS, Debian, aarch64), Zugriff per SSH über Host-Alias `pi` in `~/.config/opencode/ssh-pi.conf`.

## Zustand (Snapshot 2026-11-27)

- Laufzeit: 12 Tage ohne Neustart, Load 0,4–0,5
- Temperatur: 66,2 °C, aktuell kein Throttling (Flag `0x80000` = Temperaturgrenze seit letztem Boot einmal erreicht)
- RAM: 7,6 GiB gesamt, 1,9 GiB belegt, 5,8 GiB Cache. Swap ungenutzt.
- Festplatte: SSD `/dev/sda2`, ext4, 229 GB, 20 GB belegt (9 %)
- Systemd: keine fehlgeschlagenen Dienste

## Docker-Container

| Container | Image | Zweck |
|---|---|---|
| paperless-webserver-1 | ghcr.io/paperless-ngx/paperless-ngx:latest | Dokumentenverwaltung |
| paperless-db-1 | postgres:18 | Datenbank für Paperless |
| paperless-broker-1 | valkey/valkey:9-alpine | Queue/Cache für Paperless |
| adguardhome | adguard/adguardhome:latest | DNS-Filter (DNS 53, DoT 853) |
| portainer | portainer/portainer-ce:latest | Docker-Verwaltung (Port 9443) |
| arcane | ghcr.io/getarcaneapp/manager:latest | Docker-Verwaltung |

Hinweis: Mehrere Images laufen auf `:latest`. Updates können dadurch unerwartete Änderungen bringen.

## Netzwerk-Ports (lauschend)

| Port | Vermutlich | Status |
|---|---|---|
| 22 | SSH | bestätigt |
| 53, 853 | AdGuard Home (DNS, DoT) | bestätigt |
| 80, 443 | Reverse Proxy oder Web-UI | **offen**, Dienst nicht identifiziert |
| 111 | rpcbind (NFS) | bestätigt, NFS-Server inaktiv |
| 3000 | Arcane oder Web-UI | offen |
| 8000 | Paperless-Webserver | vermutlich |
| 3552 | Arcane-Agent oder Dienst | offen |
| 5900 | VNC (wayvnc) | bestätigt, auf allen Interfaces |
| 9443 | Portainer | bestätigt |
| 19999 | netdata | bestätigt |
| 61208 | glances | bestätigt |
| 4317, 8125 | OpenTelemetry bzw. StatsD (nur lokal) | bestätigt |

## Weitere Geräte

- Home Assistant läuft als Home Assistant OS auf einem separaten Raspberry Pi. Nicht Teil dieses Hosts, nicht Teil des Backups hier.

## Fernzugriff

- VPN: WireGuard auf der FRITZ!Box. Der Pi ist darüber aus dem Heimnetz bzw. von unterwegs erreichbar, ohne Dienste direkt ins Internet freizugeben.

## Systemdienste (aktiviert)

- Monitoring: netdata, glances, lm-sensors
- Netzwerk: NetworkManager, rpcbind
- Druck: cups
- Desktop/Grafik: lightdm, wayvnc-control (VNC)
- Container: docker, containerd
- Wartung: rpi-eeprom-update, udisks2, e2scrub_reap, rp1-test, glamor-test

## Backup

- **Paperless-Export (aktiv):** Cron `0 3 * * *` → `~/bin/backup-paperless.sh`
  - `document_exporter` nach `~/apps/paperless/export`
  - `rclone sync` nach `grive-crypt:paperless-backups/<datum>`
  - Aufbewahrung: letzte 3 Datumsordner
  - Log: `~/backups/paperless-backup.log`
  - Letzter erfolgreicher Lauf im Log: 2026-11-27 09:32 (manuell oder Cron-Lauf offen)
- **Geplante Migration:** siehe [[Pi Backup-Migration Restic]]

## Cron und Timer (systemd)

- Cron: `backup-paperless.sh` um 3:00
- Timer: `rpi-zram-writeback`, `apt-daily`, `apt-daily-upgrade`, `dpkg-db-backup`, `logrotate`, `man-db`, `systemd-tmpfiles-clean`, `e2scrub_all`, `fstrim`

## Offene Punkte

- Dienst auf Port 80/443 identifizieren (Reverse Proxy?)
- Ports 3000, 3552 zuordnen
- VNC (5900) auf alle Interfaces: abschalten oder nur über VPN erreichbar machen
- Keine Erfolgsüberwachung für Backups
- Latest-Tags bei Containern prüfen
