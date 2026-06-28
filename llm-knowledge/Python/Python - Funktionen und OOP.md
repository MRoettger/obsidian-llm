---
type: wissen
tags: [python, funktionen, oop]
status: stabil
updated: 2026-06-28
---

# 🐍 Python – Funktionen und OOP

Funktionen höherer Ordnung, Closures und objektorientierte Konzepte inklusive Dunder-Methoden. Teil von [[Python-Erkenntnisse]].

---

## Funktionen
- **`*args` / `**kwargs`:** `*args` sammelt überzählige positionale Argumente als Tuple, `**kwargs` überzählige Schlüsselwort-Argumente als Dict.
- **Closure:** innere Funktion, die Variablen des umschließenden Scopes einfängt und über dessen Ende hinaus behält. Fängt die **Variable**, nicht den Wert → Late-Binding-Falle in Schleifen (`lambda i=i: i` zur Wert-Bindung). Schreibzugriff auf eingefangene Variablen via `nonlocal`.
- **Decorator:** Funktion, die eine Funktion entgegennimmt und eine neue zurückgibt (`@deco` == `f = deco(f)`). Decorator mit Argumenten braucht eine zusätzliche Ebene. Ohne `functools.wraps` verliert die dekorierte Funktion `__name__`/`__doc__`.
- **`functools.wraps`:** kopiert Metadaten der Originalfunktion auf den Wrapper.

## Methodentypen
- **Instanzmethode** erhält `self`, **`@classmethod`** erhält `cls` (gut für alternative Konstruktoren), **`@staticmethod`** erhält keinen impliziten ersten Parameter.
- **`@property`:** macht eine Methode wie ein Attribut abrufbar (ohne Klammern), erlaubt Getter/Setter mit Validierung ohne API-Änderung. Im Setter `self._x` verwenden (sonst Rekursion).

## Vererbung
- **MRO (Method Resolution Order):** feste Suchreihenfolge bei (Mehrfach-)Vererbung, per C3-Linearisierung; abfragbar via `Klasse.__mro__` / `Klasse.mro()`. Im Diamant kommt die gemeinsame Basis zuletzt.
- **`super()`** ruft die nächste Klasse in der MRO auf (nicht zwingend die direkte Elternklasse) → kooperative Mehrfachvererbung, jede Klasse genau einmal.
- **Komposition vs. Vererbung:** Vererbung = „ist-ein", Komposition = „hat-ein" (oft bevorzugt wegen lockerer Kopplung).
- **Abstrakte Basisklasse:** `from abc import ABC, abstractmethod`; Instanziierung schlägt fehl, solange nicht alle abstrakten Methoden überschrieben sind.

## Objekterzeugung & Datenklassen
- **`__new__` vs. `__init__`:** `__new__` erstellt und liefert die Instanz (vor `__init__`), `__init__` initialisiert sie. `__new__` nur bei Singletons, Subklassen unveränderlicher Typen oder Metaclass-Tricks; muss die Instanz zurückgeben.
- **`@dataclass`:** generiert `__init__`/`__repr__`/`__eq__` aus Annotationen; Optionen `frozen=True` (unveränderlich + hashbar), `order=True`. Veränderbare Defaults via `field(default_factory=list)`.
- **`__slots__`:** feste Attributmenge statt `__dict__` pro Instanz → Speicherersparnis und schnellerer Zugriff; verhindert dynamische Attribute. Unterklasse ohne eigenes `__slots__` bekommt wieder ein `__dict__`.

## Dunder-Methoden (Protokolle)
- **`__repr__` vs. `__str__`:** `__repr__` eindeutig/entwicklerorientiert (Konsolen-Fallback), `__str__` lesbar für Endnutzer (`print`/`str`).
- **`__eq__` & `__hash__`:** gleiche Objekte müssen gleichen Hash haben. Überschreibt man `__eq__`, wird `__hash__` standardmäßig `None` (Objekt unhashbar).
- **`__call__`:** macht eine Instanz aufrufbar wie eine Funktion (Funktor mit inspizierbarem Zustand). `callable(obj)` prüft das.
- **Iterierbarkeit:** `__iter__` (gibt Iterator zurück) bzw. Iterator-Protokoll `__iter__` + `__next__` (löst `StopIteration` aus).
- **Context-Manager:** `__enter__` liefert die Ressource, `__exit__` räumt auf (auch bei Exceptions). Kompakt via `@contextlib.contextmanager` + `yield` (davor Setup, danach Cleanup).
- **Deskriptor:** Objekt mit `__get__`/`__set__`/`__delete__`, steuert Attributzugriff auf Klassenebene; Grundlage von `property`, Methoden, `classmethod`. Data-Deskriptor (`__set__`/`__delete__`) hat Vorrang vor Instanz-`__dict__`; wiederverwendbar über viele Attribute.
- **Metaclass:** „Klasse einer Klasse", steuert Klassenerzeugung; Standard `type`, eigene via `metaclass=`.

## Generatoren
- **`yield`:** Funktion produziert Werte lazy und behält Zustand zwischen Aufrufen; liefert ein Generator-Objekt (Iterator-Protokoll).
- **`yield from`:** delegiert an einen Sub-Generator und reicht dessen Werte durch.

---
## Erfasste Anki-Karten

| Anki-ID | Frage |
|---|---|
| 1781637717121 | Decorator (Grundprinzip) |
| 1781637717122 | staticmethod/classmethod/Instanzmethode |
| 1781637717123 | `__enter__` / `__exit__` |
| 1781637717124 | `@property` |
| 1781637990841 | Closure |
| 1781637990842 | `functools.wraps` |
| 1781637990843 | `__slots__` |
| 1781637990844 | `__repr__` vs. `__str__` |
| 1781637990845 | Objekt iterierbar machen |
| 1781637990846 | Deskriptor |
| 1781637990847 | `@dataclass` |
| 1781637990848 | Abstrakte Basisklasse |
| 1781637990849 | `super()` |
| 1781637990850 | Komposition vs. Vererbung |
| 1781637990851 | `__call__` |
| 1781637990852 | `__eq__` vs. `__hash__` |
| 1781637990853 | Context Manager via `contextlib` |
| 1781637990854 | Generator mit `yield` |
| 1781637990855 | `yield from` |
| 1781637990856 | Metaclass |
| 1781592965851 | MRO |
| 1781592965853 | `__new__` vs. `__init__` |

---
*Stand: Juni 2026 | Quelle: Anki „Python::Fortgeschritten" (Tags: Funktionen-OOP, OOP)*
