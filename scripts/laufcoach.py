#!/usr/bin/env python3
"""
laufcoach.py — Rechenkern für die Laufcoach-Steuerung.

Zweck: Alle Zahlen, die der Coach sonst im Kopf oder im Fließtext überschlägt,
werden hier deterministisch und nachprüfbar berechnet. Keine Abhängigkeiten
außer der Standardbibliothek.

Verhältnis zu den anderen Ebenen (siehe Coach-Prompt):

  Methodik        -> Coach-Prompt        (stabil)
  Athletenzustand -> Athletenstatus.md   (Wochen)   <- Snapshot unten, MUSS gepflegt werden
  Tagesdaten      -> Intervals.icu live  (täglich)  <- wird als Argument übergeben

WICHTIG: Der ATHLET-Block unten ist ein *Snapshot* von Athletenstatus.md.
Die Statusdatei bleibt die maßgebliche Quelle. Wenn sich dort etwas ändert,
muss dieser Block nachgezogen werden. `check_status_freshness()` warnt, wenn
der Snapshot älter als acht Wochen ist oder von der Statusdatei abweicht.

Nutzung:
    python3 scripts/laufcoach.py --self-test
    python3 scripts/laufcoach.py riegel --from 27922.46 --time 2:02:21 --to 21097.5
    python3 scripts/laufcoach.py vdot --dist 27922.46 --time 2:02:21
    python3 scripts/laufcoach.py tsb --ctl 42.2 --atl 60.5
    python3 scripts/laufcoach.py ctl --ctl 42.2 --atl 60.5 --weeks 50,58,64,48
    python3 scripts/laufcoach.py race --temp 6 --ctl 55 --atl 45 --bike-km-3d 0
    python3 scripts/laufcoach.py splits --dist 21097.5 --target 1:20:00
    python3 scripts/laufcoach.py intervals --vdot 50.5 --reps 1200,1000,800,600,400
    python3 scripts/laufcoach.py zones
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable, Sequence

# =============================================================================
# 1. ATHLETENSTATUS — Snapshot aus llm-knowledge/Laufen/Athletenstatus.md
# =============================================================================

STATUS_UPDATED = date(2026, 9, 13)
STATUS_SOURCE = "llm-knowledge/Laufen/Athletenstatus.md"
STATUS_MAX_AGE_DAYS = 56  # acht Wochen, siehe Coach-Prompt


@dataclass(frozen=True)
class Zone:
    nr: int
    name: str
    hr_lo: int
    hr_hi: int
    pace_lo: int  # s/km, langsame Grenze (größere Zahl)
    pace_hi: int  # s/km, schnelle Grenze (kleinere Zahl)


# Quelle: Sportmedizinischer Stufentest, Juni 2026.
ZONES: tuple[Zone, ...] = (
    Zone(1, "Rekomposition", 132, 144, 397, 340),
    Zone(2, "Extensiv", 144, 152, 340, 298),
    Zone(3, "Intensiv", 152, 160, 298, 265),
    Zone(4, "Schwelle", 160, 166, 265, 238),
    Zone(5, "Supramaximal", 166, 173, 238, 216),
)

LTHR_RUN = 165          # maßgeblich (Sportmedizin). Intervals.icu führt 172 -> zu hoch.
LTHR_INTERVALS_ICU = 172
RHR_NORMAL = (44, 49)   # Normalkorridor
RHR_ALARM = 52          # > 1 Woche darüber -> Abbruchkriterium der Umfangsrampe
WEIGHT_KG = 74.0

# HF-Korrektur gegenüber Laufen
SPORT_HR_OFFSET = {"run": 0, "bike": -10, "walk": -5, "swim": -20}

# Zielrennen
GOAL_RACE = "Arrow Venloop HM"
GOAL_DATE = date(2027, 3, 21)
GOAL_TIME_S = 4800          # Sub-1:20:00
CHECK_RACE = "Advents-Aaseelauf 10 km"
CHECK_DATE = date(2026, 11, 29)
CHECK_ON_TRACK_S = 2310     # 38:30
CHECK_CORRECT_S = 2370      # 39:30 -> Zielzeit auf 1:23-1:24 korrigieren

HM_M = 21097.5
MARATHON_M = 42195.0

# Umfangsrampe zum Venloop (beschlossen 13.09.2026), KW -> km
VOLUME_RAMP: dict[int, int] = {
    38: 30, 39: 50, 40: 58, 41: 64, 42: 48,
    43: 68, 44: 74, 45: 78, 46: 58, 47: 80, 48: 82,
}
LONG_RUN_SHARE = (0.25, 0.33)   # Anteil am Wochenumfang
MAX_SINGLE_RUN_KM = 24.0        # bis zum Taper
RUN_DAYS_PER_WEEK = 6

# Wettkampf-Must-Haves (aus Renntag-Erkenntnisse.md, 24.06.2026)
RACE_TEMP_MAX = 18.0
RACE_TEMP_RISKY = 25.0
RACE_TSB_RANGE = (5.0, 15.0)
RACE_BIKE_KM_MAX_3D = 30.0

# CTL/ATL-Zeitkonstanten (Intervals.icu-Default, unten empirisch verifiziert)
CTL_TC_DAYS = 42
ATL_TC_DAYS = 7
TSB_HARD_SESSION_LIMIT = -15.0   # darunter harte Einheit abschwächen


# =============================================================================
# 2. Pace- und Zeit-Hilfsfunktionen
# =============================================================================

def parse_time(s: str | int | float) -> float:
    """'2:02:21' | '4:23' | '263' -> Sekunden (float)."""
    if isinstance(s, (int, float)):
        return float(s)
    s = s.strip()
    if not re.fullmatch(r"(\d+:)?(\d+:)?\d+(\.\d+)?", s):
        raise ValueError(f"Unlesbare Zeitangabe: {s!r}")
    parts = [float(p) for p in s.split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def fmt_time(sec: float, *, force_h: bool = False) -> str:
    """Sekunden -> 'h:mm:ss' oder 'm:ss'."""
    if sec != sec or sec in (float("inf"), float("-inf")):
        return "—"
    sec = round(sec)
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    if h or force_h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fmt_pace(sec_per_km: float) -> str:
    """s/km -> 'm:ss/km'."""
    return f"{fmt_time(sec_per_km)}/km"


def pace_from(dist_m: float, time_s: float) -> float:
    """s/km aus Distanz und Zeit."""
    if dist_m <= 0:
        raise ValueError("Distanz muss > 0 sein")
    return time_s / (dist_m / 1000.0)


def speed_from_pace(sec_per_km: float) -> float:
    """s/km -> m/s."""
    return 1000.0 / sec_per_km


def pace_from_speed(mps: float) -> float:
    """m/s -> s/km."""
    return 1000.0 / mps


# =============================================================================
# 3. Leistungsprognose: Riegel und VDOT
# =============================================================================

RIEGEL_EXPONENT = 1.06


def riegel(d1_m: float, t1_s: float, d2_m: float, exponent: float = RIEGEL_EXPONENT) -> float:
    """Riegel-Prognose: t2 = t1 * (d2/d1)^exponent.

    Gültig etwa im Bereich 0.5x-2x der Ausgangsdistanz. Darüber hinaus
    optimistisch, weil der Exponent die Glykogen- und Strukturgrenze nicht
    abbildet.
    """
    if d1_m <= 0 or d2_m <= 0 or t1_s <= 0:
        raise ValueError("Distanzen und Zeit müssen > 0 sein")
    return t1_s * (d2_m / d1_m) ** exponent


def riegel_range(d1_m: float, t1_s: float, d2_m: float) -> tuple[float, float]:
    """Prognosekorridor mit Exponent 1.05-1.07 statt Scheingenauigkeit."""
    return riegel(d1_m, t1_s, d2_m, 1.05), riegel(d1_m, t1_s, d2_m, 1.07)


# --- Daniels/Gilbert VDOT -----------------------------------------------------

def _vo2_of_velocity(v_m_per_min: float) -> float:
    """Sauerstoffkosten einer Geschwindigkeit (Daniels/Gilbert)."""
    return -4.60 + 0.182258 * v_m_per_min + 0.000104 * v_m_per_min ** 2


def _velocity_of_vo2(vo2: float) -> float:
    """Umkehrung von _vo2_of_velocity über die p-q-Formel."""
    a, b, c = 0.000104, 0.182258, -4.60 - vo2
    disc = b * b - 4 * a * c
    if disc < 0:
        raise ValueError("Kein reelles Tempo für diesen VO2-Wert")
    return (-b + math.sqrt(disc)) / (2 * a)


def _pct_max_of_duration(t_min: float) -> float:
    """Anteil von VO2max, der über t Minuten gehalten werden kann."""
    return (0.8
            + 0.1894393 * math.exp(-0.012778 * t_min)
            + 0.2989558 * math.exp(-0.1932605 * t_min))


def vdot(dist_m: float, time_s: float) -> float:
    """VDOT aus einer Renn-Leistung.

    Achtung: setzt echten Wettkampfeinsatz voraus. Bei submaximalem Lauf
    (niedrige RPE, HF deutlich unter LTHR) ist der reale VDOT höher.
    """
    t_min = time_s / 60.0
    v = dist_m / t_min
    return _vo2_of_velocity(v) / _pct_max_of_duration(t_min)


def time_for_distance(vdot_value: float, dist_m: float) -> float:
    """Renn-Zeit für eine Distanz bei gegebenem VDOT (numerisch invertiert)."""
    lo, hi = 1.0, 60.0 * 12  # Minuten
    for _ in range(200):
        mid = (lo + hi) / 2
        v = dist_m / mid
        if _vo2_of_velocity(v) / _pct_max_of_duration(mid) > vdot_value:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2 * 60.0


# Trainingsintensitäten als Anteil von VO2max (Daniels).
VDOT_PCT = {
    "easy": 0.70,
    "marathon": 0.84,
    "threshold": 0.88,
    "interval": 0.985,
    "repetition": 1.06,
}


def training_paces(vdot_value: float) -> dict[str, float]:
    """Trainingspaces (s/km) aus VDOT."""
    return {
        name: pace_from_speed(_velocity_of_vo2(vdot_value * pct) / 60.0)
        for name, pct in VDOT_PCT.items()
    }


def goal_gap(dist_m: float, predicted_s: float, goal_s: float) -> dict[str, float]:
    """Lücke zwischen Prognose und Wunschziel, in s/km und Gesamtzeit."""
    km = dist_m / 1000.0
    return {
        "predicted_pace": predicted_s / km,
        "goal_pace": goal_s / km,
        "gap_s_per_km": (predicted_s - goal_s) / km,
        "gap_total_s": predicted_s - goal_s,
    }


# =============================================================================
# 4. Belastungssteuerung: CTL, ATL, TSB
# =============================================================================

def _alpha(tc_days: int) -> float:
    return 1.0 - math.exp(-1.0 / tc_days)


def update_ctl_atl(ctl: float, atl: float, load: float) -> tuple[float, float]:
    """Ein Tag Fortschreibung. Empirisch gegen Intervals.icu verifiziert."""
    ctl_a, atl_a = _alpha(CTL_TC_DAYS), _alpha(ATL_TC_DAYS)
    return (ctl + (load - ctl) * ctl_a, atl + (load - atl) * atl_a)


def tsb(ctl: float, atl: float) -> float:
    """Form / Training Stress Balance."""
    return ctl - atl


def tsb_verdict(value: float) -> str:
    if value < TSB_HARD_SESSION_LIMIT:
        return "harte Einheit abschwächen oder verschieben"
    if value < -5:
        return "belastet — Test oder Wettkampf sinnlos, Training normal möglich"
    if value < 5:
        return "neutral"
    if value <= 15:
        return "Wettkampffenster"
    return "sehr frisch — Gefahr von Formverlust bei längerem Verbleib"


def project(ctl: float, atl: float, daily_loads: Sequence[float]) -> list[dict]:
    """CTL/ATL/TSB Tag für Tag fortschreiben."""
    out = []
    for i, load in enumerate(daily_loads, start=1):
        ctl, atl = update_ctl_atl(ctl, atl, load)
        out.append({"day": i, "load": load, "ctl": ctl, "atl": atl, "tsb": ctl - atl})
    return out


def ramp_rate(ctl_series: Sequence[float]) -> float:
    """CTL-Änderung pro Woche aus einer Tagesreihe."""
    if len(ctl_series) < 2:
        return 0.0
    return (ctl_series[-1] - ctl_series[0]) / (len(ctl_series) - 1) * 7.0


# --- Load pro Kilometer, empirisch --------------------------------------------

# Stichprobe echter Läufe (km, Load, Kategorie), Intervals.icu, 08-09/2026.
# Dient dazu, die Load-Konstanten nachprüfbar zu halten statt sie zu raten.
LOAD_SAMPLE: tuple[tuple[float, float, str], ...] = (
    (27.922, 134, "race"), (5.792, 19, "easy"), (6.378, 19, "easy"),
    (7.210, 28, "quality"), (16.322, 53, "easy"), (7.981, 39, "race"),
    (9.490, 32, "easy"), (7.610, 30, "quality"), (24.021, 97, "mixed"),
    (12.456, 52, "quality"), (8.333, 26, "easy"), (10.840, 48, "quality"),
    (20.043, 61, "easy"), (7.134, 21, "easy"), (8.645, 29, "easy"),
    (13.929, 62, "quality"), (8.500, 34, "quality"), (17.629, 50, "easy"),
    (8.312, 28, "easy"), (12.212, 50, "quality"),
)


def load_per_km(sample: Iterable[tuple[float, float, str]] = LOAD_SAMPLE,
                category: str | None = None) -> float:
    """Mittlere Load je Laufkilometer, aus echten Daten abgeleitet."""
    rows = [(km, ld) for km, ld, cat in sample if category is None or cat == category]
    if not rows:
        raise ValueError(f"Keine Daten für Kategorie {category!r}")
    return sum(ld for _, ld in rows) / sum(km for km, _ in rows)


def week_load(total_km: float, quality_km: float = 0.0, race_km: float = 0.0,
              extra_load: float = 0.0) -> float:
    """Wochen-Load aus Kilometern, nach Intensität getrennt."""
    easy_km = max(0.0, total_km - quality_km - race_km)
    return (easy_km * load_per_km(category="easy")
            + quality_km * load_per_km(category="quality")
            + race_km * load_per_km(category="race")
            + extra_load)


def project_weeks(ctl: float, atl: float, weekly_km: Sequence[float],
                  quality_share: float = 0.18, extra_load_per_week: float = 0.0,
                  run_days: int = RUN_DAYS_PER_WEEK) -> list[dict]:
    """CTL-Verlauf über mehrere Wochen aus geplanten Wochenumfängen.

    Die Load wird gleichmäßig auf die Lauftage verteilt; für den CTL-Endwert
    ist die Verteilung innerhalb der Woche nahezu irrelevant, für ATL/TSB nicht.
    """
    out = []
    for w, km in enumerate(weekly_km, start=1):
        total = week_load(km, quality_km=km * quality_share,
                          extra_load=extra_load_per_week)
        per_day = total / run_days
        loads = [per_day] * run_days + [0.0] * (7 - run_days)
        for load in loads:
            ctl, atl = update_ctl_atl(ctl, atl, load)
        out.append({"week": w, "km": km, "load": total,
                    "ctl": ctl, "atl": atl, "tsb": ctl - atl})
    return out


# =============================================================================
# 5. Laufanalyse: Decoupling, Drift, Schrittlänge
# =============================================================================

def _mean(xs: Sequence[float]) -> float:
    xs = [x for x in xs if x is not None]
    if not xs:
        raise ValueError("Leere Reihe")
    return sum(xs) / len(xs)


def decoupling(speed: Sequence[float], hr: Sequence[float]) -> float:
    """Aerobes Decoupling in Prozent (Pa:HR).

    Vergleicht die Effizienz (Tempo je Herzschlag) der ersten mit der zweiten
    Hälfte. Unter 5 % gilt als aerob sauber.
    """
    n = min(len(speed), len(hr))
    if n < 4:
        raise ValueError("Zu wenig Datenpunkte")
    half = n // 2
    ef1 = _mean(speed[:half]) / _mean(hr[:half])
    ef2 = _mean(speed[half:n]) / _mean(hr[half:n])
    return (ef1 - ef2) / ef1 * 100.0


def hr_drift(hr: Sequence[float]) -> float:
    """HF-Differenz zweite minus erste Hälfte, in bpm."""
    n = len(hr)
    half = n // 2
    return _mean(hr[half:]) - _mean(hr[:half])


def stride_from(speed_mps: float, cadence_rpm: float) -> float:
    """Schrittlänge in m. cadence_rpm ist einbeinig (Garmin), also x2 Schritte."""
    steps_per_s = cadence_rpm * 2 / 60.0
    return speed_mps / steps_per_s


def stride_drift(seg_a: dict, seg_b: dict) -> dict:
    """Zerlegt den Tempoverlust zwischen zwei Segmenten in seine Ursachen.

    Der entscheidende Befund vom 13.09.2026: Tempoverlust bei konstanter HF und
    konstanter Kadenz ist vollständig Schrittlänge -> muskulär-strukturelles
    Limit, nicht kardiovaskulär. Zielwert für den nächsten langen Wettkampf:
    Schrittlängen-Drift unter 3 %.

    seg_* erwartet: {'pace': s/km, 'hr': bpm, 'cadence': rpm}
    """
    va, vb = speed_from_pace(seg_a["pace"]), speed_from_pace(seg_b["pace"])
    sa = stride_from(va, seg_a["cadence"])
    sb = stride_from(vb, seg_b["cadence"])
    d_pace = (vb - va) / va * 100.0
    d_stride = (sb - sa) / sa * 100.0
    d_cad = (seg_b["cadence"] - seg_a["cadence"]) / seg_a["cadence"] * 100.0
    d_hr = seg_b["hr"] - seg_a["hr"]

    if abs(d_hr) <= 2 and abs(d_cad) < 1.5 and d_stride < -2:
        verdict = ("muskulär-strukturell: HF und Kadenz konstant, Tempo geht "
                   "allein über die Schrittlänge verloren")
    elif d_hr > 5:
        verdict = "kardiovaskuläre Drift: HF steigt deutlich"
    elif d_stride > -2 and d_cad < -2:
        verdict = "Kadenzabfall statt Schrittlängenverlust — eher Koordination/Ermüdung ZNS"
    else:
        verdict = "gemischtes Bild"

    return {"speed_pct": d_pace, "stride_pct": d_stride, "cadence_pct": d_cad,
            "hr_delta": d_hr, "stride_a": sa, "stride_b": sb,
            "target_met": d_stride > -3.0, "verdict": verdict}


def resting_hr_flag(recent: Sequence[float], baseline: Sequence[float],
                    threshold: float = 3.0) -> dict:
    """Ruhepuls-Warnsignal: Ausreißer nach oben gegenüber den Vorwochen."""
    r, b = _mean(recent), _mean(baseline)
    return {"recent": r, "baseline": b, "delta": r - b,
            "flag": (r - b) >= threshold or r > RHR_ALARM,
            "above_ramp_limit": r > RHR_ALARM}


# =============================================================================
# 6. Wettkampf: Must-Haves, Pacing, Hitzekorrektur
# =============================================================================

def race_readiness(temp_c: float, ctl: float, atl: float,
                   bike_km_last_3d: float = 0.0) -> dict:
    """Prüft die drei Must-Haves aus Renntag-Erkenntnisse.md."""
    t = tsb(ctl, atl)
    checks = [
        {"name": "Temperatur < 18 °C", "value": f"{temp_c:.1f} °C",
         "ok": temp_c < RACE_TEMP_MAX,
         "note": ("über 25 °C: nach HF steuern statt nach Pace, oder verschieben"
                  if temp_c > RACE_TEMP_RISKY else
                  "20-25 °C ist riskant" if temp_c >= 20 else "")},
        {"name": "TSB +5 bis +15", "value": f"{t:+.1f}",
         "ok": RACE_TSB_RANGE[0] <= t <= RACE_TSB_RANGE[1],
         "note": tsb_verdict(t)},
        {"name": "keine große Radausfahrt in 3 Tagen", "value": f"{bike_km_last_3d:.0f} km",
         "ok": bike_km_last_3d <= RACE_BIKE_KM_MAX_3D,
         "note": f"max. {RACE_BIKE_KM_MAX_3D:.0f} km locker"},
    ]
    passed = sum(c["ok"] for c in checks)
    return {"checks": checks, "passed": passed, "total": len(checks),
            "go": passed == len(checks), "tsb": t}


# Hitze-Korrektur: prozentualer Tempoverlust gegenüber kühlen Bedingungen.
# Stützstellen aus der gängigen Daniels-nahen Näherung, linear interpoliert.
_HEAT_TABLE = ((13.0, 0.0), (15.5, 1.5), (18.0, 2.3), (21.0, 3.0),
               (23.5, 4.2), (26.5, 5.5), (29.0, 6.8), (32.0, 8.0))


def heat_penalty_pct(temp_c: float) -> float:
    """Näherungswert für den Tempoverlust durch Wärme, in Prozent."""
    if temp_c <= _HEAT_TABLE[0][0]:
        return 0.0
    if temp_c >= _HEAT_TABLE[-1][0]:
        return _HEAT_TABLE[-1][1]
    for (t0, p0), (t1, p1) in zip(_HEAT_TABLE, _HEAT_TABLE[1:]):
        if t0 <= temp_c <= t1:
            return p0 + (p1 - p0) * (temp_c - t0) / (t1 - t0)
    return 0.0


def heat_adjusted_pace(pace_s_per_km: float, temp_c: float) -> float:
    """Realistische Zielpace bei Wärme."""
    return pace_s_per_km * (1.0 + heat_penalty_pct(temp_c) / 100.0)


def negative_split(dist_m: float, target_s: float, split_pct: float = 1.0,
                   segment_m: float = 1000.0) -> dict:
    """Pacing-Plan mit negativem Split.

    Der Einbruch am 24.06.2026 kam von einem zu schnellen ersten Kilometer.
    split_pct = Prozent, um die die erste Hälfte langsamer läuft als die zweite.
    """
    n = dist_m / segment_m
    avg_pace = target_s / (dist_m / 1000.0)          # s/km
    # erste Hälfte um +d langsamer, zweite um -d schneller (s/km)
    d = avg_pace * split_pct / 200.0
    slow, fast = avg_pace + d, avg_pace - d
    mid = dist_m / 2.0

    # Exakt über die Distanz integriert: ein Segment, das die Hälfte
    # überschreitet, wird anteilig aufgeteilt. Nur so summiert sich der Plan
    # auf die Zielzeit auf, auch bei krummen Distanzen wie dem HM.
    segments, elapsed, done = [], 0.0, 0.0
    i = 0
    while done < dist_m - 1e-9:
        length = min(segment_m, dist_m - done)
        end = done + length
        slow_m = max(0.0, min(end, mid) - done)
        fast_m = length - slow_m
        seg_time = (slow_m * slow + fast_m * fast) / 1000.0
        elapsed += seg_time
        i += 1
        segments.append({"seg": i, "from_m": done, "to_m": end,
                         "pace": seg_time / (length / 1000.0),
                         "split": seg_time, "elapsed": elapsed})
        done = end
    half = target_s / 2
    return {"segments": segments, "avg_pace": target_s / (dist_m / 1000.0),
            "first_half_s": half + (target_s * split_pct / 400.0),
            "second_half_s": half - (target_s * split_pct / 400.0),
            "total": elapsed, "n_segments": int(math.ceil(n))}


# =============================================================================
# 7. Intervallplanung
# =============================================================================

def rep_pace(vdot_value: float, rep_m: float) -> dict:
    """Zielpace für eine Wiederholung, nach Rep-Länge gestaffelt.

    Kurze Abschnitte schneller, lange langsamer — gleiche Intensität, nicht
    Nachlässigkeit. Zwischen 60 s und 180 s wird linear zwischen
    Repetition- und Interval-Intensität interpoliert.
    """
    i_pace = pace_from_speed(_velocity_of_vo2(vdot_value * VDOT_PCT["interval"]) / 60.0)
    r_pace = pace_from_speed(_velocity_of_vo2(vdot_value * VDOT_PCT["repetition"]) / 60.0)
    est = i_pace * rep_m / 1000.0
    if est >= 180:
        pct = VDOT_PCT["interval"]
    elif est <= 60:
        pct = VDOT_PCT["repetition"]
    else:
        f = (est - 60) / 120.0
        pct = VDOT_PCT["repetition"] + f * (VDOT_PCT["interval"] - VDOT_PCT["repetition"])
    pace = pace_from_speed(_velocity_of_vo2(vdot_value * pct) / 60.0)
    dur = pace * rep_m / 1000.0
    return {"dist_m": rep_m, "pace": pace, "duration": dur,
            "rest_min_s": dur * 0.5, "rest_max_s": dur * 1.0,
            "in_sweet_spot": 140 <= dur <= 300,
            "too_short": dur < 60}


def interval_session(vdot_value: float, reps_m: Sequence[float]) -> dict:
    """Komplette Intervalleinheit durchrechnen.

    Regeln: Rep-Dauer 2-5 min (Optimum ~2:20), Pause 50-100 % der Belastung,
    Pace nach Rep-Länge gestaffelt.
    """
    rows = [rep_pace(vdot_value, m) for m in reps_m]
    work = sum(r["duration"] for r in rows)
    rest = sum((r["rest_min_s"] + r["rest_max_s"]) / 2 for r in rows[:-1])
    warn = []
    if any(r["too_short"] for r in rows):
        warn.append("Reps unter 60 s erreichen die VO2max-Zone kaum")
    in_zone = sum(r["duration"] for r in rows if r["duration"] >= 120)
    if in_zone < 600:
        warn.append(f"nur {fmt_time(in_zone)} in Reps ≥ 2 min — wenig VO2max-Reiz")
    return {"reps": rows, "work_s": work, "rest_s": rest,
            "total_s": work + rest,
            "work_m": sum(reps_m), "warnings": warn}


# =============================================================================
# 8. Umfangs- und Plausibilitätsprüfung
# =============================================================================

def volume_check(week_km: float, prev_km: float | None = None,
                 long_run_km: float | None = None) -> dict:
    """Prüft eine Wochenplanung gegen die Vorgaben aus dem Athletenstatus."""
    issues = []
    if prev_km:
        change = (week_km - prev_km) / prev_km * 100.0
        if change > 15:
            issues.append(f"Steigerung {change:+.0f} % gegenüber Vorwoche — über 15 %")
    else:
        change = None
    if long_run_km is not None:
        share = long_run_km / week_km * 100.0 if week_km else 0.0
        lo, hi = LONG_RUN_SHARE[0] * 100, LONG_RUN_SHARE[1] * 100
        if not (lo <= share <= hi):
            issues.append(f"Long Run {share:.0f} % des Umfangs — Zielkorridor {lo:.0f}-{hi:.0f} %")
        if long_run_km > MAX_SINGLE_RUN_KM:
            issues.append(f"Long Run {long_run_km:.0f} km über der Grenze "
                          f"{MAX_SINGLE_RUN_KM:.0f} km bis zum Taper")
    else:
        share = None
    avg = week_km / RUN_DAYS_PER_WEEK if RUN_DAYS_PER_WEEK else 0.0
    return {"week_km": week_km, "change_pct": change, "long_run_share_pct": share,
            "avg_run_km": avg, "issues": issues, "ok": not issues}


def ramp_release(rhr_recent: float, calf_ok: bool, tsb_value: float,
                 strength_ok: bool) -> dict:
    """Freigabekriterien vor jeder neuen Umfangsstufe.

    Alle vier erfüllt -> nächste Stufe. Einer nicht -> Stufe wiederholen,
    nicht überspringen.
    """
    checks = [
        {"name": f"Ruhepuls im Normalbereich {RHR_NORMAL[0]}-{RHR_NORMAL[1]}",
         "value": f"{rhr_recent:.0f} bpm", "ok": rhr_recent <= RHR_NORMAL[1]},
        {"name": "keine Wadenbeschwerden > 5 min nach Laufende",
         "value": "ja" if calf_ok else "nein", "ok": calf_ok},
        {"name": "TSB über -5", "value": f"{tsb_value:+.1f}", "ok": tsb_value > -5},
        {"name": "Krafteinheit sauber durchführbar",
         "value": "ja" if strength_ok else "nein", "ok": strength_ok},
    ]
    ok = all(c["ok"] for c in checks)
    return {"checks": checks, "release": ok,
            "action": "nächste Stufe" if ok else "Stufe wiederholen, nicht überspringen"}


def polarization(easy_min: float, hard_min: float) -> dict:
    """80/20-Verteilung prüfen (Zeit, nicht Kilometer)."""
    total = easy_min + hard_min
    if total <= 0:
        raise ValueError("Keine Trainingszeit")
    easy_pct = easy_min / total * 100.0
    return {"easy_pct": easy_pct, "hard_pct": 100 - easy_pct,
            "ok": easy_pct >= 75,
            "note": "zu viel Intensität" if easy_pct < 75 else "im Rahmen"}


def hr_for_sport(hr_run: float, sport: str) -> float:
    """Sportartenkorrektur der HF-Vorgabe."""
    key = sport.lower()
    if key not in SPORT_HR_OFFSET:
        raise ValueError(f"Unbekannte Sportart {sport!r}; bekannt: {list(SPORT_HR_OFFSET)}")
    return hr_run + SPORT_HR_OFFSET[key]


def zone_for_hr(hr: float) -> Zone | None:
    for z in ZONES:
        if z.hr_lo <= hr <= z.hr_hi:
            return z
    return None


def zone_for_pace(pace_s_per_km: float) -> Zone | None:
    for z in ZONES:
        if z.pace_hi <= pace_s_per_km <= z.pace_lo:
            return z
    return None


def pct_lthr(hr: float) -> float:
    return hr / LTHR_RUN * 100.0


# =============================================================================
# 9. Status- und Terminlogik
# =============================================================================

def check_status_freshness(today: date | None = None) -> dict:
    today = today or date.today()
    age = (today - STATUS_UPDATED).days
    return {"updated": STATUS_UPDATED, "age_days": age,
            "stale": age > STATUS_MAX_AGE_DAYS,
            "source": STATUS_SOURCE,
            "note": (f"Snapshot ist {age} Tage alt — vor der Planung "
                     f"{STATUS_SOURCE} gegenlesen" if age > STATUS_MAX_AGE_DAYS
                     else "aktuell")}


def weeks_until(target: date, today: date | None = None) -> float:
    today = today or date.today()
    return (target - today).days / 7.0


def countdown(today: date | None = None) -> dict:
    today = today or date.today()
    return {
        "today": today,
        CHECK_RACE: {"date": CHECK_DATE, "weeks": weeks_until(CHECK_DATE, today)},
        GOAL_RACE: {"date": GOAL_DATE, "weeks": weeks_until(GOAL_DATE, today)},
    }


# =============================================================================
# 10. Selbsttest — verifiziert die Formeln gegen echte Intervals.icu-Werte
# =============================================================================

def self_test() -> int:
    fails: list[str] = []

    def close(a: float, b: float, tol: float, label: str) -> None:
        if abs(a - b) > tol:
            fails.append(f"{label}: {a:.4f} != {b:.4f} (tol {tol})")

    # --- Zeitparser
    close(parse_time("2:02:21"), 7341, 0, "parse 2:02:21")
    close(parse_time("4:23"), 263, 0, "parse 4:23")
    close(parse_time(263), 263, 0, "parse int")

    # --- CTL/ATL gegen echte Intervals.icu-Werte (12.09. -> 13.09.2026, Load 320)
    ctl, atl = update_ctl_atl(35.506546, 20.640894, 320.0)
    close(ctl, 42.200195, 0.05, "CTL 13.09.2026 gegen Intervals.icu")
    close(atl, 60.492207, 0.15, "ATL 13.09.2026 gegen Intervals.icu")

    # --- Schrittlänge gegen die Garmin-Werte des 28ers
    v = 27922.46 / 7337
    close(v, 3.805, 0.002, "Ø-Tempo 28er")
    close(stride_from(v, 83.05317), 1.3747, 0.002, "Schrittlänge 28er gegen Garmin")

    # --- Riegel: 28er -> HM
    t_hm = riegel(27922.46, 7341, HM_M)
    close(t_hm, 5454.5, 2.0, "Riegel 28er -> HM")
    g = goal_gap(HM_M, t_hm, GOAL_TIME_S)
    close(g["goal_pace"], 227.5, 0.2, "Sub-1:20 Zielpace")
    close(g["gap_s_per_km"], 31.0, 0.5, "Lücke zu Sub-1:20")

    # --- VDOT plausibel
    vd = vdot(27922.46, 7341)
    if not (48 < vd < 53):
        fails.append(f"VDOT 28er unplausibel: {vd:.1f}")
    # Rückrechnung muss die Ausgangsleistung reproduzieren
    close(time_for_distance(vd, 27922.46), 7341, 5.0, "VDOT-Rückrechnung")

    # --- Load pro Kilometer aus echten Daten
    lpk_easy = load_per_km(category="easy")
    lpk_race = load_per_km(category="race")
    if not (2.9 < lpk_easy < 3.4):
        fails.append(f"Load/km locker unplausibel: {lpk_easy:.2f}")
    if not (4.5 < lpk_race < 5.1):
        fails.append(f"Load/km Renntempo unplausibel: {lpk_race:.2f}")

    # --- TSB
    close(tsb(42.2, 60.5), -18.3, 0.01, "TSB")

    # --- Decoupling: konstante Effizienz -> 0 %
    close(decoupling([3.5] * 10, [150] * 10), 0.0, 1e-9, "Decoupling konstant")
    # HF steigt in der zweiten Hälfte -> positives Decoupling
    if decoupling([3.5] * 10, [145] * 5 + [155] * 5) <= 0:
        fails.append("Decoupling bei HF-Anstieg nicht positiv")

    # --- Stride-Drift: der Befund vom 13.09.2026 muss reproduziert werden
    d = stride_drift({"pace": 256, "hr": 152, "cadence": 83.3},
                     {"pace": 271, "hr": 152, "cadence": 83.1})
    close(d["stride_pct"], -5.3, 0.4, "Schrittlängen-Drift 28er")
    if d["target_met"]:
        fails.append("Schrittlängen-Drift -5,3 % darf das 3-%-Ziel nicht erfüllen")
    if "muskulär" not in d["verdict"]:
        fails.append(f"Drift-Urteil falsch: {d['verdict']}")

    # --- Wettkampf-Must-Haves: der 13.09. hat alle drei erfüllt
    r = race_readiness(temp_c=12.0, ctl=42.2, atl=27.3, bike_km_last_3d=0)
    if not r["go"]:
        fails.append("Must-Haves 13.09.2026 sollten erfüllt sein")
    # 24.06.2026: Hitze + Vorermüdung -> muss durchfallen
    r2 = race_readiness(temp_c=27.0, ctl=50.0, atl=58.0, bike_km_last_3d=80)
    if r2["go"] or r2["passed"] != 0:
        fails.append("Must-Haves 24.06.2026 müssten alle drei scheitern")

    # --- Hitze
    close(heat_penalty_pct(10), 0.0, 1e-9, "Hitze unter 13 °C")
    if not (heat_penalty_pct(26) > heat_penalty_pct(20) > heat_penalty_pct(15)):
        fails.append("Hitzekorrektur nicht monoton")

    # --- Negativer Split
    ns = negative_split(HM_M, GOAL_TIME_S, split_pct=1.0)
    close(ns["total"], GOAL_TIME_S, 1.0, "Negativer Split Gesamtzeit")
    if ns["first_half_s"] <= ns["second_half_s"]:
        fails.append("Erste Hälfte muss langsamer sein als die zweite")

    # --- Intervalle: kurze Reps nie langsamer als lange.
    # 1200 m und 1000 m liegen beide über 180 s und teilen sich die I-Pace —
    # daher nur monoton, nicht streng monoton. Streng wird es erst unter 180 s.
    s = interval_session(vd, [1200, 1000, 800, 600, 400])
    paces = [r["pace"] for r in s["reps"]]
    if not all(paces[i] >= paces[i + 1] - 1e-9 for i in range(len(paces) - 1)):
        fails.append("Rep-Paces nicht nach Länge gestaffelt")
    if not paces[0] > paces[-1]:
        fails.append("400 m muss schneller sein als 1200 m")

    # --- Zonen
    if zone_for_hr(155) is None or zone_for_hr(155).nr != 3:
        fails.append("Zonenzuordnung HF 155 falsch")
    close(hr_for_sport(150, "bike"), 140, 0, "HF-Korrektur Rad")

    # --- Umfangsprüfung
    vc = volume_check(64, prev_km=58, long_run_km=30)
    if vc["ok"]:
        fails.append("Long Run 30 km müsste die Grenze reißen")

    # --- Freigabekriterien
    if ramp_release(47, True, 2.0, True)["release"] is not True:
        fails.append("Freigabe müsste erteilt werden")
    if ramp_release(54, True, 2.0, True)["release"] is not False:
        fails.append("Ruhepuls 54 müsste die Freigabe blockieren")

    print(f"Selbsttest: {'OK' if not fails else str(len(fails)) + ' FEHLER'}")
    for f in fails:
        print("  FEHLER:", f)
    return 1 if fails else 0


# =============================================================================
# 11. CLI
# =============================================================================

def _print_table(rows: list[tuple[str, str]], title: str = "") -> None:
    if title:
        print(f"\n{title}")
        print("-" * max(len(title), 40))
    w = max((len(a) for a, _ in rows), default=0)
    for a, b in rows:
        print(f"  {a:<{w}}  {b}")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Rechenkern für die Laufcoach-Steuerung")
    p.add_argument("--self-test", action="store_true", help="Formeln gegen echte Daten prüfen")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("riegel", help="Distanzprognose")
    sp.add_argument("--from", dest="d1", type=float, required=True, help="Ausgangsdistanz in m")
    sp.add_argument("--time", required=True, help="Zeit, z. B. 2:02:21")
    sp.add_argument("--to", dest="d2", type=float, required=True, help="Zieldistanz in m")

    sp = sub.add_parser("vdot", help="VDOT und Trainingspaces")
    sp.add_argument("--dist", type=float, required=True)
    sp.add_argument("--time", required=True)

    sp = sub.add_parser("tsb", help="Form berechnen")
    sp.add_argument("--ctl", type=float, required=True)
    sp.add_argument("--atl", type=float, required=True)

    sp = sub.add_parser("ctl", help="CTL über Wochenumfänge projizieren")
    sp.add_argument("--ctl", type=float, required=True)
    sp.add_argument("--atl", type=float, required=True)
    sp.add_argument("--weeks", required=True, help="Wochen-km, kommagetrennt")
    sp.add_argument("--quality-share", type=float, default=0.18)

    sp = sub.add_parser("race", help="Wettkampf-Must-Haves prüfen")
    sp.add_argument("--temp", type=float, required=True)
    sp.add_argument("--ctl", type=float, required=True)
    sp.add_argument("--atl", type=float, required=True)
    sp.add_argument("--bike-km-3d", type=float, default=0.0)

    sp = sub.add_parser("splits", help="Pacing-Plan mit negativem Split")
    sp.add_argument("--dist", type=float, required=True)
    sp.add_argument("--target", required=True)
    sp.add_argument("--split-pct", type=float, default=1.0)

    sp = sub.add_parser("intervals", help="Intervalleinheit durchrechnen")
    sp.add_argument("--vdot", type=float, required=True)
    sp.add_argument("--reps", required=True, help="Rep-Distanzen in m, kommagetrennt")

    sub.add_parser("zones", help="Zonentabelle")
    sub.add_parser("status", help="Statusfrische und Countdown")

    a = p.parse_args(argv)

    if a.self_test:
        return self_test()

    if a.cmd == "riegel":
        t1, d1, d2 = parse_time(a.time), a.d1, a.d2
        t2 = riegel(d1, t1, d2)
        lo, hi = riegel_range(d1, t1, d2)
        _print_table([
            ("Ausgang", f"{d1/1000:.3f} km in {fmt_time(t1)} ({fmt_pace(pace_from(d1, t1))})"),
            ("Prognose", f"{d2/1000:.3f} km in {fmt_time(t2)} ({fmt_pace(pace_from(d2, t2))})"),
            ("Korridor", f"{fmt_time(lo)} – {fmt_time(hi)} (Exponent 1,05–1,07)"),
        ], "Riegel-Prognose")
        if abs(math.log(d2 / d1)) > math.log(2):
            print("\n  Achtung: Extrapolation über Faktor 2 — Prognose optimistisch.")

    elif a.cmd == "vdot":
        t = parse_time(a.time)
        vd = vdot(a.dist, t)
        tp = training_paces(vd)
        _print_table([("VDOT", f"{vd:.1f}"),
                      ("Leistung", f"{a.dist/1000:.3f} km in {fmt_time(t)}")], "VDOT")
        _print_table([(k.capitalize(), fmt_pace(v)) for k, v in tp.items()], "Trainingspaces")
        _print_table([(f"{d/1000:.3f} km", fmt_time(time_for_distance(vd, d)))
                      for d in (5000, 10000, HM_M, MARATHON_M)], "Äquivalente Rennzeiten")
        print("\n  Gilt nur bei echtem Wettkampfeinsatz. Bei submaximalem Lauf "
              "(niedrige RPE,\n  HF deutlich unter LTHR) liegt der reale VDOT höher.")

    elif a.cmd == "tsb":
        v = tsb(a.ctl, a.atl)
        _print_table([("CTL", f"{a.ctl:.1f}"), ("ATL", f"{a.atl:.1f}"),
                      ("TSB", f"{v:+.1f}"), ("Bewertung", tsb_verdict(v))], "Form")

    elif a.cmd == "ctl":
        km = [float(x) for x in a.weeks.split(",")]
        rows = project_weeks(a.ctl, a.atl, km, quality_share=a.quality_share)
        _print_table([(f"Woche {r['week']}: {r['km']:.0f} km",
                       f"Load {r['load']:.0f}  CTL {r['ctl']:.1f}  "
                       f"ATL {r['atl']:.1f}  TSB {r['tsb']:+.1f}") for r in rows],
                     "CTL-Projektion")
        print(f"\n  Load/km: locker {load_per_km(category='easy'):.2f}, "
              f"Qualität {load_per_km(category='quality'):.2f}, "
              f"Renntempo {load_per_km(category='race'):.2f} (aus echten Daten)")

    elif a.cmd == "race":
        r = race_readiness(a.temp, a.ctl, a.atl, a.bike_km_3d)
        _print_table([(("OK   " if c["ok"] else "NEIN ") + c["name"],
                       c["value"] + (f"  — {c['note']}" if c["note"] else ""))
                      for c in r["checks"]], "Wettkampf-Must-Haves")
        print(f"\n  {r['passed']}/{r['total']} erfüllt — "
              f"{'Start freigegeben' if r['go'] else 'kein valider Test'}")
        if a.temp >= 20:
            print(f"  Hitzekorrektur: {heat_penalty_pct(a.temp):.1f} % langsamer erwarten")

    elif a.cmd == "splits":
        t = parse_time(a.target)
        ns = negative_split(a.dist, t, a.split_pct)
        _print_table([(f"km {s['seg']}", f"{fmt_pace(s['pace'])}   kumuliert {fmt_time(s['elapsed'])}")
                      for s in ns["segments"]], f"Pacing {a.dist/1000:.3f} km in {fmt_time(t)}")
        _print_table([("Ø-Pace", fmt_pace(ns["avg_pace"])),
                      ("1. Hälfte", fmt_time(ns["first_half_s"])),
                      ("2. Hälfte", fmt_time(ns["second_half_s"]))], "Hälften")

    elif a.cmd == "intervals":
        reps = [float(x) for x in a.reps.split(",")]
        s = interval_session(a.vdot, reps)
        _print_table([(f"{r['dist_m']:.0f} m",
                       f"{fmt_pace(r['pace'])}  ≈ {fmt_time(r['duration'])}  "
                       f"Pause {fmt_time(r['rest_min_s'])}–{fmt_time(r['rest_max_s'])}"
                       + ("" if r["in_sweet_spot"] else "  (außerhalb 2–5 min)"))
                      for r in s["reps"]], "Intervalleinheit")
        _print_table([("Belastung", f"{s['work_m']:.0f} m / {fmt_time(s['work_s'])}"),
                      ("Pausen", fmt_time(s["rest_s"])),
                      ("Gesamt (ohne Ein/Aus)", fmt_time(s["total_s"]))], "Summe")
        for w in s["warnings"]:
            print(f"\n  Hinweis: {w}")

    elif a.cmd == "zones":
        _print_table([(f"Z{z.nr} {z.name}",
                       f"{z.hr_lo}–{z.hr_hi} bpm   {fmt_pace(z.pace_lo)}–{fmt_pace(z.pace_hi)}")
                      for z in ZONES], f"Zonen (LTHR {LTHR_RUN}, Stufentest Juni 2026)")
        print(f"\n  Intervals.icu führt LTHR {LTHR_INTERVALS_ICU} — zu hoch, nicht verwenden.")

    elif a.cmd == "status":
        f = check_status_freshness()
        c = countdown()
        _print_table([("Snapshot", f"{f['updated']} ({f['age_days']} Tage alt)"),
                      ("Quelle", f["source"]), ("Bewertung", f["note"])], "Athletenstatus")
        _print_table([(k, f"{v['date']} — {v['weeks']:.1f} Wochen")
                      for k, v in c.items() if isinstance(v, dict)], "Countdown")
    else:
        p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
