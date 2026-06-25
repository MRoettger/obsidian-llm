# 🐍 Python – Syntax und Datentypen

Kernaussagen zu Sprachgrundlagen, Datentypen und idiomatischer Syntax. Teil von [[Python-Erkenntnisse]].

---

## Datentypen & Hashbarkeit
- **list vs. tuple:** `tuple` ist unveränderlich und (bei hashbaren Elementen) hashbar → als Dict-Key/Set-Element nutzbar. `list` ist veränderlich und damit nicht hashbar.
- **Falsy-Werte:** `None`, `False`, numerische Null (`0`, `0.0`, `0j`), leere Sammlungen (`''`, `[]`, `()`, `{}`, `set()`) sowie Objekte, deren `__bool__`/`__len__` das signalisiert.
- **Float-Vergleich:** `0.1 + 0.2 == 0.3` kann `False` sein (IEEE-754, Dezimalbrüche nicht exakt darstellbar). Stattdessen `math.isclose()` oder `decimal.Decimal`.

## Slicing & Unpacking
- **`a[::-1]`** liefert eine umgekehrte Kopie (dritter Slice-Wert = Schrittweite, `-1` läuft rückwärts).
- **Erweitertes Unpacking** mit `*`: `a, *rest = [1,2,3,4]` → `a=1, rest=[2,3,4]`; `first, *mid, last = range(5)`. Der gestirnte Name sammelt die übrigen Elemente als Liste.
- **`zip(*matrix)`** transponiert (Zeilen → Spalten): `[[1,2,3],[4,5,6]]` → `[(1,4),(2,5),(3,6)]`.

## Comprehensions & Generatoren
- **List Comprehension** `[x for x in it]` baut die ganze Liste sofort im Speicher; **Generator-Ausdruck** `(x for x in it)` ist lazy. Generator ist **einmalig** (nach Durchlauf erschöpft). Generator für große/einmalige Streams, Liste für Indizierung/`len()`/Mehrfachzugriff.
- **Set- vs. Dict-Comprehension:** `{x for x in it}` → Set; `{k: v for ...}` → Dict (Doppelpunkt macht den Unterschied).
- **Walrus `:=`** (ab 3.8): Zuweisungsausdruck, weist zu *und* liefert den Wert — nützlich in `while`-Schleifen und Comprehensions (teure Berechnung nur einmal). Sparsam einsetzen; nicht als ganze Top-Level-Anweisung erlaubt.

## Strings & Formatierung
- **f-strings** (`f"{x}"`) werten Ausdrücke inline zur Laufzeit aus, schneller/lesbarer. `str.format()` trennt Vorlage und Werte (gut für wiederverwendbare Templates).
- **`{x=}`** im f-string (ab 3.8): gibt Name **und** Wert aus (`x=42`), ideal fürs Debugging.

## Sets
- Mengenoperationen: Vereinigung `|`, Schnitt `&`, Differenz `-`, symmetrische Differenz `^` (auch als `.union()`, `.intersection()` usw.).

## Dicts
- **Gleichheit** ignoriert die Reihenfolge (gleiche Key-Value-Paare → gleich). Die **Einfügereihenfolge** bleibt seit 3.7 bei Iteration erhalten.

## Listen-Methoden & Sortierung
- **`append(x)`** fügt ein Element hinzu (Liste → verschachtelt); **`extend(it)`** hängt jedes Element einzeln an.
- **`sorted(it)`** gibt eine neue Liste zurück (jedes Iterable); **`list.sort()`** sortiert in-place und gibt `None` zurück.
- **Sortieren nach Schlüssel:** `key`-Parameter, z. B. `sorted(people, key=lambda p: p.age)`; stabil, `reverse=True` möglich.
- **`enumerate(it, start=1)`** liefert `(index, element)` ab Startwert.

## Identität & Kopien
- **`is` vs. `==`:** `==` vergleicht Werte (`__eq__`), `is` vergleicht Objekt-Identität. Für Singletons wie `None` immer `is` (`is None` korrekt/schneller; `== None` durch `__eq__` verfälschbar).
- **Veränderbarer Default** `def f(x=[])`: Default wird nur **einmal** bei Definition erzeugt und über alle Aufrufe geteilt → stattdessen `x=None; x = x or []`.
- **Shallow vs. Deep Copy:** Shallow (`copy.copy`, `x[:]`, `list(x)`) kopiert nur die äußere Struktur, verschachtelte Objekte bleiben geteilt; `copy.deepcopy` kopiert rekursiv (langsamer).

## Pattern Matching
- **`match/case`** (ab 3.10): Verzweigung anhand der Struktur von Werten, mit Destrukturierung, Guards und Klassenmustern.

---
## Erfasste Anki-Karten

| Anki-ID | Frage |
|---|---|
| 1781637717116 | list vs. tuple bzgl. Hashbarkeit |
| 1781637717118 | `*args` und `**kwargs` |
| 1781637717119 | Shallow Copy vs. Deep Copy |
| 1781637717120 | Generator-Ausdruck vs. List Comprehension |
| 1781637990825 | `a[::-1]` |
| 1781637990826 | Falsy-Werte |
| 1781637990827 | `str.format()` vs. f-strings |
| 1781637990828 | `{x=}` im f-string |
| 1781637990829 | Erweitertes Unpacking mit `*` |
| 1781637990830 | Set- vs. Dict-Comprehension |
| 1781637990831 | `0.1 + 0.2 == 0.3` |
| 1781637990832 | Mengenoperationen bei `set` |
| 1781637990833 | Dict-`==` und Key-Reihenfolge |
| 1781637990834 | `is None` vs. `== None` |
| 1781637990835 | `enumerate(it, start=1)` |
| 1781637990836 | `append()` vs. `extend()` |
| 1781637990837 | `zip(*matrix)` |
| 1781637990838 | Structural Pattern Matching |
| 1781637990839 | `sorted()` vs. `list.sort()` |
| 1781637990840 | Sortieren nach Schlüssel |
| 1781592965843 | `is` vs. `==` |
| 1781592965845 | Veränderbarer Default-Wert |
| 1781592965865 | Walrus-Operator `:=` |

---
*Stand: Juni 2026 | Quelle: Anki „Python::Fortgeschritten" (Tags: Syntax-Datentypen, Sprach-Grundlagen)*
