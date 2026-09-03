---
type: moc
tags: [laufen, uebersicht]
status: lebend
updated: 2026-08-26
---

# Laufen — Übersicht

Map of Content für alle Laufen-Notizen. Flache Ordnerstruktur, Filterung läuft über `type` und `tags` im Frontmatter statt über Unterordner — leichter für ein LLM zu durchsuchen als verschachtelte Ordner.

## Ziele & Status
- **[[Athletenstatus]]** — ⭐ maßgebliche Quelle für aktuellen Zustand: Zonen, LTHR, Zielpaces, Umfangstoleranz, aktives Ziel. Schlägt bei Widerspruch alle anderen Notizen.
- [[Laufziele]] — Saisonziele, aktueller Hauptfokus
- [[Herzfrequenzzonen]] — Zonen-Referenz aus dem Stufentest

## Pläne & Methodik
- [[Trainingsplan HM Sub-120 2026]] — aktiver 16-Wochen-Plan
- [[HM-Aufbau Forschungsgrundlagen 2026]] — wissenschaftliche Grundlage des Plans
- [[Trainingsmethoden Halbmarathon Marathon]] — Methodik-Referenz HM/Marathon
- [[Trainingsbausteine 5km]] — abgeschlossener 5-km-Fokus
- [[Trainingspräferenzen]] — persönliche Vorgaben, haben Vorrang vor Faustregeln

## Rennen & Tests
- [[Rennvorbereitung-Checkliste]] — Checkliste vor jedem Test/Rennen
- [[Renntag-Erkenntnisse]] — laufend gepflegte Fehler-Datenbank
- [[Wettkampf 2027-03-21 Venloop]] — HM-Zielrennen Sub-1:20, Startplatz gesichert

## Wochenberichte & Trainingslogs
- [[Wochenbericht 2026-06-18 bis 06-25]]
- [[Trainingslog 2026-07-02 Schwelle]] — Qualitätseinheit KW 27, Plan-Abgleich

## Analysen
- [[Umfangshistorie 2025-2026]] — 64 Wochen Wochenumfänge, Belastbarkeit und Konstanz

## Urlaub & Pausen
- [[Urlaub 2026-07-13 bis 07-19]] — Rennrad-Urlaub (KW 29), Plan-Anpassung KW 29–31

## Prinzip für neue Notizen
1. Immer Frontmatter mit `type`, `tags`, `status`, `updated` setzen.
2. Diese Index-Datei bei jeder neuen Notiz um einen Link ergänzen.
3. Keine neuen Unterordner anlegen — Auffindbarkeit läuft über Frontmatter + Links, nicht über Ordnertiefe.

## Hinweis zur Aktualität

Notizen in diesem Ordner altern unterschiedlich schnell. [[Athletenstatus]] wird laufend gepflegt und gilt bei Widersprüchen. Planungsdokumente wie [[Trainingsplan HM Sub-120 2026]] halten den Stand ihrer Erstellung fest — sie werden nicht rückwirkend korrigiert, sondern durch den Athletenstatus überschrieben.

Der Laufcoach-Agent (`.opencode/agent/laufcoach.md`) liest den Athletenstatus zu Beginn jeder Session. Der Befehl `/wochencheck` fährt den wöchentlichen Soll-Ist-Abgleich und aktualisiert den Status bei Bedarf.
