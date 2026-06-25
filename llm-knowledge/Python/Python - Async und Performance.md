# 🐍 Python – Async und Performance

Nebenläufigkeit, Parallelität, der GIL und Performance-Messung. Teil von [[Python-Erkenntnisse]].

---

## Grundbegriffe
- **Concurrency vs. Parallelism:** Concurrency = mehrere Aufgaben machen Fortschritt (verschachtelt, evtl. ein Kern); Parallelism = Aufgaben laufen gleichzeitig auf mehreren Kernen. `asyncio` = Concurrency, `multiprocessing` = Parallelism.
- **GIL (Global Interpreter Lock):** Lock in CPython, lässt pro Prozess nur **einen** Thread Python-Bytecode ausführen → reine Python-Rechenarbeit läuft mit Threads nicht echt parallel. I/O-gebunden → Threads (GIL wird beim Warten freigegeben); CPU-gebunden → Prozesse. NumPy gibt den GIL in C-Routinen frei. Ab 3.13 experimenteller free-threading-Build.

## asyncio
- **`async def`** definiert eine Coroutine; der Aufruf führt den Körper **nicht** aus, sondern liefert ein Coroutine-Objekt für die Event-Loop. Kein Multithreading — kooperativ in einem Thread.
- **`await`** pausiert die Coroutine bis das Awaitable fertig ist und gibt die Kontrolle an die Event-Loop zurück.
- **Mehrere Coroutinen nebenläufig:** `await asyncio.gather(coro1(), coro2(), ...)` startet sie zusammen und sammelt die Ergebnisse.
- **`gather` vs. `wait`:** `gather` liefert Ergebnisse in Input-Reihenfolge und reicht Exceptions direkt durch (`return_exceptions=True` zum Einsammeln). `wait` gibt zwei Sets (`done`, `pending`) zurück, erlaubt Timeouts und „sobald einer fertig"-Logik, propagiert Exceptions nicht automatisch (`t.result()` auslesen). Ab 3.11 oft `asyncio.TaskGroup` bevorzugen.

## Threads vs. Prozesse
- **`ThreadPoolExecutor`** für I/O-gebundene Arbeit (warten auf Netzwerk/Datei), **`ProcessPoolExecutor`** für CPU-gebundene Arbeit (umgeht den GIL, echte Parallelität). Faustregel: Warten → Threads/async; Rechnen → Prozesse.

## Performance messen
- **`timeit`:** misst kleine Schnipsel zuverlässig durch vielfache Ausführung (`timeit.timeit('sum(range(100))', number=10000)`).
- **`cProfile`:** Profiler für Aufrufzahlen und Zeit pro Funktion (`python -m cProfile -s cumtime script.py`). Erst messen, dann optimieren.

---
## Erfasste Anki-Karten

| Anki-ID | Frage |
|---|---|
| 1781637990868 | Concurrency vs. Parallelism |
| 1781637990869 | GIL |
| 1781637990870 | `async def` vs. normale Funktion |
| 1781637990871 | `await` |
| 1781637990872 | Coroutinen nebenläufig ausführen |
| 1781637990873 | ThreadPool vs. ProcessPool |
| 1781637990874 | Laufzeit messen (`timeit`) |
| 1781637990875 | Engpässe finden (`cProfile`) |
| 1781592965875 | `asyncio.gather` vs. `asyncio.wait` |

---
*Stand: Juni 2026 | Quelle: Anki „Python::Fortgeschritten" (Tags: Async-Performance, Async)*
