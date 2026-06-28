---
type: wissen
tags: [python, numpy, pandas, data-science]
status: stabil
updated: 2026-06-28
---

# 🐍 Python – Data Science (numpy und pandas)

Kernkonzepte zu numpy und pandas. Teil von [[Python-Erkenntnisse]].

---

## Indizierung (pandas)
- **`loc` vs. `iloc`:** `loc` ist label-basiert (Namen), `iloc` positions-basiert (Integer ab 0). Beim Slicing ist `loc` am Ende **inklusiv**, `iloc` **exklusiv**. Schreibender Zugriff immer über `df.loc[maske, spalte] = ...`.
- **SettingWithCopyWarning:** entsteht durch chained indexing (`df[mask]['spalte'] = ...`), weil unklar ist, ob auf Kopie oder Original geschrieben wird. Korrekt: ein einziger `.loc`-Zugriff; oder bewusst `.copy()`. Niemals `df[...][...] = ...`.

## Funktionen anwenden (pandas)
- **`map` / `apply` / `applymap`:** `Series.map` elementweise (auch Dict-Mapping); `DataFrame.apply` zeilen-/spaltenweise (`axis`); `applymap`/`DataFrame.map` elementweise auf jeden Wert (`applymap` ab pandas 2.1 veraltet → `df.map`). Wo möglich vektorisiert statt `apply` arbeiten.

## numpy
- **Vektorisierung:** schneller als Python-Schleifen, weil Operationen in vorkompiliertem C-Code über ganze Arrays laufen — kein Interpreter-Overhead pro Element, cache-effiziente kontinuierliche Speicherblöcke.
- **Views vs. Kopien:** einfaches Slicing (`a[i:j]`) erzeugt einen **View** (teilt Speicher, Änderungen wirken auf beide); Fancy-Indexing (Listen/Boolean-Masken) und `.copy()` erzeugen eine **Kopie**. Prüfen mit `b.base is a`. Im Zweifel `.copy()`.

---
## Erfasste Anki-Karten

| Anki-ID | Frage |
|---|---|
| 1781592965883 | `df.loc` vs. `df.iloc` |
| 1781592965885 | Vektorisierung schneller als Schleife |
| 1781592965887 | `apply` / `map` / `applymap` |
| 1781592965889 | SettingWithCopyWarning |
| 1781592965891 | numpy Views vs. Kopien |

---
*Stand: Juni 2026 | Quelle: Anki „Python::Fortgeschritten" (Tag: DataScience)*
