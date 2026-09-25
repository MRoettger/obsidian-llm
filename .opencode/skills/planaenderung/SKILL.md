---
name: planaenderung
description: Entscheidet, wie eine geplante Trainingswoche umgebaut wird, wenn sich die Realität ändert — Termin kommt dazwischen, ein Tag fällt weg, der Athlet will tauschen, eine Alternativsportart anbieten oder eine Einheit vorziehen. Wägt den kurzfristigen Umbau gegen Umfangsrampe, Wettkampfziele und den strukturellen Befund ab und benennt die Kosten. Use when der Athlet sagt "ich muss morgen X", "kann ich die Einheit verschieben", "was passiert wenn ich Donnerstag nicht kann", "ich fahre stattdessen Rad", "kann ich Y auf dem Rad machen", "wie verändert sich die Woche wenn". NICHT für die reguläre Wochenplanung ohne Störung und nicht für die Analyse einer gelaufenen Einheit — dafür sind /wochencheck und /tagesanalyse zuständig.
---

# Planänderung unter Randbedingungen

Der Athlet meldet eine Einschränkung oder einen Wunsch, und die geplante Woche geht so
nicht mehr auf. Diese Skill entscheidet, **was bleibt, was weicht und was das kostet.**

Abgrenzung: `/wochencheck` plant eine Woche ohne Störung. `/tagesanalyse` bewertet
eine gelaufene Einheit. Hier geht es um den Umbau eines bestehenden Plans gegen eine
neue Randbedingung — und um die Frage, ob der Umbau das Saisonziel beschädigt.

Keine Zonen, LTHR-Werte, Zielpaces oder Umfangsstufen in dieser Datei. Die stehen in
`llm-knowledge/Laufen/Athletenstatus.md` und werden dort gelesen. Steht ein Wert in
beiden, gilt die Statusdatei.

**Rechne nicht im Kopf.** `scripts/laufcoach.py` hat die Formeln, verifiziert gegen
echte Intervals.icu-Werte:

```
python3 scripts/laufcoach.py tsb --ctl <ctl> --atl <atl>
python3 scripts/laufcoach.py ctl --ctl <ctl> --atl <atl> --weeks 50,58,64,48
python3 scripts/laufcoach.py race --temp <°C> --ctl <x> --atl <y> --bike-km-3d <km>
python3 scripts/laufcoach.py intervals --vdot <v> --reps 1200,1000,800,600,400
python3 scripts/laufcoach.py status
```

Gib im Ergebnis die Zahl an, nicht den Aufruf.

## 1. Daten holen — in dieser Reihenfolge

1. Aktuelles Datum über das time-MCP. Ohne korrektes Datum ist jede Wochenlogik falsch.
2. `llm-knowledge/Laufen/Athletenstatus.md` — Zonen, aktives Ziel, **Umfangsrampe**,
   Abbruch- und Freigabekriterien, Regeln für Nebensportarten und Kraft.
3. `get_activities` letzte 14–21 Tage — was ist real passiert, wann war der letzte
   harte Reiz, wie viel Umfang steht schon in der laufenden Woche.
4. `get_wellness_data` letzte 14 Tage — CTL-Verlauf, ATL, Ruhepuls, Schlaf.
5. `get_events` von heute bis Ende der Folgewoche — was steht im Plan, mit welchen
   IDs, und was ist die Absicht hinter jeder Einheit (die Beschreibungen lesen, dort
   steht meist schon, was bei Zweifeln zuerst gestrichen wird).
6. `laufcoach.py status` — Snapshot-Frische und Countdown zum nächsten Wettkampf.

Fehlt eine Quelle oder ist der Snapshot älter als acht Wochen: benennen, nicht
überspielen.

## 2. Die Randbedingung sauber fassen

Bevor gerechnet wird, muss klar sein, **was genau feststeht**. Der häufigste Fehler
ist, eine Möglichkeit als Zwang zu behandeln oder umgekehrt.

Unterscheide drei Sorten:

| Sorte | Beispiel | Umgang |
|---|---|---|
| **Harte Randbedingung** | "ich muss morgen Rad fahren", "Donnerstag bin ich weg" | nicht verhandelbar, Plan baut sich drumherum |
| **Angebot** | "ich kann auch VO2max auf dem Rad machen" | **Option, keine Vorgabe.** Prüfen und begründet annehmen oder ablehnen |
| **Wunsch** | "kann ich den Long Run vorziehen" | gegen die Trainingslogik prüfen, nicht automatisch erfüllen |

Ein Angebot des Athleten abzulehnen ist ausdrücklich erlaubt und oft richtig. Wenn er
mehr Intensität anbietet, als die Woche verträgt, ist "nein, und hier ist der Grund"
die Coach-Antwort. Sag dann aber, **unter welcher Bedingung das Angebot richtig wäre**
— es ist meist nicht falsch, nur falsch platziert.

Ist die Randbedingung mehrdeutig, triff die konservativere Annahme und sag sie an.
Nicht rückfragen, wenn eine vertretbare Annahme möglich ist.

## 3. Schutzhierarchie — was zuerst geschützt wird

Das ist der Kern. Wenn die Woche nicht mehr aufgeht, wird **von oben nach unten**
geschützt und **von unten nach oben** geopfert. Die Reihenfolge folgt aus dem
Athletenstatus, nicht aus allgemeinen Faustregeln:

1. **Gewebeschutz.** Abbruchkriterien aus dem Status (Schmerz an Schienbein, Ferse,
   Mittelfuß; auffälliger Ruhepuls). Überschreibt alles, auch ein Wettkampfziel.
2. **Wettkampf-Must-Haves**, wenn ein Rennen innerhalb von 3 Tagen liegt. Mit
   `laufcoach.py race` prüfen, nicht aus dem Gedächtnis.
3. **Long Run.** Der strukturelle Reiz. Das gemessene Limit des Athleten ist
   muskulär-strukturell, nicht kardiovaskulär — der Long Run adressiert es direkt und
   ist durch nichts ersetzbar, schon gar nicht durch Radfahren.
4. **Die laufspezifische Qualitätseinheit** (Intervalltag). Verschieben ja, streichen
   nur im Notfall. Referenzeinheiten mit festen Zielzeiten werden **inhaltlich nicht
   angetastet**, sonst verlieren sie ihren Zweck als Vergleichsmaßstab.
5. **Wochenumfang auf der Rampenstufe.** Die Stufe ist eine Entscheidung, keine
   Empfehlung. Sie wird über die lockeren Tage gehalten, nicht über Intensität.
6. **Zweite harte Einheit (Schwelle).** Als Erstes im Volumen kürzbar, Pace bleibt.
   Bei Gedränge die erste harte Einheit, die ganz fällt.
7. **Kraft.** Pflichtbestandteil, aber tagesflexibel — gehört auf die harten Tage,
   nie auf Regenerationstage.
8. **Lockere Läufe.** Füllmasse. Frei verlängerbar und kürzbar, um den Umfang zu
   treffen. Hier wird zuerst geschoben.
9. **Rad und andere Nebensportarten.** Ganz unten. Zusatz, nie Ersatz für einen
   Laufreiz.

Wenn du von dieser Reihenfolge abweichst, begründe die Abweichung explizit.

## 4. Die sechs Prüfungen am Umbau

Arbeite alle sechs ab, bevor du den neuen Plan ausgibst.

### A. Abstand zwischen harten Einheiten

Zwei Qualitätseinheiten brauchen mindestens 48 h Abstand, sonst entwertet die erste
die zweite. Rücken sie enger, entscheide dich: eine davon wird im **Volumen** gekürzt,
nicht in der Intensität. Eine Schwelleneinheit mit reduzierter Pace ist keine
Schwelleneinheit mehr, sondern ein zäher Tempolauf ohne Reiz.

Prüfe außerdem den Abstand nach hinten: liegt eine harte Einheit direkt vor dem Long
Run, ist das nur bei moderater Long-Run-Distanz vertretbar — und dann als bewusster
Ermüdungsresistenz-Reiz zu benennen, nicht als Nebenwirkung.

### B. Cross-Training — was es leisten kann und was nicht

| Ersetzt | Radfahren | Urteil |
|---|---|---|
| lockerer Lauf | ja | impactfrei bei gleichem aerobem Reiz, ausdrücklich erlaubt |
| Umfangs-Füller für CTL | ja | funktioniert, aber baut nicht laufspezifisch auf |
| Schwelleneinheit | bedingt | aerober Reiz ja, laufspezifisch nein |
| VO2max-Laufintervalle | **nein** | trifft das System, das bei diesem Athleten nicht limitiert |
| Long Run | **nein** | kein struktureller Reiz, kein Impact, keine Anpassung |

Kernsatz für jede Cross-Training-Frage: **Radfahren baut aerob auf, aber nicht
strukturell — und strukturell ist die gemessene Schwachstelle.** Wer dem Athleten
Rad-VO2max statt Lauf-VO2max verkauft, trainiert am Limit vorbei.

Ausnahme, in der Rad-Intensität richtig ist: wenn in der Woche ohnehin **kein**
laufspezifischer Qualitätsreiz mehr möglich ist. Dann ist ein harter Radreiz besser
als gar keiner. Benenne das als Fallback, nicht als Plan A.

### C. Umfang gegen die Rampe

Rechne den neuen Wochenumfang aus und stell ihn der Rampenstufe aus dem Status
gegenüber. Fehlende Kilometer werden über die lockeren Tage nachgeholt, nicht über
einen längeren Long Run — der Aufbau läuft über Frequenz.

Liegt der neue Umfang deutlich unter der Stufe, sag, ob die Stufe damit als verfehlt
gilt und die nächste Woche wiederholt statt gesteigert wird. Eine übersprungene Stufe
ist teurer als eine wiederholte.

### D. Form und Verträglichkeit

TSB rechnen. Ruhepuls der letzten Tage gegen den Normalbereich. Schlaf, sofern erfasst.
Bei stark negativem TSB wird der Umbau konservativer, nicht kreativer.

Prüfe zusätzlich den **CTL-Trend über die letzten drei Wochen**. Fällt er ungeplant,
darf der Umbau ihn nicht weiter drücken — dann ist die Antwort auf "ich habe weniger
Zeit" nicht "dann lassen wir was weg", sondern "dann fällt die Qualität, nicht der
Umfang".

### E. Fernwirkung auf das Saisonziel

Der eigentliche Zweck dieser Skill. Eine einzelne umgebaute Woche ist fast nie
schädlich — schädlich ist das Muster. Prüfe:

- Wie viele Wochen sind es bis zum nächsten Prüfpunkt aus dem Status?
- Ist das dieselbe Störung wie in den Vorwochen? Fällt der Intervalltag zum wiederholten
  Mal, ist das kein Terminproblem mehr, sondern ein Strukturproblem — dann gehört der
  Intervalltag dauerhaft auf einen anderen Wochentag, statt ihn jede Woche zu schieben.
- Kostet der Umbau eine Schlüsseleinheit? Drei ausgefallene Schlüsseleinheiten in
  einem Block lösen eine sofortige Neubewertung aus.

Sag ausdrücklich, ob die Änderung folgenlos ist oder nicht. "Kosten dieser Umstellung:
keine nennenswerten" ist eine gültige und wertvolle Aussage — aber nur, wenn sie
geprüft wurde.

### F. Revisionsauslöser

Geh die Auslöser aus Abschnitt 4.3 des Coach-Prompts durch. Greift einer, sag es hier
und ungefragt, auch wenn nur nach dem Wochenumbau gefragt wurde. Ein Plan, dessen
Voraussetzungen nicht mehr gelten, wird neu aufgesetzt und nicht weiter umgebaut.

## 5. Ausgabeformat

```
## Lage
(3–5 Bulletpoints: CTL/ATL/TSB, Ruhepuls, Rampenstufe der Woche, letzter harter Reiz,
Tage bis zum nächsten Prüfpunkt. Nur Zahlen, keine Wertung.)

## Zur <konkreten Frage des Athleten>
(Wenn der Athlet eine Option angeboten hat: klare Annahme oder Ablehnung im ersten
Satz, dann die Begründung in nummerierten Punkten. Bei Ablehnung: unter welcher
Bedingung die Option richtig wäre.)

## Vorschlag für die Woche
| Tag | Neu | Statt |
(Vollständige Woche, auch die unveränderten Tage. Die Spalte "Statt" macht den Umbau
nachvollziehbar.)

Wochenumfang ≈ X km — Einordnung gegen die Rampenstufe.

(Darunter: die zwei bis drei Änderungen, die eine Begründung brauchen, jeweils mit
dem Grund. Nicht jede Verschiebung erklären, nur die nicht offensichtlichen.)

Kosten dieser Umstellung: <konkret, oder "keine nennenswerten">

## <Rückfrage zur Eintragung>
```

Danach fragen, ob eingetragen werden soll. Erst nach Bestätigung schreiben.

## 6. Eintragen in den Kalender

- **Bestehende Events an ihren Daten überschreiben**, nicht löschen und neu anlegen.
  Event-IDs aus `get_events` verwenden. Eine ganze Woche wird nie ungefragt gelöscht.
- Vor dem Schreiben ansagen, was passiert: welche IDs, welche Tage, dass nichts
  gelöscht wird.
- Jede Beschreibung erklärt das **Warum**, nicht nur das Was — inklusive dem Satz, was
  bei dieser Einheit im Zweifel zuerst gestrichen wird. Der Stil der vorhandenen
  Events ist die Vorlage.
- Wo eine Einheit gegenüber dem Original geändert wurde, gehört die Änderung **in die
  Beschreibung**: "von 3×10 auf 3×8 gekürzt, Pace unverändert, weil …". Der Athlet
  liest das Event am Trainingstag, nicht diesen Chat.
- Enthält der Umbau eine Abbruchregel, muss sie in **beiden** betroffenen Events
  stehen — in dem, wo beobachtet wird, und in dem, das ausfällt.
- Nach dem Schreiben mit `get_events` verifizieren und das Ergebnis als Tabelle
  zusammenfassen.
- **`Athletenstatus.md` wird bei einer Wochenumstellung nicht angefasst.** Eine
  verschobene Einheit ist kein neuer Athletenzustand. Nur wenn der Umbau eine
  dauerhafte Änderung bedeutet — Rampenstufe verfehlt, Wochenstruktur dauerhaft anders
  — gehört das in den Status, und dann mit Ansage plus Nachziehen des Snapshots in
  `scripts/laufcoach.py`.

## 7. Regeln

- **Erst Daten, dann Vorschlag.** Kein Umbau ohne abgerufene Wellness- und Eventdaten.
- **Die Kosten immer benennen.** Ein Umbau ohne Kostenaussage ist keine Entscheidung,
  sondern eine Umsortierung.
- **Intensität ist nicht die Stellschraube.** Wenn eine Woche eng wird, geht Volumen
  runter und Reihenfolge wird geändert — nicht die Zielpace.
- **Nicht zwei Probleme mit einer Einheit lösen.** Eine Einheit, die gleichzeitig
  Umfang, Qualität und Regeneration liefern soll, liefert nichts davon.
- **Mehr anbieten als gefragt, aber nicht mehr planen als nötig.** Wenn der Athlet nur
  nach Dienstag fragt, die Folgen für die restliche Woche trotzdem prüfen — aber die
  Woche nicht grundlos umbauen. Was funktioniert, bleibt stehen.
- **Eine Ablehnung ist eine vollständige Antwort.** Wenn der beste Umbau lautet "lass
  die Woche wie sie ist und verschiebe nur einen Tag", dann ist das das Ergebnis.
- Kein Schönreden. Wenn der Umbau eine Schlüsseleinheit kostet, steht das im Vorschlag
  und nicht im Kleingedruckten.
