#!/usr/bin/env python3
"""Maak (of ververs) de map van een editie.

Gebruik:
    python3 tools/nieuwe_editie.py 2027-q1 "Q1 2027"

- maakt edities/<code>/ met index.html (vaste template) en een lege data.json
  (een bestaande data.json wordt nooit overschreven)
- zet de editie bovenaan in edities.json (het archief op de startpagina)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://eloc16.github.io/nieuwsbrief-zna"

STUB = """<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nieuwsbrief {periode} – Competitiezwemmen Neptunus Aalst</title>
<meta name="description" content="Wedstrijden, medailles, stages en de kalender van de competitiezwemmers van Neptunus Aalst.">
<meta property="og:title" content="Nieuwsbrief {periode} – Competitiezwemmen Neptunus Aalst">
<meta property="og:description" content="Wedstrijden, medailles, stages en de kalender van de competitiezwemmers.">
<meta property="og:type" content="article">
<meta property="og:url" content="{site}/edities/{code}/">
<meta property="og:image" content="{site}/assets/deelbeeld.png">
<link rel="icon" href="../../assets/favicon.svg">
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<main id="nieuwsbrief" data-src="data.json"><p style="padding:24px">Nieuwsbrief laden…</p></main>
<script src="../../assets/render.js"></script>
</body>
</html>
"""

LEEG = {
    "editie": "",
    "titel": "Nieuwsbrief",
    "periode": "",
    "ondertitel": "",
    "redactie": "",
    "gepubliceerd": None,
    "concept": True,
    "intro": "",
    "wedstrijden": {"titel": "Wedstrijdnieuws", "intro": "",
                    "voetnoot": "De medailles worden alfabetisch op achternaam vermeld.", "items": []},
    "stages": {"titel": "Stages", "items": []},
    "kalender": {"titel": "Wedstrijdkalender", "items": []},
    "extra": {"titel": "Extra", "items": []},
    "sponsors": {"titel": "Dank aan onze sponsors", "items": [], "vrij": ""},
}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    code, periode = sys.argv[1].lower(), sys.argv[2]
    map_ = ROOT / "edities" / code
    (map_ / "fotos").mkdir(parents=True, exist_ok=True)
    (map_ / "fotos" / ".gitkeep").touch()
    (map_ / "index.html").write_text(STUB.format(periode=periode, code=code, site=SITE), encoding="utf-8")

    data = map_ / "data.json"
    if not data.exists():
        leeg = dict(LEEG, editie=code, periode=periode)
        data.write_text(json.dumps(leeg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Nieuwe data.json aangemaakt: {data}")
    else:
        print(f"data.json bestaat al, niet aangeraakt: {data}")

    archief = ROOT / "edities.json"
    lijst = json.loads(archief.read_text(encoding="utf-8")) if archief.exists() else []
    if not any(e["code"] == code for e in lijst):
        lijst.insert(0, {"code": code, "periode": periode})
        archief.write_text(json.dumps(lijst, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Toegevoegd aan archief: {periode}")


if __name__ == "__main__":
    main()
