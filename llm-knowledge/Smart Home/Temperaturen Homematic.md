---
type: messwerte
tags: [smart-home, homematic, temperatur, heizung]
quelle: Home Assistant (MCP)
stand: 2026-11-16 20:27
---

# 🌡️ Temperaturen – Homematic IP

Momentaufnahme aus Home Assistant vom **16.11.2026, ca. 20:27 Uhr**. Alle Geräte sind
Homematic IP (eQ-3) und hängen über den Access Point `HmIP-HAP2` an der Cloud-Verbindung.
Aktuelle Werte stehen nur in Home Assistant, diese Seite ist nur eine Momentaufnahme.

## Räume (Heizgruppen)

| Raum (Name in HA) | Ist °C | Soll °C | Modus | Entität |
|---|---:|---:|---|---|
| Büro | 18,9 | 18,5 | heat | `climate.raum_2_hmip_raum_2` |
| Wohnzimmer Tür | 19,9 | 18,0 | heat | `climate.hmip_bad` |
| Wohnzimmer Essbereich | 19,3 | 18,5 | heat | `climate.hmip_kuche` |
| Schlafzimmer | 17,2 | 17,0 | heat | `climate.hmip_schlafzimmer` |
| Bad | 19,7 | 17,5 | heat | `climate.hmip_wohnzimmer` |
| Gästezimmer | 18,1 | 18,0 | heat | `climate.hmip_buro` |

- Einstellbereich bei allen Gruppen: 5,0 bis 30,0 °C.
- Preset überall `none`, `hvac_action` meldet HA nicht.
- Durchschnitt Ist: ca. 18,9 °C. Kühlster Raum: Schlafzimmer (17,2), wärmster: Wohnzimmer Tür (19,9).

## Heizkörperthermostate

| Gerät (Name in HA)             | Typ           | Temperatur °C | Ventil % | Batterie | Entität (Temperatur)                                  |
| ------------------------------ | ------------- | ------------: | -------: | -------- | ----------------------------------------------------- |
| Radiator Thermostat Raum 2     | HmIP-eTRV-2   |          18,9 |       33 | ok       | `sensor.hmip_heating_thermostat_temperature_2`        |
| Radiator Thermostat büro       | HmIP-eTRV-2   |          19,9 |        0 | ok       | `sensor.hmip_heating_thermostat_temperature`          |
| Radiator Thermostat Küche      | HmIP-eTRV-2   |          19,3 |        2 | ok       | `sensor.hmip_heating_thermostat_temperature_3`        |
| Radiator Thermostat Wohnzimmer | HmIP-eTRV-2   |          19,7 |        0 | ok       | `sensor.hmip_heating_thermostat_temperature_4`        |
| Radiator Thermostat - compact  | HmIP-eTRV-C-2 |          17,2 |        0 | ok       | `sensor.hmip_radiator_thermostat_compact_temperature` |
| Büro Thermostat                | HmIP-eTRV-2   |          18,1 |       29 | ok       | `sensor.hmip_buro_thermostat_temperature`             |

## Zuordnung Thermostat ↔ Raum

Die Gerätenamen in HA passen nicht zu den Raumnamen der Heizgruppen. Die Zuordnung
unten ist **aus identischen Messwerten abgeleitet**, nicht aus der HA-Konfiguration.
In HA lassen sich die Gruppenmitglieder prüfen und die Namen angleichen.

| Raum (Heizgruppe) | Thermostat mit gleichem Wert |
|---|---|
| Büro | Radiator Thermostat Raum 2 |
| Wohnzimmer Tür | Radiator Thermostat büro |
| Wohnzimmer Essbereich | Radiator Thermostat Küche |
| Schlafzimmer | Radiator Thermostat - compact |
| Bad | Radiator Thermostat Wohnzimmer |
| Gästezimmer | Büro Thermostat |

## Auffälligkeiten

- **Heizt gerade:** Büro (Ventil 33 %) und Gästezimmer (Ventil 29 %). Bei den anderen
  Räumen steht das Ventil bei 0 bis 2 %.
- **Bad und Wohnzimmer Tür** liegen 1,5 bis 1,9 °C über dem Soll, dort heizt nichts.
- Keine Batteriewarnung bei einem der sechs Thermostate.
- Die Namen der Heizgruppen und Geräte sind in HA vertauscht, siehe oben.

## Quellen

- Home Assistant `192.168.178.50:8123`, abgefragt über MCP (`render_template`)
- Nicht enthalten: Hue-Bewegungssensoren (Küche 14,0 °C, Flur 15,3 °C) und die
  FRITZ!Box CPU-Temperatur, weil sie nicht zu Homematic gehören
