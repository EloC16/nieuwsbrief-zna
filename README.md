# Nieuwsbrief Competitiezwemmen Neptunus Aalst

Elke editie is een webpagina met een vaste template, gepubliceerd via GitHub Pages.

- **Alle edities:** https://eloc16.github.io/nieuwsbrief-zna/
- **Een editie:** `https://eloc16.github.io/nieuwsbrief-zna/edities/<code>/`, bijvoorbeeld `edities/2026-q2q3/`

Zie [WERKWIJZE.md](WERKWIJZE.md) voor hoe een editie gemaakt wordt.

## Opbouw

```
index.html              archief (lijst van alle edities, uit edities.json)
edities.json            volgorde van het archief, nieuwste bovenaan
assets/style.css        huisstijl (kleuren, lettertypes, printversie)
assets/render.js        zet data.json om in de pagina
edities/<code>/
  index.html            vaste template, niet aanpassen
  data.json             ALLE inhoud van de editie
  fotos/                foto's van die editie (verkleind, max ~1600px)
tools/nieuwe_editie.py  maakt een nieuwe editiemap aan
tools/controle.py       controleert datums (met weekdag), foto's en open punten
```

## data.json in het kort

| Veld | Betekenis |
|---|---|
| `concept` | `true` toont een gele "concept"-balk en de open punten; zet op `false` bij publicatie |
| `gepubliceerd` | publicatiedatum, `"2027-01-14"` |
| `wedstrijden.items[]` | per wedstrijd: `naam`, `plaats`, `van`, `tot`, `tekst`, `goud`/`zilver`/`brons` (lijst van `"Naam (100SS)"`), `finales` (`{"A-finale": [...]}`), `records`, `fotos` |
| `{"tussentitel": "..."}` | een tussenkopje tussen de wedstrijden, bv. Zomerkampioenschappen |
| `stages.items[]` | `titel`, `groep`, `van`, `tot`, `tekst`, `fotos` |
| `kalender.items[]` | `naam`, `plaats`, `van`, `tot`, `details`, `gewijzigd` (`true` toont een rood label 'Gewijzigd') |
| `extra.items[]` | `tag` (bv. "Save the date"), `titel`, `van`, `tekst`, `link`, `linktekst` |
| `sponsors.items[]` | `naam`, `logo` (pad naar afbeelding), `url` |
| `todo` | op elk item mogelijk: verschijnt als geel "nog te doen"-blok (niet in de printversie) |

Datums altijd als `JJJJ-MM-DD`; de weekdag wordt automatisch berekend.
In teksten: lege regel = nieuwe alinea, `**vet**`, links en e-mailadressen worden vanzelf klikbaar.
