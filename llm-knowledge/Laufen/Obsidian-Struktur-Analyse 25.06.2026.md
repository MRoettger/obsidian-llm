# 🏗️ Obsidian-Struktur für Laufen — Analyse & Verbesserungen

**Stand: 25. Juni 2026 | Nach 5-km-Test Auswertung**

---

## Aktuelle Struktur (IST)

```
Laufen/
├── Aktueller Fitnessstatus.md      — CTL/ATL/TSB Live-Status
├── Herzfrequenzzonen.md             — Zonen-Definitionen
├── Laufziele.md                     — Saisonziele
├── Renntag-Erkenntnisse.md          — Fehler-Datenbank aus Rennen
├── Trainingsbausteine 5km.md        — VO2max, Threshold, Long Run
├── Trainingsmethoden HM Marathon.md — HM/Marathon-Training
├── Trainingspr\u00e4ferenzen.md      — Persönliche Vorzüge, Routine
└── Wochenbericht 2026-06-18 bis 06-25.md — Analyse einer Woche
```

**Was funktioniert gut:**
- ✅ Klar kategorisiert (Ziele, Status, Training, Erkenntnisse)
- ✅ Jede Datei hat klare Funktion
- ✅ Verknüpfungen (Links) zwischen Dateien
- ✅ Regelmäßige Wochenberichte als "Spiegel"

---

## Probleme & Lücken

### 1. **Keine actionable Checklisten/Workflows**
**Problem:** Renntag-Erkenntnisse sind konzeptionell, aber wenn es Zeit zu rennen ist, muss man sie erst noch umlegen in konkrete Schritte.

**Lösung:** ✅ **GELÖST** — [[Rennvorbereitung-Checkliste]] hinzugefügt
- 3 MUST-HAVES klar formatiert
- 1-Woche-Checkliste + Renntag-Checkliste
- Schnelle Entscheidungsregel: "Wenn zwei von drei ausfallen → verschieben"

### 2. **Keine prospektive Test-Dokumentation**
**Problem:** Test-Daten werden nachträglich analysiert (wie heute). Bessere Struktur: **vor dem Test** alle Bedingungen dokumentieren, dann systematisch ausfüllen.

**Lösung:** ✅ **GELÖST** — [[5km-Test-Protokoll]] hinzugefügt
- Pre-Test Checkliste (3–4 Tage davor)
- Test-Tag Dokumentation (Wetter, Status, Splits)
- Post-Test Analyse (was lief gut, was nicht)
- Template für nächsten Versuch

### 3. **Wochenberichte nicht standardisiert**
**Problem:** Nur eine Woche dokumentiert (18.–25.06.). Künftig: Jede Woche sollte im gleichen Format auftauchen, damit Trends sichtbar werden.

**Lösung:** 📋 **NOCH OFFEN** — Wochenberichte-Template anlegen
```
Laufen/Wochenberichte/
├── Wochenbericht 2026-06-18 bis 06-25.md
├── Wochenbericht 2026-06-25 bis 07-02.md
├── _Wochenbericht-Template.md (Blanko-Form)
```

### 4. **Langzeittrends sind schwer zu sehen**
**Problem:** CTL/ATL/TSB sind live in Intervals.icu, aber Obsidian hat keine Übersicht über Trends über Monate.

**Lösung:** 📊 **OPTIONAL** — Monatsbericht über langfristige Trends
```
Laufen/Monatsberichte/
├── Monatsbericht Juni 2026.md  — Aggregation der 4 Wochen
```

### 5. **Kein klarer "nächster Test"-Plan**
**Problem:** Test war am 24.06., ist gescheitert, aber keine strukturierte "Retry-Planung" in Obsidian.

**Lösung:** ✅ **EMPFOHLEN** — Nächsten Test gezielt einplanen
- Kandidat: **22.07.2026** (Morgen, < 15 °C, TSB +10, nach 2 Taper-Woche)
- Diese Planung sollte in einem neuen "5km-Retry-Plan.md" stehen oder in die Laufziele integriert werden

---

## 🎯 Empfohlene Struktur (SOLL)

```
Laufen/
├── 📌 ÜBERSICHT/
│   ├── Laufziele.md                      — Saisonziele & kommende Tests
│   ├── Aktueller Fitnessstatus.md        — Live CTL/ATL/TSB
│   └── Herzfrequenzzonen.md              — Zonen-Referenz
│
├── 🏋️ TRAINING/
│   ├── Trainingsbausteine 5km.md         — VO2max, Threshold, Long
│   ├── Trainingsmethoden HM Marathon.md  — Übergang zu längeren Distanzen
│   ├── Trainingspr\u00e4ferenzen.md      — Persönliche Routinen
│   └── _Trainingsblock-Template.md       — (optional) Für Periodisierung
│
├── 📊 DOKUMENTATION & AUSWERTUNG/
│   ├── Wochenberichte/
│   │   ├── Wochenbericht 2026-06-18 bis 06-25.md
│   │   └── _Wochenbericht-Template.md     — Blanko-Form für neue Wochen
│   │
│   ├── Monatsberichte/
│   │   └── Monatsbericht Juni 2026.md    — (optional) Langzeittrends
│   │
│   └── Renntag-Erkenntnisse.md           — Fehler-Datenbank, aktualisiert nach Tests
│
├── 🏁 RENNVORBEREITUNG & TESTS/
│   ├── Rennvorbereitung-Checkliste.md    — 3 MUST-HAVES, 1-Woche + Renntag-Checklist
│   ├── 5km-Test-Protokoll.md             — Dokumentations-Vorlage für alle 5-km-Tests
│   ├── 5km-Retry-Plan 22.07.2026.md      — Nächster Versuch (Datum, Taper-Plan)
│   └── (optional) Wettkampf-Planung.md   — Wenn echte Rennen kommen
│
└── Python/                               — Unabhängig
```

---

## 🔑 Konkrete nächste Schritte

### Sofort (bis 26.06.)
- [ ] **5km-Retry-Plan einplanen**: 22.07.2026, Morgenstart 08:00, Taper ab 20.07.
  - Einplanen in Intervals.icu als Event
  - [[Rennvorbereitung-Checkliste]] am 20.07. durchgehen
  
- [ ] **Wochenbericht-Template** in Obsidian als Blanko erstellen, damit 26.06.–03.07. systematisch dokumentiert wird

### Diese Woche (bis 01.07.)
- [ ] **Wochenberichte ab sofort strukturiert schreiben** (Format: TSB-Trend, Training-Qualität, Schlaf-Score, nächste Woche Fokus)
- [ ] **Erste 5-km-Test ausfüllen** mit dem [[5km-Test-Protokoll]] retrospektiv (24.06.)

### Optional (für später)
- [ ] Monatsbericht-Template (zum Ende Juni)
- [ ] Trainingsblock-Planung (wenn Periodisierung klarer wird)

---

## Verknüpfungen

**Neu verlinkt in Laufziele:**
- [[5km-Retry-Plan 22.07.2026]] (zu erstellen)
- [[Rennvorbereitung-Checkliste]]
- [[5km-Test-Protokoll]]

**Neu verlinkt in Renntag-Erkenntnisse:**
- [[5km-Test-Protokoll]]
- [[Rennvorbereitung-Checkliste]]

---

*Erstellt: 25. Juni 2026 | Aktualisierung der Obsidian-Struktur nach 5-km-Test-Analyse*
