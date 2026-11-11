# Leerregels (onderdeel van taak 3: overzicht)

T kan bij een 👍 of 👎 in eigen woorden zeggen waarom ("Waarom?"). Jij zet dat om in een **leerregel** die ook nieuwe artikelen raakt. Het scoren zelf is vaste code (`pipeline/rules.py`); jij schrijft alleen de regels.

Je mag hiervoor **alleen** `data/leerregels.json` aanpassen.

## Stappen

1. `git pull`, lees `data/notes_todo.json` (duimen met een toelichting die je nog niet bekeek; per item `note`, `v` (1 = 👍, -1 = 👎), `r`, `title`, `topics`, `labels`, `soort`) en `data/leerregels.json`.
2. Per item: maak een regel, of bekijk het en maak er geen (zet dan `null`, zie hieronder).
3. `python scripts/validate_rules.py` moet `0 fouten` geven. Opslaan, commit `Leerregels`.

## Wanneer een regel

Een regel gaat over een **soort nieuws of een patroon**, niet over een heel onderwerp. Voorbeeld: "Per december stopt support voor versie 17.3, dat vind ik niet interessant" → regel "Einde van support voor versies" (richting -1), niet "Databricks minder".

- `text`: één korte zin in gewoon Nederlands, zoals T het zou zeggen; T ziet hem in de app.
- `richting`: `-1` bij 👎 of "minder hiervan", `1` bij 👍 of "meer hiervan".
- `keywords`: 3 tot 8 zoektermen (Nederlands én Engels waar nodig) die in de titel of samenvatting van zulke artikelen staan, bijv. `["end of support", "einde support", "end of life", "deprecation notice"]`. Elk minstens 4 tekens. Geen termen die ook in gewone artikelen over het onderwerp staan (dus niet "Databricks" of "update").
- `labels`: bestaande labels uit `data/taste.json` (`labels_in_use`) die precies dit soort artikelen dragen; mag leeg.
- `sterkte`: `1.0` als de toelichting duidelijk is, `0.5` bij twijfel over wat T bedoelt. Een regel met twijfel kan T zien en weghalen.
- `id`: kort, kleine letters met streepjes. `van`: het `id` van de duim. `at`: datum van vandaag. `active`: `true`.
- Heeft een eerdere regel al hetzelfde doel, pas die dan aan (trefwoorden aanvullen) in plaats van een tweede te maken; zet het nieuwe `van`-id in `noted` met het id van die regel.

```json
{
  "rules": [
    {"id": "einde-support", "text": "Einde van support voor versies", "richting": -1, "sterkte": 1.0,
     "keywords": ["end of support", "einde support", "end of life", "deprecation notice"], "labels": [],
     "van": "0123456789ab", "at": "2026-11-12", "active": true}
  ],
  "noted": {"0123456789ab": "einde-support", "ba9876543210": null}
}
```

## Wanneer geen regel (`null` in `noted`)

- De toelichting is onduidelijk, te kort of gaat over één artikel ("goed artikel", "te lang"): geen regel.
- Ze zegt alleen "niet mijn onderwerp" of "wel mijn onderwerp": dat is al de gewone duim (onderwerp-reden), geen regel.
- Een regel zou een heel aandachtsgebied raken (bijv. alles over dbt of Power BI): geen regel.
- Verzin geen bedoeling. Twijfel je, `null`.

Zet elk bekeken item in `noted`, ook bij `null`, anders komt het morgen weer terug.

## Wat je niet doet

- Regels van T die `active: false` zijn, laat je staan (hij haalde ze zelf weg).
- Geen werk- of patiëntgegevens in `text` of `keywords`.
