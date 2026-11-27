#!/usr/bin/env python3
"""Haal podium- en finaleplaatsen van Neptunus Aalst uit een Splash Meet Manager-uitslag (PDF).

Gebruik:
    python3 tools/uitslagen.py uitslag.pdf [--club ZNA] [--top 3] [--alles]

Werkt per 'rangschikking': een programmanummer, eventueel opgesplitst per
leeftijdscategorie (bv. '13 - 14 jaar', '12 jaar, Meisjes') of per finale (A/B).
Een zwemmer van de club wordt herkend aan de licentie (ZNA/...), de clubcode ZNA
of de clubnaam 'Neptunus Aalst'.

Uitvoer: een lijst per medaillekleur in het formaat van data.json, plus
(met --alles) elke ZNA-plaats met tijd, handig om clubrecords na te kijken.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict

SLAG = {"vlinderslag": "VL", "rugslag": "R", "schoolslag": "SS", "vrije slag": "VS", "wisselslag": "W"}
RE_EVENT = re.compile(r"Programmanr\.\s*(\d+)[,\s]+(.*)")
RE_NUMMER = re.compile(r"(\d+)\s*m\s+(vlinderslag|rugslag|schoolslag|vrije slag|wisselslag)", re.I)
RE_ESTAFETTE = re.compile(r"\d\s*x\s*\d+\s*m", re.I)
RE_LEEFTIJD = re.compile(r"^\s*(\d+\s*-\s*\d+ jaar|\d+ jaar(?: en ouder)?(?:,\s*(?:Jongens|Meisjes|Dames|Heren))?|open leeftijdsgroep|Junioren|Senioren|Masters.*)\s*$", re.I)
RE_FINALE = re.compile(r"\b([A-D])[\s-]*Finale\b|\bFinale\s+([A-D])\b", re.I)
RE_VOORRONDE = re.compile(r"Voorronde|Series", re.I)
RE_RESULTAAT = re.compile(r"^\s*(\d+)\.\s+(\S.*?)\s{2,}(.*)$")
RE_GELIJK = re.compile(r"^\s{2,}([A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ'’\- ]+,?\s+[A-Za-zÀ-ÿ].*?)\s{2,}(.*\d\.\d\d.*)$")  # ex aequo: zelfde plaats, geen rangnummer
RE_TIJD = re.compile(r"(\d{1,2}:\d{2}\.\d{2}|\d{2}\.\d{2})")


def is_club(rest, club):
    return bool(re.search(rf"(^|\s){club}(/|\s|$)", rest)) or "Neptunus Aalst" in rest


def seconden(t):
    m, _, sec = t.rpartition(":")
    return (int(m) * 60 if m else 0) + float(sec)


def splits_naam(naam):
    """'DE SMET, Lily' of 'DE SMET Lily' -> ('De Smet', 'Lily')."""
    naam = naam.strip()
    if "," in naam:
        a, v = naam.split(",", 1)
    else:
        delen = naam.split()
        i = 0
        while i < len(delen) - 1 and delen[i].upper() == delen[i] and any(c.isalpha() for c in delen[i]):
            i += 1
        a, v = " ".join(delen[:i]), " ".join(delen[i:])
    return a.strip().title(), v.strip()


def lees(pdf):
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout


def ontleed(tekst, club):
    rijen = []
    event = None   # (nummer, slag-afkorting)
    groep = ""
    ronde = ""
    vorige = None        # rang van de vorige resultaatlijn (voor ex aequo)
    finale_start = None  # eerste rang binnen de huidige finale
    for lijn in tekst.splitlines():
        m = RE_EVENT.search(lijn)
        if m:
            titel = m.group(2)
            n = RE_NUMMER.search(titel)
            if RE_ESTAFETTE.search(titel) or not n:
                event = None
            else:
                nieuw = f"{n.group(1)}{SLAG[n.group(2).lower()]}"
                vervolg = "," in lijn.split("Programmanr.")[1][:6]  # 'Programmanr. 3, Dames, ...' = vervolgpagina
                if not vervolg:
                    groep = ""
                    ronde = ""
                event = nieuw
            continue
        if event is None:
            continue
        if RE_VOORRONDE.search(lijn) and "Resultaten" in lijn:
            ronde = "voorronde"
        f = RE_FINALE.search(lijn)
        if f and "Resultaten" in lijn or (f and len(lijn.strip()) < 30):
            ronde = (f.group(1) or f.group(2)).upper() + "-finale"
            finale_start = None
            continue
        if RE_LEEFTIJD.match(lijn):
            groep = lijn.strip()
            continue
        r = RE_RESULTAAT.match(lijn)
        if r:
            rang, naam, rest = int(r.group(1)), r.group(2), r.group(3)
        elif vorige and RE_GELIJK.match(lijn):
            g = RE_GELIJK.match(lijn)
            rang, naam, rest = vorige, g.group(1), g.group(2)
        else:
            if lijn.strip() and not lijn.strip().startswith(("50m", "100m", "SW", "Splash")):
                vorige = None if not re.match(r"^\s+\d", lijn) else vorige
            continue
        vorige = rang
        if ronde.endswith("finale") and finale_start is None:
            finale_start = rang
        if is_club(rest, club):
            achternaam, voornaam = splits_naam(naam)
            tijden = RE_TIJD.findall(rest)
            rijen.append({
                "nummer": event, "groep": groep, "ronde": ronde,
                "plaats": rang, "plaats_in_finale": rang - (finale_start or 1) + 1,
                "achternaam": achternaam, "voornaam": voornaam,
                "tijd": max(tijden, key=seconden) if tijden else "",
            })
    return rijen


def herstel_namen(rijen):
    """Namen als 'Van Calenbergh Lena' (geen hoofdletters/komma) splitsen met de namen uit andere uitslagen;
    anders is het laatste woord de voornaam."""
    gekend = {f"{r['achternaam']} {r['voornaam']}".lower(): (r["achternaam"], r["voornaam"])
              for r in rijen if r["achternaam"]}
    for r in rijen:
        if r["achternaam"]:
            continue
        vol = r["voornaam"]
        if vol.lower() in gekend:
            r["achternaam"], r["voornaam"] = gekend[vol.lower()]
        else:
            *a, v = vol.split()
            r["achternaam"], r["voornaam"] = " ".join(a).title(), v


def namen(rijen):
    """Voornaam, met initiaal van de achternaam als meerdere clubzwemmers dezelfde voornaam hebben."""
    per_voornaam = defaultdict(set)
    for r in rijen:
        per_voornaam[r["voornaam"]].add(r["achternaam"])
    def toon(r):
        if len(per_voornaam[r["voornaam"]]) > 1:
            return f"{r['voornaam']} {''.join(w[0] for w in r['achternaam'].split())}"
        return r["voornaam"]
    return toon


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="+", help="een of meer uitslagen-PDF's (samen verwerken = consistente namen)")
    ap.add_argument("--club", default="ZNA")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--alles", action="store_true")
    a = ap.parse_args()

    per_pdf = {pdf: ontleed(lees(pdf), a.club) for pdf in a.pdf}
    herstel_namen([r for rijen in per_pdf.values() for r in rijen])
    toon = namen([r for rijen in per_pdf.values() for r in rijen])
    for pdf, rijen in per_pdf.items():
        medailles = {1: defaultdict(list), 2: defaultdict(list), 3: defaultdict(list)}
        finales = defaultdict(list)
        for r in rijen:
            if r["ronde"].endswith("finale"):
                finales[r["ronde"]].append(f"{toon(r)} ({r['nummer']}, {r['plaats_in_finale']}e)")
            elif r["ronde"] != "voorronde" and r["plaats"] <= min(a.top, 3):
                key = (r["achternaam"], toon(r))
                if r["nummer"] not in medailles[r["plaats"]][key]:
                    medailles[r["plaats"]][key].append(r["nummer"])
        uit = {}
        for plaats, kleur in [(1, "goud"), (2, "zilver"), (3, "brons")]:
            uit[kleur] = [f"{naam} ({', '.join(nrs)})" for (_, naam), nrs in sorted(medailles[plaats].items())]
        if finales:
            uit["finales"] = dict(sorted(finales.items()))
        print(f"=== {pdf}  ({len(rijen)} clubresultaten)")
        print(json.dumps(uit, ensure_ascii=False, indent=2))
        if a.alles:
            for r in rijen:
                print(f"  {r['nummer']:6} {r['groep'][:22]:22} {r['ronde']:10} {r['plaats']:>3}. {toon(r):12} {r['tijd']}")


if __name__ == "__main__":
    main()
