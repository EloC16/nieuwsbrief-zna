# Werkwijze nieuwsbrief

## Ritme en deadlines

Eén editie per kwartaal. **Deadline: 14 dagen na het einde van het kwartaal.**

| Editie | Periode | Verzamelen tot | Publiceren uiterlijk |
|---|---|---|---|
| Q2 + Q3 2026 (inhaaleditie) | apr – sep 2026 | – | zo snel mogelijk |
| Q4 2026 | okt – dec 2026 | 31/12/2026 | do 14/01/2027 |
| Q1 2027 | jan – maa 2027 | 31/03/2027 | wo 14/04/2027 |
| Q2 2027 | apr – jun 2027 | 30/06/2027 | wo 14/07/2027 |
| Q3 2027 | jul – sep 2027 | 30/09/2027 | do 14/10/2027 |

(Weekdagen gecontroleerd tegen de kalender.)

## Tijdens het kwartaal (doorlopend, 2 minuten per wedstrijd)

Alles komt in Google Drive, map **Nieuwsbrief Competitie / <kwartaal>**:

- `01_uitslagen-pdf/`: de uitslag van elke wedstrijd, meteen na de wedstrijd. Bij voorkeur:
  1. **`results.lxf`** van de livetiming-pagina (Lenex: het nauwkeurigst, `tools/lenex.py`)
  2. anders de **uitslagen-PDF** van Splash Meet Manager (`tools/uitslagen.py`)
  3. BK's op swimrankings: **screenshots** van de clubpagina van Neptunus Aalst
- `02_fotos/`: een paar goede foto's per wedstrijd/stage (submapje per wedstrijd mag)
- `03_teksten/`: verslagjes, aankondigingen, save the dates (een notitie of Google Doc volstaat)

Vaste zaken (logo, sponsorlogo's, clubrecords) staan in `_vast/`.

## Na het kwartaal (de editie maken)

1. **Claude vragen** de editie op te stellen ("maak de nieuwsbrief van Q1 2027"). Claude:
   - maakt de editiemap aan (`tools/nieuwe_editie.py`)
   - haalt uit de uitslagen-PDF's alle podiumplaatsen en finaleplaatsen van Neptunus Aalst
     (`tools/uitslagen.py`, werkt op Splash Meet Manager-PDF's; zwemmers herkend aan licentie ZNA/…)
   - vergelijkt de tijden met de clubrecords
   - zet foto's verkleind in de editie en teksten op hun plaats
   - draait `tools/controle.py` en zet ontbrekende zaken als gele "nog te doen"-blokken
2. **Nalezen** via de link (concept is zichtbaar, maar nog niet in het archief gedeeld).
3. **Aanvullen**: open punten wegwerken (via Claude of rechtstreeks in `data.json` op GitHub).
4. **Publiceren**: `concept` op `false`, `gepubliceerd` invullen.
5. **Delen**: link in de WhatsApp-groepen en op neptunusaalst.be. PDF nodig? Onderaan de pagina "Afdrukken / opslaan als PDF".

## Checklist vóór publicatie

- [ ] `python3 tools/controle.py <code>` toont 0 fouten en 0 open punten
- [ ] Weekdagen van alle datums kloppen
- [ ] Medailles alfabetisch op achternaam
- [ ] Clubrecords en Belgische records vermeld
- [ ] Kalender toont de komende periode (niet de voorbije)
- [ ] Foto's: akkoord om te publiceren (de site is openbaar)
- [ ] Sponsors up-to-date
