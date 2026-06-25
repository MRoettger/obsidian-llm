# 🐍 Python – Standardbibliothek

Wichtige Module und Helfer aus der Standardbibliothek. Teil von [[Python-Erkenntnisse]].

---

## collections
- **`defaultdict`:** erzeugt für fehlende Keys automatisch einen Default per Factory (`defaultdict(list)`), erspart Existenzprüfungen.
- **`Counter`:** Dict-Subtyp zum Zählen von Häufigkeiten; `Counter('aabbbc').most_common(1)` → `[('b', 3)]`.
- **`deque`:** doppelt verkettete Queue, O(1) an beiden Enden (`append`/`appendleft`/`pop`/`popleft`); optional `maxlen` für Ringpuffer.
- **`namedtuple`:** Tuple mit benannten Feldern (`Point = namedtuple('Point', 'x y')`), unveränderlich und speicherarm.

## functools
- **`lru_cache`:** memoisiert Rückgabewerte anhand der Argumente (Least-Recently-Used); `cache_info()`/`cache_clear()`.
- **`cache` vs. `lru_cache`:** `cache` (ab 3.9) = `lru_cache(maxsize=None)`, unbegrenzt und minimal schneller. `lru_cache(maxsize=N)` begrenzt die Größe. Argumente müssen hashbar sein, Funktion sollte rein sein. Faustregel: `cache` bei begrenztem Eingaberaum (Rekursion), `lru_cache(maxsize=...)` bei großem Eingaberaum/begrenztem Speicher.

## itertools
- **`chain`:** verkettet mehrere Iterables zu einem (Länge = Summe); `chain.from_iterable(...)` für Iterable von Iterables. Lazy.
- **`product`:** kartesisches Produkt / alle Kombinationen (Länge = Produkt der Längen), ersetzt verschachtelte Schleifen; `repeat=`-Parameter.
- **`permutations` / `combinations`:** Anordnungen (Reihenfolge zählt) bzw. Auswahlen (Reihenfolge egal, ohne Wiederholung).
- **`groupby`:** gruppiert **aufeinanderfolgende** gleiche Elemente — Daten vorher nach demselben Key sortieren, sonst mehrere Gruppen pro Wert.

## Dateien, Zeit, Daten
- **`pathlib.Path`:** objektorientierte, plattformunabhängige Pfade mit `/`-Operator (`Path('dir') / 'file.txt'`, `.read_text()`, `.exists()`), Vorteil gegenüber `os.path`.
- **`datetime`:** `strptime` parst aus String, `strftime` formatiert in String.
- **`json`:** `dumps` → String, `dump` → schreibt in Datei-Objekt; analog `loads`/`load` beim Lesen.

## Sonstiges
- **`enum.Enum`:** benannte konstante Werte (`class Color(Enum): RED = 1`), bessere Lesbarkeit/Typsicherheit als rohe Konstanten.
- **`logging` vs. `print`:** strukturiertes Logging mit Levels (DEBUG/INFO/WARNING/ERROR), konfigurierbaren Handlern/Formaten, pro Modul aktivierbar — `print` nur für Ad-hoc-Ausgaben.

---
## Erfasste Anki-Karten

| Anki-ID | Frage |
|---|---|
| 1781637717125 | `collections.defaultdict` |
| 1781637717126 | `functools.lru_cache` |
| 1781637990857 | `collections.Counter` |
| 1781637990858 | `collections.deque` |
| 1781637990859 | `namedtuple` |
| 1781637990860 | `pathlib.Path` vs. `os.path` |
| 1781637990861 | `datetime` parsen/formatieren |
| 1781637990862 | `json.dumps` vs. `json.dump` |
| 1781637990863 | `itertools.chain` |
| 1781637990864 | `itertools.groupby` |
| 1781637990865 | `product`/`permutations`/`combinations` |
| 1781637990866 | `enum.Enum` |
| 1781637990867 | `logging` vs. `print` |
| 1781592965867 | `lru_cache` vs. `cache` |
| 1781592965871 | `itertools.chain` vs. `product` |

---
*Stand: Juni 2026 | Quelle: Anki „Python::Fortgeschritten" (Tag: Standardbibliothek)*
