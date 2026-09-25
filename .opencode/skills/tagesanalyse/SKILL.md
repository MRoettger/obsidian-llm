---
name: tagesanalyse
description: Umfassende Beurteilung einer einzelnen Trainingseinheit (Lauf, Rad, Kraft) aus Intervals.icu — Ausführungstreue, HF-Drift/Decoupling, Intervallqualität, Belastungseinordnung und Konsequenz für die nächsten Tage. Use when der Athlet nach "wie war mein Training heute", "beurteile den Lauf", "Tagesanalyse", "analysier die Einheit von gestern" fragt oder eine einzelne Aktivität bewertet haben will. NICHT für Wochenrückblick oder Wochenplanung — dafür ist /wochencheck zuständig.
---

# Tagesanalyse einer Einheit

Beurteilt **eine** Einheit gründlich. Abgrenzung: `/wochencheck` macht Soll-Ist über
die Woche und plant voraus. Diese Analyse geht in die Tiefe einer Session und endet
mit einer Konsequenz für die nächsten 1–3 Tage — nicht mit einem Wochenplan.

Keine Zonen, LTHR-Werte oder Zielpaces in dieser Datei. Die stehen in
`llm-knowledge/Laufen/Athletenstatus.md` und werden dort gelesen. Steht ein Wert in
beiden, gilt die Statusdatei.

**Rechne nicht im Kopf.** Für Decoupling, TSB, Schrittlängen-Drift, Riegel/VDOT und
Pacing gibt es `scripts/laufcoach.py`. Nutze es statt Überschlagsrechnungen — die
Formeln sind dort gegen echte Intervals.icu-Werte verifiziert:

```
python3 scripts/laufcoach.py tsb --ctl <ctl> --atl <atl>
python3 scripts/laufcoach.py riegel --from <m> --time <h:mm:ss> --to <m>
python3 scripts/laufcoach.py vdot --dist <m> --time <h:mm:ss>
```

Für `decoupling()`, `stride_drift()`, `resting_hr_flag()` und `polarization()` gibt
es keinen CLI-Befehl — die brauchen Messreihen. Dafür das Modul importieren:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from laufcoach import stride_drift
d = stride_drift({'pace': 256, 'hr': 152, 'cadence': 83.3},
                 {'pace': 271, 'hr': 152, 'cadence': 83.1})
print(d['stride_pct'], d['verdict'])"
```

(`pace` in s/km, `cadence` einbeinig wie von Garmin geliefert. Der `sys.path`-Zusatz
macht den Aufruf unabhängig davon, aus welchem Verzeichnis er läuft.)

Gib im Ergebnis die Zahl an, nicht den Aufruf.

## 1. Daten holen — in dieser Reihenfolge

1. Aktuelles Datum über das time-MCP.
2. `llm-knowledge/Laufen/Athletenstatus.md` — Zonen, LTHR, Zielpaces, aktives Ziel.
3. `get_activities` letzte 10 Tage. Daraus die zu analysierende Einheit
   identifizieren. Ist unklar welche gemeint ist: die jüngste Einheit nehmen und
   das ansagen, nicht rückfragen.
4. `get_activity_intervals` für die Einheit — **Pflicht** bei jeder Einheit mit
   Struktur (Intervalle, Schwelle, Fahrtspiel).
5. `get_activity_streams` — nur wenn die Intervalle eine Frage offen lassen, z. B.
   bei Drift-Verdacht im Long Run oder unplausiblen HF-Werten.
6. `get_wellness_data` letzte 14 Tage — CTL, ATL, Ruhepuls, Schlaf.
7. `get_events` ±3 Tage — war die Einheit so geplant?

Fehlt eine Quelle, benenne die Lücke, statt sie zu überspielen.

## 2. Die sechs Prüfblöcke

Arbeite alle sechs ab. Was unauffällig ist, bekommt eine Zeile — nicht weglassen,
denn "unauffällig" ist selbst ein Befund.

### A. Ausführungstreue

Geplantes Event gegen tatsächliche Einheit. Distanz, Struktur, Zielpace, HF-Korridor.
Abweichung ist nicht automatisch schlecht — bewerte, ob sie sinnvoll war. Gab es kein
geplantes Event, sag das und bewerte die Einheit für sich.

### B. Intensitätsverteilung

Zeit je Zone gegen die Absicht der Einheit. Der klassische Fehler ist die zu schnelle
Grundlageneinheit: locker geplant, in Zone 3 gelandet. Prüfe das explizit, auch wenn
die Einheit sich gut anfühlte. Bei einer harten Einheit umgekehrt: wurde die Zielzone
überhaupt erreicht und wie lange?

### C. Intervallqualität (bei strukturierten Einheiten)

Aus `get_activity_intervals` pro Rep: Pace, Ø-HF, Max-HF.

- **Pace-Konsistenz:** Hält die Pace über alle Reps? Ein Abfall über 3 % vom ersten
  zum letzten Rep heißt: zu schnell gestartet oder Pause zu kurz.
- **HF-Anstieg über die Serie:** normal und erwünscht. Erreicht die HF aber schon in
  Rep 1 das Maximum, war der Start zu hart.
- **Pausenqualität:** Fällt die HF in der Pause ausreichend ab? Wenn nicht, war die
  Pause zu kurz — Intensität schlägt kurze Pause.
- **Rep-Dauer:** Lag sie im wirksamen Bereich, oder waren die Abschnitte zu kurz für
  einen echten Reiz?

Nenne die Werte als Tabelle. Ohne Zahlen ist die Aussage wertlos.

### D. Aerobe Qualität — Drift und Decoupling

Bei Läufen ab ~45 min: erste gegen zweite Hälfte, Pace-zu-HF.

- Decoupling unter 5 % → aerob gut abgedeckt
- 5–10 % → Grenzbereich, meist Umfang oder Hitze
- über 10 % → zu schnell für den aktuellen Zustand, oder Hitze/Dehydrierung

Liefert Intervals.icu kein Decoupling (häufig `None`, wie bei fast allen Einheiten
des Athleten), rechne es mit `decoupling(speed, hr)` aus `scripts/laufcoach.py` über
die Streams oder Runden-Splits und sag, dass es eine eigene Rechnung ist.

Vergleiche das Ergebnis mit früheren Einheiten desselben Typs. Ein Einzelwert ohne
Vergleich sagt wenig.

### E. Belastungseinordnung

- Training Load der Einheit, CTL/ATL/TSB davor und danach.
- **TSB = CTL − ATL**, ausgerechnet nennen, nicht schätzen.
- Ruhepuls am Folgetag gegen den Schnitt der Vorwochen. Ist der Folgetag noch nicht
  da, sag das statt zu raten.
- **RPE/Feel gegen die objektive Load prüfen.** Hohe RPE bei niedriger Load ist das
  wichtigste Frühwarnzeichen überhaupt — schlechte Tagesform, nicht harte Einheit.
  Andersherum: niedrige RPE bei hoher Load ist ein gutes Formzeichen.

### F. Technik und Nebenbefunde

Kadenz und Schrittlänge gegen den persönlichen Normalbereich aus der Historie —
nicht gegen irgendeinen Lehrbuchwert. Auffällig fallende Kadenz bei gleicher Pace
deutet auf Ermüdung. Dazu Höhenmeter, Temperatur, Wind, sofern erfasst und relevant.

**Bei Läufen ab ~90 min zusätzlich Pflicht: Schrittlängen-Drift.** Vergleiche ein
frühes gegen ein spätes Segment mit `stride_drift()` aus `scripts/laufcoach.py`.
Das ist bei diesem Athleten der aussagekräftigste Einzelbefund — am 13.09.2026
brach das Tempo über die letzten 7 km um 5,5 % ein, bei **konstanter HF und
konstanter Kadenz**, also vollständig über die Schrittlänge. Das Limit ist
muskulär-strukturell, nicht kardiovaskulär.

Konsequenz für die Analyse: Eine unauffällige HF ist kein Beleg dafür, dass die
Einheit gut weggesteckt wurde. Zielwert ist Drift unter 3 %. Liegt er darüber,
gehört das in die Befunde, auch wenn Decoupling und HF sauber aussehen.

## 3. Revisionsauslöser prüfen

Geh die Auslöser aus Abschnitt 4.3 deines Prompts durch. Eine Einzeleinheit kann
einen davon auslösen — besonders Schmerzmeldungen, ein auffälliger Ruhepuls oder
eine dritte ausgefallene Schlüsseleinheit. Greift einer, sag es hier und ungefragt.
Die Tagesanalyse ist der häufigste Ort, an dem so etwas zuerst sichtbar wird.

## 4. Ausgabeformat

Halte dich an diese Struktur. Gesamtlänge: deutlich unter einer Bildschirmseite plus
Tabellen.

```
## <Einheit>, <Datum>

**Urteil:** <ein Satz — hat die Einheit ihren Zweck erfüllt, ja oder nein>

| Kennwert | Wert | Einordnung |
|---|---|---|
(Distanz, Pace, Ø/Max-HF, Load, TSB danach, Decoupling)

### Intervalle
(Tabelle pro Rep — nur bei strukturierten Einheiten)

### Was auffällt
(2–4 Punkte. Nur Befunde mit Konsequenz, keine Aufzählung von Selbstverständlichem.)

### Konsequenz für die nächsten Tage
(Konkret: was morgen und übermorgen ansteht bzw. was angepasst gehört. Wenn nichts
anzupassen ist, genau das sagen.)
```

## 5. Regeln

- **Erst Zahlen, dann Urteil.** Jede Bewertung hängt an einem konkreten Wert aus den
  Daten.
- **Eine gute Einheit ist eine gute Einheit.** Wenn alles passt, sag das in einem
  Satz und hör auf. Keine erfundenen Verbesserungspunkte.
- Bewerte gegen den **Zweck** der Einheit. Ein langsamer Long Run ist kein Mangel,
  ein zu schneller schon.
- **Keine Zielpace aus einer Einzeleinheit ableiten.** Ein guter Tag ist kein neuer
  Leistungsdatenpunkt. Nur eine Einheit, die wirklich als Referenz taugt — Test,
  Wettkampf oder eine saubere Referenzeinheit — gehört nach `Athletenstatus.md`.
  Schlage die Aufnahme vor und begründe sie, statt sie stillschweigend zu machen.
- **Kalender nur nach Rückfrage ändern.** Ergibt die Analyse, dass eine kommende
  Einheit angepasst gehört, sag was und warum — und frag, bevor du
  `add_or_update_event` oder `delete_event` aufrufst.
- Kein Schönreden. Wenn die Einheit ihren Zweck verfehlt hat, steht das im ersten
  Satz.
