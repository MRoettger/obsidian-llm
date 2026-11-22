---
name: buecher
description: Legt Bücher im Obsidian-Vault an (llm-knowledge/Books/Buchliste) und pflegt ihren Status — neues Buch auf die Leseliste setzen, Buch als gelesen markieren. Ergänzt Autor, Erscheinungsjahr und ISBN per Websuche nur mit belegten Fakten, prüft vorher auf Duplikate und hält das feste Frontmatter-Schema ein. Use when der Nutzer sagt "füge das Buch X hinzu", "setz X auf die Leseliste", "neues Buch", "ich will X lesen", "habe X gelesen", "X ist ausgelesen", "markiere X als gelesen". NICHT für Zusammenfassungen oder Rezensionen erfinden und nicht für Notizen außerhalb von Books/.
---

# Bücher im Vault pflegen

Pro Buch eine Notiz in `llm-knowledge/Books/Buchliste/`. Die Übersicht
`llm-knowledge/Books/Bücherübersicht.md` ist reines Dataview und wird **nicht** von Hand
gepflegt — sie zieht sich alles aus dem Frontmatter. Diese Skill ändert sie nie.

Zwei Aufgaben: **Buch anlegen** und **Buch als gelesen markieren.** Es gibt bewusst nur
zwei Status, keine Bewertung und kein "lesend".

## Schema

```yaml
---
type: book
autor: Vorname Nachname
status: ungelesen        # ungelesen | gelesen
gelesen:                 # YYYY-MM-DD, nur bei status: gelesen
erscheinungsjahr:        # Jahr der Erstveröffentlichung des Originals
isbn:                    # ISBN-13 mit Bindestrichen, nur wenn Ausgabe bekannt
hinzugefügt: 2026-11-22  # Tag, an dem die Notiz angelegt wurde
tags: [buch, dystopie]
---
```

Regeln, die Dataview und Obsidian-Properties stabil halten:

- Alle Schlüssel stehen immer im Frontmatter, auch wenn der Wert leer ist.
- Schlüssel durchgehend **kleingeschrieben** (`autor`, nicht `Autor`).
- Datumsfelder immer `YYYY-MM-DD`, nie in Anführungszeichen.
- `status: gelesen` verlangt ein `gelesen`-Datum. `status: ungelesen` lässt es leer.
- `tags`: immer `buch` plus **höchstens zwei** Genre-Tags, klein und ohne Leerzeichen
  (`dystopie`, `science-fiction`, `sachbuch`, `gesellschaft`, `satire`, `krimi`,
  `thriller`, `fantasy`, `roman`, `biografie`, `alternativgeschichte`). Vor einem neuen
  Genre-Tag erst prüfen, ob ein vorhandener passt:
  `grep -rh "^tags:" llm-knowledge/Books/Buchliste`.

## Aufgabe A — Buch anlegen

### 1. Datum
Aktuelles Datum über das time-MCP holen. `hinzugefügt` ist **heute**, nicht das Datum
aus dem Gedächtnis.

### 2. Duplikate prüfen — vor jeder Recherche
1. `glob` auf `llm-knowledge/Books/Buchliste/*.md` und gegen den Titel abgleichen,
   ohne Groß-/Kleinschreibung und ohne Bindestriche/Untertitel.
2. `grep` auf `autor:` desselben Autors. Gleicher Autor mit anderem Dateinamen kann
   dasselbe Buch unter anderem Titel sein (deutscher Titel vs. Originaltitel, Figurenname
   statt Buchtitel).

Gibt es einen Treffer: **nicht** anlegen. Den Treffer nennen und fragen, ob es dasselbe
Buch ist. Ist es dasselbe, geht es höchstens um Aufgabe B.

### 3. Fakten per Websuche ergänzen
Nutze `web_search_exa` über `execute` (`tools.exa.web_search_exa`). Der Parameter
`objective` ist Pflicht; ohne ihn schlägt der Aufruf fehl. Suche gezielt nach
Verlags-, DNB- oder Wikipedia-Seiten, nicht nach Shops.

Gesucht wird **nur**:

| Feld | Quelle und Regel |
|---|---|
| exakter Titel, Autor | Schreibweise der Verlagsseite (z. B. *Marc-Uwe*, nicht *Mark-Uwe*) |
| `erscheinungsjahr` | Jahr der **Erstveröffentlichung des Originals**, nicht der deutschen Ausgabe |
| `isbn` | ISBN-13 **der Ausgabe, die der Nutzer nennt.** Nennt er keine und gibt es mehrere deutsche Ausgaben (Hardcover, Taschenbuch, Sondereditionen): **leer lassen** |
| Genre-Tags | aus dem festen Vokabular oben |

Keine Inhaltsangabe, kein Klappentext, keine Bewertung — auch nicht "als Quelle markiert".
Der Body bleibt leer, außer der Nutzer liefert selbst Text.

ISBN-13 vor dem Eintragen auf die Prüfziffer testen: Ziffern abwechselnd mit 1 und 3
gewichten, die Summe muss durch 10 teilbar sein. Besteht sie nicht, ist die ISBN falsch
abgeschrieben: neu suchen oder leer lassen.

Widersprechen sich Quellen beim Jahr, oder findet sich nichts Belastbares: Feld **leer
lassen** und im Ergebnis sagen, dass es offen ist. Ein falsches Jahr ist schlechter als
ein leeres.

### 4. Datei schreiben
Pfad: `llm-knowledge/Books/Buchliste/<Titel>.md`

- Dateiname = Titel, wie der Nutzer das Buch nennt, sonst der deutsche Titel. Ohne
  Untertitel. Verbotene Zeichen `\ / : * ? " < > |` durch ` - ` ersetzen oder entfernen.
- Frontmatter nach Schema, `status: ungelesen`, `gelesen` leer.
- Nach dem Frontmatter bleibt der Body leer. Hat der Nutzer etwas dazu gesagt
  ("empfohlen von Anna", "wegen der Serie"), kommt das **wörtlich** als normaler Absatz
  in den Body.

### 5. Rückmeldung
Eine kurze Zusammenfassung: Dateiname, was eingetragen wurde, **was leer geblieben ist
und warum** (z. B. "ISBN leer, weil mehrere deutsche Ausgaben — nenn mir die Ausgabe,
dann trage ich sie nach").

## Aufgabe B — Buch als gelesen markieren

1. Datei per `glob` suchen. Nicht gefunden: nachfragen, ob das Buch erst angelegt
   werden soll (Aufgabe A), und nicht still anlegen.
2. Datum: Nennt der Nutzer eins ("gestern", "im Mai"), das nehmen und auf einen Tag
   auflösen — bei "im Mai" den 1. des Monats. Sonst heute, aus dem time-MCP.
3. Im Frontmatter `status: gelesen` und `gelesen: YYYY-MM-DD` setzen. Alles andere und
   den Body **unangetastet** lassen.
4. Ist das Buch schon `gelesen`: Datum nicht überschreiben, sondern nachfragen.

## Was diese Skill nicht tut

- Keine Inhaltsangaben, Rezensionen oder Zitate erfinden oder aus dem Web übernehmen.
- Bestehende Notizen nicht umbenennen, umformatieren oder inhaltlich verbessern.
- `Bücherübersicht.md` nicht anfassen.
- Keine Dateien außerhalb von `llm-knowledge/Books/` ändern.
