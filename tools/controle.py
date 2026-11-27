#!/usr/bin/env python3
"""Controleer een editie vóór publicatie.

Gebruik:
    python3 tools/controle.py 2026-q2q3

Toont:
- fouten (ongeldige JSON, onbestaande datum, einddatum vóór begindatum, ontbrekende foto)
- elke datum met zijn weekdag, om te controleren tegen de echte kalender
- alle open 'todo'-punten
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAGEN = ["ma", "di", "wo", "do", "vr", "za", "zo"]


def d(s):
    return date.fromisoformat(s) if s else None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    map_ = ROOT / "edities" / sys.argv[1].lower()
    try:
        data = json.loads((map_ / "data.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"FOUT: data.json is geen geldige JSON: {e}")

    fouten, todos, datums = [], [], []

    def check(waar, item):
        try:
            van, tot = d(item.get("van")), d(item.get("tot"))
        except ValueError as e:
            fouten.append(f"{waar}: ongeldige datum ({e})")
            return
        if van:
            datums.append((van, tot, waar))
        if van and tot and tot < van:
            fouten.append(f"{waar}: einddatum ligt vóór begindatum")
        for f in item.get("fotos") or []:
            src = f if isinstance(f, str) else f.get("src", "")
            if not src.startswith("http") and not (map_ / src).exists():
                fouten.append(f"{waar}: foto niet gevonden: {src}")
        if item.get("todo"):
            todos.append(f"{waar}: {item['todo']}")

    for sectie in ["wedstrijden", "stages", "kalender", "extra"]:
        blok = data.get(sectie) or {}
        if blok.get("todo"):
            todos.append(f"[{sectie}] {blok['todo']}")
        for item in blok.get("items", []):
            if "tussentitel" in item:
                continue
            naam = item.get("naam") or item.get("titel") or "?"
            check(f"[{sectie}] {naam}", item)

    print(f"Editie {data.get('periode')} – concept: {data.get('concept')}\n")
    print("DATUMS (controleer de weekdag):")
    for van, tot, waar in sorted(datums, key=lambda x: (x[0], x[2])):
        s = f"{DAGEN[van.weekday()]} {van:%d/%m/%Y}"
        if tot and tot != van:
            s += f" – {DAGEN[tot.weekday()]} {tot:%d/%m/%Y}"
        print(f"  {s:32} {waar}")
    print(f"\nOPEN PUNTEN ({len(todos)}):")
    for t in todos:
        print("  - " + t)
    print(f"\nFOUTEN ({len(fouten)}):")
    for f in fouten:
        print("  ! " + f)
    if not fouten and not todos and not data.get("concept"):
        print("\nKlaar om te publiceren ✔")
    sys.exit(1 if fouten else 0)


if __name__ == "__main__":
    main()
