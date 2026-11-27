#!/usr/bin/env python3
"""Haal podium- en finaleplaatsen van Neptunus Aalst uit een Lenex-uitslag (.lxf of .lef).

Lenex is het officiële uitwisselformaat van Splash Meet Manager; op elke livetiming-pagina
staat het als 'results.lxf'. Dit is nauwkeuriger dan een PDF.

Gebruik:
    python3 tools/lenex.py results.lxf [--club ZNA] [--alles]
"""
import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict

SLAG = {"FREE": "VS", "BACK": "R", "BREAST": "SS", "FLY": "VL", "MEDLEY": "W"}


def laad(pad):
    if zipfile.is_zipfile(pad):
        with zipfile.ZipFile(pad) as z:
            naam = next(n for n in z.namelist() if n.lower().endswith(".lef"))
            return ET.fromstring(z.read(naam))
    return ET.parse(pad).getroot()


def tijd(t):
    # '00:01:02.34' -> '1:02.34'
    if not t or t.startswith("NT"):
        return ""
    h, m, s = t.split(":")
    m = int(h) * 60 + int(m)
    return f"{m}:{s}" if m else s.lstrip("0") if not s.startswith("0.") else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lenex")
    ap.add_argument("--club", default="ZNA")
    ap.add_argument("--alles", action="store_true")
    a = ap.parse_args()

    root = laad(a.lenex)
    meet = root.find(".//MEET")

    events = {}
    for ev in meet.iter("EVENT"):
        st = ev.find("SWIMSTYLE")
        nr = f"{st.get('distance')}{SLAG.get(st.get('stroke'), st.get('stroke'))}"
        aflossing = int(st.get("relaycount", "1"))
        if aflossing > 1:
            nr = f"{aflossing}x{nr}"
        events[ev.get("eventid")] = {"nummer": nr, "ronde": ev.get("round", "TIM"), "estafette": aflossing > 1,
                                     "groepen": ev.findall(".//AGEGROUP")}

    # resultaten van de club
    van_club = {}
    personen = []
    for club in meet.iter("CLUB"):
        if club.get("code") != a.club:
            continue
        for atl in club.iter("ATHLETE"):
            p = {"voornaam": atl.get("firstname", "").strip(), "achternaam": atl.get("lastname", "").strip().title()}
            personen.append(p)
            for res in atl.iter("RESULT"):
                van_club[res.get("resultid")] = (p, res.get("swimtime"))
        for rel in club.iter("RELAY"):
            for res in rel.iter("RESULT"):
                van_club[res.get("resultid")] = ({"estafette": True}, res.get("swimtime"))

    per_voornaam = defaultdict(set)
    for p in personen:
        per_voornaam[p["voornaam"]].add(p["achternaam"])

    def toon(p):
        if len(per_voornaam[p["voornaam"]]) > 1:
            return f"{p['voornaam']} {''.join(w[0] for w in p['achternaam'].split())}"
        return p["voornaam"]

    medailles = {1: defaultdict(list), 2: defaultdict(list), 3: defaultdict(list)}
    estafettes = []
    finales = defaultdict(list)
    alles = []
    for ev in events.values():
        for g in ev["groepen"]:
            for rk in g.iter("RANKING"):
                rid = rk.get("resultid")
                if rid not in van_club:
                    continue
                p, t = van_club[rid]
                plaats = int(rk.get("place", "0") or 0)
                if plaats <= 0:
                    continue
                naam = "estafette" if p.get("estafette") else toon(p)
                alles.append(f"  {ev['nummer']:9} {ev['ronde']:4} {g.get('name', ''):12} {plaats:>3}. {naam:12} {tijd(t)}")
                if ev["ronde"] in ("FIN", "SOF"):
                    finales["A-finale"].append(f"{naam} ({ev['nummer']}, {plaats}e)")
                if ev["ronde"] in ("PRE", "SEM") or plaats > 3:
                    continue
                if p.get("estafette"):
                    estafettes.append(f"{['', 'goud', 'zilver', 'brons'][plaats]}: {ev['nummer']} ({g.get('name', '')})")
                else:
                    key = (p["achternaam"], naam)
                    if ev["nummer"] not in medailles[plaats][key]:
                        medailles[plaats][key].append(ev["nummer"])

    uit = {kleur: [f"{n} ({', '.join(nrs)})" for (_, n), nrs in sorted(medailles[pl].items())]
           for pl, kleur in [(1, "goud"), (2, "zilver"), (3, "brons")]}
    if finales:
        uit["finales"] = dict(finales)
    if estafettes:
        uit["estafettes"] = estafettes
    print(f"=== {meet.get('name')} ({meet.get('city')})  {len(personen)} clubzwemmers")
    print(json.dumps(uit, ensure_ascii=False, indent=2))
    if a.alles:
        print("\n".join(alles))


if __name__ == "__main__":
    main()
