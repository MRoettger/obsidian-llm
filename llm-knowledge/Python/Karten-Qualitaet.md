---
type: meta
tags: [python, anki, kartenqualitaet]
status: stabil
updated: 2026-06-28
---

# 🟥 Karten-Qualität — was gute Python-Karten unterscheidet

Abgeleitet aus dem Vergleich der **rot markierten** (überarbeitungsbedürftigen) Karten gegen die bewährten Karten im Deck **Python::Fortgeschritten**. Diese Notiz hält fest, *warum* die roten Karten markiert wurden, damit künftige Karten von Anfang an besser entstehen.

---

## Beobachtetes Muster

Die rot markierten Karten waren durchweg **knapp und einzeilig**: eine korrekte, aber minimale Antwort ohne Beispiel, Kontext oder Abgrenzung. Die bewährten Karten (z. B. MRO, `__new__`/`__init__`, `heapq`, Walrus-Operator, `lru_cache`) folgen dagegen einem reichhaltigeren, einheitlichen Aufbau.

### Die markierten Karten waren
- `def f(x=[])` — Default-Werte (nur 2 Zeilen Erklärung, knappes Snippet)
- `@staticmethod` / `@classmethod` / Instanzmethode (reine Definitionsabgrenzung, kein Beispiel)
- Erweitertes Unpacking mit `*` (nur zwei Mini-Snippets, kein Kontext)

---

## Qualitätskriterien für gute Karten

Eine starke Karte in diesem Deck enthält idealerweise:

1. **Kernaussage zuerst** — ein bis zwei Sätze, die die Frage direkt beantworten, Schlüsselbegriffe **fett**.
2. **Lauffähiges Codebeispiel** in `<pre><code>…</code></pre>` — mit Kommentaren, die das *Ergebnis* zeigen (z. B. `# [1, 1]  ← überrascht!`).
3. **„Warum“-Erklärung** — der zugrunde liegende Mechanismus, nicht nur das „Was“ (z. B. Default ist an `f.__defaults__` gebunden).
4. **Fallstricke / Voraussetzungen** — typische Fehler, Randfälle, Bedingungen (z. B. Argumente müssen hashbar sein; `x = x or []` ersetzt auch gültige leere Werte).
5. **Abgrenzung zu Verwandtem** — Bezug zu ähnlichen Konzepten (z. B. `*args` → Tuple vs. Unpacking → Liste).
6. **Faustregel / Merksatz** zum Schluss — eine knappe Entscheidungshilfe, *wann* man was nutzt.

Nicht jede Karte braucht alle sechs Punkte, aber eine reine Definition ohne Beispiel + Faustregel ist ein Markierungs-Kandidat.

---

## Checkliste vor dem Anlegen / nach dem Markieren

- [ ] Gibt es ein konkretes, lauffähiges Beispiel mit sichtbarem Ergebnis?
- [ ] Wird das *Warum* erklärt, nicht nur das *Was*?
- [ ] Ist mindestens ein Fallstrick oder eine Voraussetzung genannt?
- [ ] Gibt es eine Faustregel/Abgrenzung am Ende?
- [ ] Schlüsselbegriffe **fett**, Code in `<code>`/`<pre>`?

---

*Stand: Juni 2026 | Quelle: rote Flaggen (flag:1) im Deck „Python::Fortgeschritten“ — 3 Karten überarbeitet*
