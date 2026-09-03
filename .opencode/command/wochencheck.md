---
description: Wöchentlicher Coach-Check — Soll-Ist der letzten Woche, Statusdatei prüfen, kommende Woche planen.
agent: laufcoach
---

Führe den wöchentlichen Trainingscheck durch. Arbeite die Schritte in dieser
Reihenfolge ab und überspringe keinen.

Zusatzkontext vom Athleten (kann leer sein): $ARGUMENTS

## 1. Daten holen

- Aktuelles Datum über das time-MCP.
- `llm-knowledge/Laufen/Athletenstatus.md` lesen.
- Aktivitäten der letzten 14 Tage.
- Wellness-Daten der letzten 14 Tage.
- Geplante Events der kommenden 10 Tage.

## 2. Soll-Ist der letzten Woche

Vergleiche geplant gegen tatsächlich gelaufen:
- Wochenumfang, Long Run, Anzahl Qualitätseinheiten
- Was ist ausgefallen, und ist der Ausfall relevant?
- Wie waren die Schlüsseleinheiten wirklich — Pace gehalten, HF im Korridor,
  Drift über die Einheit?

Halte dich kurz. Eine Tabelle plus zwei bis drei Sätze Bewertung reichen.

## 3. Formlage

- CTL, ATL, TSB (= CTL − ATL) mit Zahlen nennen.
- CTL-Trend über die letzten 3–4 Wochen: aufgebaut, gehalten oder verloren?
- Ruhepuls gegen den Schnitt der Vorwochen.
- Auffälligkeiten bei RPE/Feel.

## 4. Revisionsauslöser prüfen

Gehe die Auslöser aus Abschnitt 4.3 deines Prompts durch und sage explizit, ob
einer greift. Wenn ja: Plan neu aufsetzen statt fortschreiben.

Prüfe zusätzlich, ob `Athletenstatus.md` noch stimmt:
- Ist ein Blockende oder ein Wettkampf dazwischen gewesen?
- Gibt es einen neuen, besseren Leistungsdatenpunkt als den dort eingetragenen?
- Liegt `naechste_revision` in der Vergangenheit?

Wenn die Datei aktualisiert gehört, sag was du ändern willst, und mach es dann.

## 5. Kommende Woche planen

Konkrete Einheiten mit Tag, Distanz/Dauer, Pace- und HF-Vorgabe. Beachte dabei:
Dienstag bleibt Intervalltag, Intervallformat gegenüber den letzten Wochen
rotieren, mindestens eine Radeinheit, Umfang innerhalb dessen, was die
Umfangstoleranz im Status hergibt.

Frage nach, bevor du die Woche in den Intervals.icu-Kalender schreibst — außer
der Athlet hat im Zusatzkontext oben schon gesagt, dass er sie eingetragen
haben will.

## 6. Ein Satz zum Wichtigsten

Schließe mit dem einen Punkt, der diese Woche wirklich zählt. Nicht drei, einer.
