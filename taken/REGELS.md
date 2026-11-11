# Gemeenschappelijke regels voor de nachttaken van de Data & AI Radar

De radar draait 's nachts in vier korte taken. Elke taak heeft een eigen bestand in `taken/`:

| Tijd (Nederland) | Taak | Bestand |
|---|---|---|
| 04:12 | Uitleggen: nieuwe artikelen | `taken/UITLEGGEN.md` |
| 05:12 | Verdiepen: verdieping(en) en 5 keuzes voor morgen | `taken/VERDIEPEN.md` |
| 06:12 | Overzicht: trends, interesses, begrippen aanvullen, zondag Jouw week | `taken/OVERZICHT.md` |
| 07:27 | Inhalen: alleen wat vannacht nog ontbreekt | `taken/INHALEN.md` |

Lees dit bestand en daarna alleen het bestand van jouw taak.

## Altijd

- **Verzin niets.** Alleen wat in de bron, de officiële documentatie of de data staat. Weet je iets niet, laat het weg.
- **Nooit patiënt- of werkdata**, ook niet in voorbeelden, experimenten of codevoorbeelden. Alleen verzonnen of openbare data.
- **Geen sleutels of geheimen** in bestanden.
- Schrijf in eenvoudig Nederlands, zoals in `context/editorial-guide.md`.
- Wie T is: `context/profile.md`, `context/tech-stack.md`, `context/projects.md`. Lees die als je taak over inhoud gaat.
- Alles wat T kiest, hoort pas de volgende ochtend in de app. Scripts die zeggen `NIET NU` volg je altijd.

## Welke bestanden je mag aanpassen

Alleen: `data/enrichment/`, `data/deepdives/`, `data/deepdive_options.json`, `data/trends.json`, `data/weekly.json`, `data/interest_suggestions.json`, `data/interest_log.json`, `data/interest_requests.json`, `data/leerregels.json`, `data/runs/`, `data/run-request`, en (alleen bij T's verzoeken in Overzicht) `context/interests.yml`. Nooit `app/`, `pipeline/`, `scripts/`, `.github/` of andere contextbestanden.

## Starten

1. `git pull` op `main`, daarna `pip install -r requirements.txt`.
2. Noteer de starttijd (UTC) voor het taakverslag.

## Tussendoor opslaan

Sla op na elk afgerond onderdeel, niet pas aan het eind. Zo blijft werk bewaard als de taak halverwege stopt:

1. `python scripts/validate_enrichment.py` moet `0 fout` geven. Los fouten eerst op.
2. `git add` alleen de bestanden van dat onderdeel, commit met een korte Nederlandse boodschap.
3. `git pull --rebase` en `git push`. Lukt de push niet, probeer het nog één keer na `git pull --rebase`.

## Taakverslag (altijd, ook als er niets te doen was)

Schrijf aan het eind `data/runs/<datum>-<taak>.json`, met de datum in Nederlandse tijd (`TZ=Europe/Amsterdam date +%F`) en `<taak>` = `uitleggen`, `verdiepen`, `overzicht` of `inhalen`:

```json
{"task": "uitleggen", "started_at": "2026-11-02T03:12:40Z", "finished_at": "2026-11-02T03:58:10Z",
 "status": "ok", "summary": "12 artikelen uitgelegd (4 met voorbeeld), 3 overgeslagen",
 "counts": {"uitgelegd": 12, "overgeslagen": 3}, "problems": []}
```

- `status`: `ok` (alles gedaan), `deels` (een deel lukte niet) of `mislukt`.
- `summary`: één zin in gewoon Nederlands; de app toont die op de pagina Status.
- `problems`: korte zinnen over wat niet lukte.
Sla het verslag op zoals hierboven (valideren, committen, pushen).

## Afsluiten

Geef een korte samenvatting in het Nederlands van wat je deed.
