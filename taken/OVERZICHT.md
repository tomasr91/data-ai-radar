# Taak 3: overzicht (06:12)

Lees eerst `taken/REGELS.md`. Deze taak doet alles wat over de feed als geheel gaat.

## Stappen

1. **Context lezen.** `context/profile.md`, `context/editorial-guide.md`, `context/interests.yml`, `data/feedback.json`. `git pull` zodat je de uitleg van vannacht hebt.
2. **Trends.** Werk `data/trends.json` bij volgens **Trends** hieronder (een lege lijst mag). Opslaan, commit `Trends`.
3. **Interesses.** Draai `python scripts/interest_requests.py` en verwerk elke `VERWERKEN`-regel volgens **Mijn interesses** hieronder (wachtrij `data/interest_requests.json` daarna leeg: `{"requests": []}`). Bij `NIET NU`, `GEEN VERZOEKEN` of `ONBEKEND`: niets aan `context/interests.yml` veranderen. Opslaan, commit `Interesses aangepast` (met `Closes #n` voor losse issues).
4. **Begrippen aanvullen.** Hooguit 15 bestaande uitleg- of verdiepingsbestanden zonder `terms`, volgens **Begrippen** hieronder. Opslaan, commit `Begrippen aangevuld`.
5. **Alleen op zondag** (datum in Europe/Amsterdam):
   - `data/weekly.json` volgens **Jouw week** hieronder.
   - hooguit 3 voorstellen in `data/interest_suggestions.json` volgens **Mijn interesses** (voorstellen doen).
   - Opslaan, commit `Jouw week`.
6. **Afronden.** Taakverslag `data/runs/<datum>-overzicht.json` en opslaan.

## Trends

Een trend is een ontwikkeling of techniek waar nu meerdere bronnen tegelijk over schrijven, bijvoorbeeld "geheugen voor AI-agents" of "metric views als bron voor AI". Geen breed onderwerp als "AI-agents" of "Databricks".

- Kijk naar de uitgelegde artikelen in `data/feed.json` van de **laatste 21 dagen**.
- Een trend heeft **minstens 3 artikelen uit minstens 2 bronnen**. Hooguit **3 trends**; liever geen trend dan een geforceerde.
- `title`: hooguit 80 tekens, zegt wat er speelt. `summary`: 2 of 3 korte zinnen: wat is de gemeenschappelijke lijn, en waarom komt het nu op. Alleen wat in de artikelen staat.
- Een trend van gisteren die nog klopt, houd je met hetzelfde `id` en vul je aan.

```json
{
  "format_version": 1,
  "generated_at": "2026-10-30T06:20:00Z",
  "trends": [
    {"id": "geheugen-voor-agents", "title": "...", "summary": "...", "article_ids": ["<id>", "<id>", "<id>"], "topics": ["ai_agents_rag"]}
  ]
}
```

## Mijn interesses

T ziet in de app (tandwiel > Mijn interesses) zijn onderwerpen uit `context/interests.yml`, jouw voorstellen en een logboek. Wat hij wil veranderen komt als issue "Interesses: ..." binnen; `scripts/interest_requests.py` zet het om in een lijst. Je mag hiervoor **alleen** `context/interests.yml`, `data/interest_suggestions.json` en `data/interest_log.json` aanpassen; nooit het profiel, de bronnen of andere contextbestanden.

**Verzoeken verwerken (stap 3)**
- `onderwerp <id>: belangrijker` → `priority` één omhoog (hooguit 5). `minder` → één omlaag (minstens 1). `weg` → `enabled: false` (het onderwerp blijft staan, zodat het terug kan). `leren` → `learning: true` (leeronderwerp: geel lampje op de kaarten, uitleg bij de basis beginnen); `niet_leren` → haal `learning` weg.
- `voorstel <id>: JA` → voer het voorstel uit. Bij `nieuw`: voeg een onderwerp toe onder `topics` met een `id` in snake_case, `name`, `description` (2 of 3 zinnen), een bestaande `feed_group`, `enabled: true`, `priority: 3` (tenzij het voorstel iets anders zegt), 5 tot 15 specifieke `keywords` (geen losse woorden die ook in andere teksten staan) en `related_topics`; zet het `id` ook bij het passende gebied in `interest_areas`. Bij `belangrijker`/`minder`/`weg`: zoals hierboven.
- `voorstel <id>: NEE` → niets veranderen.
- Haal elk beantwoord voorstel (ja of nee) uit `data/interest_suggestions.json`.
- `in eigen woorden`: vertaal het naar concrete aanpassingen in `interests.yml` (prioriteit, zoekwoorden, omschrijving, `excluded_topics`). Is het onduidelijk of valt het buiten `interests.yml` (bijv. een nieuwe bron), verander dan niets en schrijf dat in het logboek.
- Zet `updated:` bovenin `interests.yml` op de datum van vandaag.
- Draai `python scripts/validate_context.py`. Bij een fout: herstel het, of zet `interests.yml` terug en meld het.
- Schrijf per wijziging één regel bovenaan `data/interest_log.json` (nieuwste eerst), in gewoon Nederlands:
  `{"changes": [{"at": "2026-11-02T04:40:00Z", "text": "Power BI en semantische modellen: van 'regelmatig' naar 'belangrijk' (jouw verzoek)."}, ...]}`
  Ook een afgewezen voorstel krijgt een regel ("Voorstel 'Data contracts' niet overgenomen (jouw nee)."), zodat je het niet snel opnieuw voorstelt.
- Zet `Closes #<n>` voor elk verwerkt issue in de commitboodschap.

**Voorstellen doen (stap 5, alleen op zondag)**
- Hooguit 3, en vervang de vorige (onbeantwoorde) voorstellen. Liever geen voorstel dan een zwak voorstel; een lege lijst mag.
- Soorten (`kind`): `nieuw` (een onderwerp dat er nog niet is), `belangrijker`, `minder` of `weg` (een bestaand onderwerp, met `topic`).
- Baseer je op: T's duimpjes, redenen en gelezen artikelen (`data/feedback.json`, laatste 4 weken); onderwerpen die vaak in het nieuws of in de werklijst zitten maar niet goed in `interests.yml` passen; overgeslagen artikelen; de leerdoelen in `context/profile.md`.
- `why`: één zin met het concrete bewijs ("kwam deze maand in 5 artikelen terug; 2 daarvan gaf je een 👍"). Verzin geen cijfers.
- Stel niets voor wat T in de laatste 8 weken heeft afgewezen (zie `data/interest_log.json`).

```json
{
  "generated_at": "2026-11-08T04:40:00Z",
  "suggestions": [
    {"id": "data-contracts", "kind": "nieuw", "name": "Data contracts", "description": "...", "why": "..."},
    {"id": "powerbi-belangrijker", "kind": "belangrijker", "topic": "powerbi_semantic_models", "why": "..."}
  ]
}
```

## Begrippen: `terms`

T heeft nog beginnersniveau in data-ingestion, bundels en release pipelines, en komt veel nieuwe termen tegen. Geef daarom bij elke uitleg (hooguit 5) en elke verdieping (hooguit 8) de begrippen die hij misschien nog niet kent. De app onderstreept ze in de tekst; tikken geeft de uitleg. Alle begrippen samen staan onder Verdieping > Begrippen.

- **Welke:** vaktermen, afkortingen en productonderdelen met een eigen betekenis (bijv. Auto Loader, ADBC, MCP, asset bundle, CDC, idempotent, service principal). **Niet** wat T dagelijks gebruikt: SQL, dbt, Databricks, Power BI, Delta Lake, Unity Catalog, model, tabel.
- **Letterlijk:** `term` staat precies zo in de tekst waarin de app onderstreept: bij artikelen in `story`, bij verdiepingen in `summary` of de alinea's van de secties. Anders keurt de controle het af. Kies de vorm die in de tekst staat.
- **Uitleg:** één of twee korte zinnen (hooguit 240 tekens), eenvoudig Nederlands: wat het is en waarvoor je het gebruikt. Geen herhaling van het artikel.
- **Zelfde uitleg:** staat het begrip al in `glossary` in `data/feed.json`, neem die uitleg over, tenzij hij niet klopt. Zo blijft de woordenlijst consistent.
- Geen lastige begrippen in het stuk? Laat `terms` weg.

```json
"terms": [{"term": "Auto Loader", "explanation": "Een functie in Databricks die nieuwe bestanden in cloudopslag vanzelf ziet en ze stap voor stap inleest, zonder dat je bijhoudt wat al verwerkt is."}]
```

**Aanvullen (elke run, na de werklijst):** uitlegbestanden van artikelen die nu in de app staan (`articles` in `data/feed.json`) maar nog geen `terms` hebben: voeg ze toe, hooguit 15 per run, nieuwste eerst. Verander verder niets aan die bestanden. Hetzelfde voor verdiepingen zonder `terms`. Noem het aantal in de melding.

## Jouw week (alleen op zondag)

Een kort overzicht dat T zondagochtend leest om de week af te sluiten. De app zet er zelf zijn quizscores, herhaalvragen en Leren-voortgang bij; jij schrijft alleen de inhoud.

- Kijk naar de uitgelegde artikelen in `data/feed.json` die de afgelopen 7 dagen in de app kwamen (`processed_at`), en naar de verdiepingen van die week.
- Kies de **3 belangrijkste ontwikkelingen** voor T's werk (dbt, Databricks, Power BI, Claude, AI-agents): wat verandert er echt voor hem. Liever iets dat in meerdere artikelen terugkomt dan één losse melding. Minder dan 3 mag in een rustige week.
- `title`: hooguit 90 tekens, de ontwikkeling zelf. `why`: 2 korte zinnen, wat het is en wat het voor T betekent. Alleen wat in de artikelen staat.
- `article_ids`: 1 tot 3 artikelen waar het in staat.
- `intro`: één zin over de week als geheel.
- `focus` (optioneel): één concreet ding om deze week te doen of uit te proberen, met een link naar een artikel of verdieping als dat kan. Geen werk- of patiëntdata.
- Eenvoudig Nederlands, zoals in de redactiegids.

```json
{
  "week": "2026-W44",
  "generated_at": "2026-11-01T04:40:00Z",
  "intro": "...",
  "highlights": [
    {"title": "...", "why": "...", "article_ids": ["<id>", "<id>"]}
  ],
  "focus": "..."
}
```

`week` is de ISO-week van de zondag zelf (`date +%G-W%V`).
