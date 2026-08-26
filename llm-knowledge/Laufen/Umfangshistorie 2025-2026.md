---
type: analyse
tags: [laufen, umfang, historie, analyse]
status: abgeschlossen
updated: 2026-08-26
---

# 📈 Umfangshistorie Juni 2025 – August 2026

Auswertung aller Laufaktivitäten aus Intervals.icu über 64 Wochen. Anlass: die Frage, ob Wochenumfänge von 100–120 km realistisch sind. Diese Notiz hält **nur den Rückblick** fest — keine Planung.

---

## 🔑 Kennzahlen

| Kennzahl | Wert |
|----------|------|
| Höchste Wochenumfang | **100,1 km** (Woche ab 01.09.2025) |
| Längster Einzellauf | **42,3 km** (21.09.2025) |
| Wochen ≥ 70 km | 5 |
| Wochen ≥ 60 km | 11 |
| **Längste Serie ≥ 60 km** | **3 Wochen** (27.04.–17.05.2026) |
| **Längste Serie ≥ 50 km** | **5 Wochen** (27.04.–31.05.2026) |
| Ø über 64 Wochen | **38,7 km** |
| Verletzungen | **keine** |

---

## 📊 Wochenumfänge (km, Woche ab Montag)

| Monat | Wochenwerte |
|-------|-------------|
| Jun 2025 | 50 · **70** · 42 · 32 · 13 |
| Jul 2025 | 58 · 28 · 61 · 57 |
| Aug 2025 | 47 · 67 · 58 · 11 |
| Sep 2025 | **100** · 41 · 44 · 0 · 18 |
| Okt 2025 | 10 · 19 · 12 · 15 |
| Nov 2025 | 8 · 32 · 8 · 25 |
| Dez 2025 | 18 · 20 · 57 · 54 · 0 |
| Jan 2026 | 10 · 58 · 39 · 43 |
| Feb 2026 | 42 · 40 · 48 · 40 |
| Mär 2026 | 17 · 41 · 44 · 40 · 22 |
| Apr 2026 | **73** · 59 · 20 · **71** |
| Mai 2026 | **74** · **71** · 56 · 61 |
| Jun 2026 | 39 · 59 · 30 · 18 · 60 |
| Jul 2026 | 16 · 0 · 36 · 9 |
| Aug 2026 | 44 · 57 · 62 |

**Bester zusammenhängender Block:** 06.04.–31.05.2026 — 8 Wochen à Ø 61 km, drei davon ≥ 70 km. Der Einbruch auf 20 km (Woche ab 20.04.) war eine Zwift-/Radwoche, kein Ausfall.

---

## 💡 Erkenntnisse

**1. Die Belastbarkeit ist nachgewiesen, die Dauerhaftigkeit nicht.**
Eine 100-km-Woche und ein 42-km-Lauf zeigen, dass der Bewegungsapparat hohe Einzelbelastungen trägt. Was in den Daten *nirgends* steht: mehr als drei aufeinanderfolgende Wochen über 60 km. Ein 16-Wochen-Block bei 90–110 km verlangt zwölf bis vierzehn Wochen am Stück — eine Beanspruchung, die bisher nie getestet wurde.

**2. Die Einbrüche waren Planung, keine Verletzungen.**
Über den gesamten Zeitraum keine einzige Laufverletzung. Die Löcher erklären sich durch Radurlaube (30.06.2025, 13.07.2026), Reisen, Badmintonsaison und die Off-Season nach dem 42er im September 2025. **Daraus folgt: der begrenzende Faktor ist die Kalenderplanung, nicht der Körper.** Umfangsziele dürfen entsprechend ambitioniert angesetzt werden.

**3. Das Sägezahnmuster ist der eigentliche Leistungsverlust.**
Der 64-Wochen-Schnitt von 38,7 km liegt weit unter dem, was die guten Wochen andeuten. Nicht die Höhe der Spitzenwochen war das Limit, sondern wie oft sie von 10–20-km-Wochen unterbrochen wurden. Die aerobe Substanz wurde dadurch wiederholt auf- und wieder abgebaut.

**4. Die Abbruchkriterien bleiben gültig.**
Trotz Punkt 2 gilt die Warnung aus [[Wettkampf 2026-09-13 Münster 28]] weiter: punktueller Schmerz an Schienbeinkante, Ferse oder Mittelfuß, der im Laufverlauf zunimmt statt nachzulassen → auf Rad umstellen. „Nie verletzt" bei Ø 38,7 km ist schwächere Evidenz als „nie verletzt bei konstant 90 km".

---

## ⚠️ Methodenhinweis für spätere Auswertungen

Die Intervals.icu-Rohdaten enthalten zwei Fallstricke, die die Zahlen sonst massiv verfälschen:

1. **Doppelte Aktivitäten** bei überlappenden Abfragezeiträumen → immer über die Activity-ID deduplizieren. Ohne Dedup erschienen Januar/Februar 2026 fälschlich als 80–115-km-Block.
2. **Falsch getaggte Radfahrten**: die Einträge „Tour de France Stage 13/14" (205 km / 155 km, 23.04.2026) sind als `Type: Run` gespeichert. Einzelläufe > 60 km herausfiltern.
3. Laufbandeinheiten laufen als `Type: VirtualRun` — mitzählen, sonst fehlen ~10 Einheiten.

---

## Verwandte Notizen

[[Laufziele]] · [[Trainingsplan HM Sub-120 2026]] · [[Wettkampf 2027-03-21 Venloop]] · [[Wettkampf 2026-09-13 Münster 28]] · [[HM-Aufbau Forschungsgrundlagen 2026]]

---
*Angelegt: 26.08.2026 | Datenquelle: Intervals.icu, 64 Wochen (02.06.2025–23.08.2026), dedupliziert*
