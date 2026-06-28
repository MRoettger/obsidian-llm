---
type: wissen
tags: [python, datenstrukturen, komplexitaet]
status: stabil
updated: 2026-06-28
---

# 🐍 Python – Datenstrukturen und Komplexität

Spezialisierte Datenstrukturen und Laufzeitverhalten. Teil von [[Python-Erkenntnisse]].

---

## heapq
- **`heapq`** implementiert einen Min-Heap direkt auf einer Liste; das kleinste Element steht immer an Index 0.
- Operationen: `heappush`/`heappop` **O(log n)**, `heapify` **O(n)**, Minimum-Zugriff `h[0]` **O(1)**.
- **Max-Heap** durch Negieren der Werte (`heappush(h, -wert)`, `-heappop(h)`).
- Helfer: `nlargest(k, it)` / `nsmallest(k, it)`, `heappushpop`, `heapreplace`, `heapq.merge`.
- Anwendung: Priority Queue, Dijkstra, Top-k-Probleme, Merge sortierter Streams.

## Membership-Komplexität
- **`in` bei `list`:** O(n) lineare Suche. **`in` bei `set`:** O(1) amortisiert via Hashing. Für Membership-Tests immer `set` bevorzugen.

---
## Erfasste Anki-Karten

| Anki-ID | Frage |
|---|---|
| 1781592965859 | `heapq` und Komplexität |
| 1781592965861 | `in` bei list vs. set |

---
*Stand: Juni 2026 | Quelle: Anki „Python::Fortgeschritten" (Tag: Datenstrukturen)*
