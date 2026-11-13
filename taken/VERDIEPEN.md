# Taak 2: verdiepingen en keuzes voor morgen (05:12)

Lees eerst `taken/REGELS.md`. Deze taak schrijft de verdieping die T gisteren koos (en zijn eigen voorstellen) en zet 5 nieuwe keuzes klaar.

## Stappen

1. **Context lezen.** `context/profile.md`, `context/tech-stack.md`, `context/projects.md`, `context/editorial-guide.md`, `context/verdieping.yml`, de onderwerpen en `interest_areas` in `context/interests.yml`, en `data/feedback.json`.
2. **Wat schrijven?** Draai `python scripts/next_deepdive.py`:
   - `NIET NU`: geen verdieping en **geen** nieuwe keuzes. Schrijf alleen het taakverslag ("niet in de nacht gestart") en stop.
   - `SCHRIJVEN: <id> (issue #n)`: schrijf die verdieping volgens **Verdiepingen** hieronder. Er kunnen er meerdere zijn: de gewone keuze en hooguit 2 eigen voorstellen van T (zie **Eigen onderwerp**). Schrijf ze allemaal.
   - `AL GESCHREVEN`: niets schrijven; sluit het issue met `Closes #n` in een commit.
   - `ONBEKENDE KEUZE`: niets schrijven; zet het in het taakverslag.
   - `LATER`: komt een volgende nacht; niets doen.
   - `GEEN KEUZE` of `ONBEKEND`: vandaag geen verdieping.
3. **Na elke verdieping opslaan** (REGELS: tussendoor opslaan). Commit `Verdieping: <id>` met `Closes #<n>` op een eigen regel.
4. **Nieuwe keuzes.** Maak 5 nieuwe keuzes in `data/deepdive_options.json` volgens **Dagelijkse keuzes** hieronder. Opslaan, commit `Keuzes voor morgen`.
5. **Afronden.** Taakverslag `data/runs/<datum>-verdiepen.json` (in `counts`: `verdiepingen` en `keuzes`) en opslaan.

## Verdiepingen

Een verdieping is een langer stuk over een onderwerp dat T nog minder goed kent. Heeft het onderwerp `level: beginner` (of gaat het over ingestion, release pipelines of bundles, zie `context/profile.md` §2), begin dan bij de basis: wat is het, waarom bestaat het, een vergelijking uit het dagelijks leven, en dan pas de details en de eigen stack. T kiest het onderwerp zelf in de app, uit de 5 keuzes van gisteren. Het script geeft de gekozen keuze terug: de `question` en `why` bepalen waar het stuk over gaat.

### Eigen onderwerp (`eigen-...`)

T kan in de app zelf iets op "Jouw lijst" zetten ("Later bekijken") en daar een verdieping van laten maken. Het script meldt dan `SCHRIJVEN: eigen-<slug>` met `"own": true`, de `title` (het onderwerp in T's woorden), soms een `question` (zijn notitie) en `seen_in` (waar hij het las).

- Schrijf over precies dat onderwerp; de notitie zegt waar T benieuwd naar is. Ontbreekt die, beantwoord dan: wat is het, waarvoor gebruik je het, hoe pas je het toe in T's stack, en waar let je op.
- Zoek het op in de actuele officiële documentatie en recente bronnen; verzin niets. Bestaat het onderwerp niet of kun je er niets betrouwbaars over vinden, schrijf dan niets en meld het.
- `id` en `plan_id` zijn de `eigen-...`-sleutel uit het script; ook de bestandsnaam. Verder hetzelfde formaat (met quiz en begrippen).

### Dagelijkse keuzes

Elke run zet je 5 nieuwe keuzes klaar. T kiest er in de app één; die schrijf je de volgende ochtend.

- **Waar komen ze vandaan?** Combineer:
  - het nieuws van de afgelopen dagen (`data/feed.json` en de werklijst): wat roept een "hoe werkt dat eigenlijk?"-vraag op;
  - de interessegebieden en hun richtverdeling in `context/interests.yml` (`interest_areas`) en de leerdoelen in `context/profile.md` §2;
  - de ideeënlijst in `context/verdieping.yml` (onderwerpen en regels).
- **Trends:** is er een trend in `data/trends.json`, maak dan van minstens één trend een keuze (`why` noemt de trend).
- **Basiskennis:** staan er in `context/verdieping.yml` open onderwerpen met `level: beginner` (nog geen verdieping over geschreven), neem er dan elke dag minstens één als keuze op, met hetzelfde `id`. Zo komt T's ontbrekende basiskennis (ingestion, release pipelines, bundles) regelmatig langs.
- **Spreiding:** de 5 keuzes komen uit minstens 3 verschillende interessegebieden. Volg ongeveer de verdeling 30/30/20/20; zet het gebied in `area`.
- **Vers:** niet iets waar al een verdieping over is (`data/deepdives/`), en niet dezelfde 5 als gisteren. Een keuze die gisteren niet is gekozen mag terugkomen, maar hooguit 2 per dag.
- **Afwisseling in soort:** bijvoorbeeld één uitleg van een concept, één vergelijking van aanpakken, één praktische bouwsteen voor de eigen stack, één onderwerp uit het nieuws.
- **Per keuze:**
  - `id`: korte sleutel, kleine letters en koppeltekens (bijv. `reranking-bij-rag`). Wordt later de bestandsnaam.
  - `title`: hooguit 80 tekens, Nederlands, zegt waar het over gaat.
  - `question`: de vraag die de verdieping beantwoordt.
  - `why`: één zin waarom dit nu interessant is (bijv. een artikel van deze week, of een lopend project).
  - `topics`: 1 tot 3 id's uit `interests.yml`. `area`: id uit `interest_areas`.
- **Bestand:** verplaats de keuzes van gisteren naar `history` (bewaar hooguit de laatste 60) en zet de nieuwe in `options`:

```json
{
  "format_version": 1,
  "generated_at": "2026-10-30T06:20:00Z",
  "options": [
    {"id": "reranking-bij-rag", "title": "...", "question": "...", "why": "...", "topics": ["ai_context_engineering"], "area": "context_agents"}
  ],
  "history": []
}
```

### Actualiteit (belangrijkste regel)

- Schrijf alleen over technieken, werkwijzen en tools die **nu** de gangbare of aanbevolen aanpak zijn. Geen verouderde technieken, tools of productnamen.
- Zoek eerst recente bronnen (bij voorkeur van de laatste twaalf maanden). Een oudere bron mag alleen voor een basisidee dat nog steeds klopt, en altijd naast een recente bron.
- Controleer elke product- of functienaam in de **actuele officiële documentatie** (Azure Databricks, dbt, Microsoft). Is iets hernoemd of vervangen, gebruik dan de nieuwe naam en aanpak.
- Schrijf in `currency_check` kort hoe je dat gecontroleerd hebt: op welke datum, uit welke periode de bronnen komen, en wat je bewust níet hebt opgenomen omdat het verouderd is.

### Bronnen en betrouwbaarheid

- Lees 2 tot 5 goede bronnen volledig: officiële documentatie, erkende vakmensen (zie redactiegids, Opiniestukken), of degelijke technische artikelen. Geen marketing.
- Verzin niets. Elk feit, getal en elke naam komt uit een bron die je hebt gelezen. Meningen schrijf je toe ("volgens Husain…").
- Zet de gelezen bronnen in `further_reading`, met per bron in één zin waarom hij het lezen waard is. Alleen links die je zelf hebt geopend.

### Opbouw

- Schrijf volgens de redactiegids (§1: eenvoudig Nederlands, korte zinnen, Engelse term tussen haakjes bij eerste gebruik, één vergelijking per nieuw begrip).
- 5 tot 7 onderdelen (`sections`), elk met een korte kop en 2 tot 4 alinea's. Samen 6 tot 10 minuten lezen. Een logische lijn is: waarom bestaat dit · hoe werkt het · wat zijn de keuzes en valkuilen · waar zijn experts het oneens · hoe ziet het eruit in de eigen stack · wat betekent het voor een lopend project.
- Leg begrippen die in `profile.md` §2 als bekend staan niet uit.
- `experiment`: een proef van hooguit een middag, alleen met openbare of verzonnen data. Externe AI alleen zonder werkdata.
- `limitations`: 2 tot 4 korte zinnen over beperkingen, kosten of risico's, met aandacht voor zorgdata waar dat speelt.
- `showcase`: volgens **Zien** hieronder, als het onderwerp zich ervoor leent.
- `terms`: volgens **Begrippen** hieronder.
- `quiz`: **3 controlevragen** over de kern van het stuk, zodat T merkt of het is blijven hangen. Per vraag 3 of 4 antwoorden, precies één goed (`answer` is de index, vanaf 0), en een `explanation` van 1 of 2 zinnen. Vraag naar begrip (waarom, wanneer kies je wat), niet naar losse namen of getallen. De foute antwoorden zijn geloofwaardig, maar volgens het stuk echt fout. Zet het goede antwoord niet steeds op dezelfde plek.

### Formaat van `data/deepdives/<id>.json`

Gebruik de `id` van de gekozen keuze als bestandsnaam, `id` en `plan_id`.

```json
{
  "format_version": 1,
  "id": "<id van de gekozen keuze>",
  "plan_id": "<id van de gekozen keuze>",
  "request_issue": 12,
  "headline": "Nederlandse kop, hooguit ongeveer 70 tekens",
  "summary": "Twee of drie zinnen voor de kaart en de opening.",
  "sections": [{"heading": "Korte kop", "paragraphs": ["Alinea.", "Alinea."]}],
  "experiment": "Een proef van hooguit een middag, zonder werk- of patiëntdata.",
  "limitations": ["Korte zin"],
  "further_reading": [{"label": "Titel (auteur of organisatie, maand jaar)", "url": "https://...", "note": "Waarom lezen."}],
  "quiz": [{"question": "Vraag?", "options": ["A", "B", "C"], "answer": 1, "explanation": "Waarom B klopt."}],
  "currency_check": "Gecontroleerd op <datum>: ...",
  "topics": ["<1 tot 4 id's uit interests.yml>"],
  "written_at": "2026-10-29T06:30:00Z",
  "processed_by": "Claude (geplande taak)",
  "prompt_version": "verdieping-v2"
}
```

Een voorbeeld staat in `data/deepdives/evals-ai-assistent.json`.

## Zien: `showcase`

T leert het best als hij het ziet. Lezen alleen blijft te abstract. Voeg daarom waar het past dit blok toe (bij artikelen én verdiepingen):

**`showcase` – "Zo ziet het eruit"**: een klein stukje echte code (SQL, dbt-YAML, Python, een commando) met, als het kan, het resultaat eronder.
- Gebruik het als het artikel over iets gaat dat je in code of configuratie doet. Bij puur nieuws of een mening laat je het weg.
- **Verzin geen productnotatie.** Staat de exacte syntax in de bron of de officiële documentatie, gebruik die. Zo niet, laat dan het idee zien in gewone SQL of Python en zeg dat in `note` ("zo werkt het idee in gewone SQL; de notatie in X staat in de documentatie").
- Bij een SQL-voorbeeld met resultaat: draai het echt in DuckDB (`python -c "import duckdb; ..."`) op een klein verzonnen dataset en neem de echte uitkomst over (hooguit 12 rijen). Geen werk- of patiëntdata.
- Hooguit ongeveer 25 regels code. `note` zegt alleen wat een lezer anders verkeerd zou aannemen: welke notatie uit de documentatie komt, of wat in het voorbeeld is nagebouwd of anders werkt. Schrijf er niet in dat de data verzonnen is of dat je het in DuckDB draaide; dat is vanzelfsprekend. Is er niets te melden, laat `note` leeg.

```json
"showcase": {"caption": "Wat je ziet, in één of twee zinnen.", "language": "sql", "code": "SELECT ...",
             "result": {"columns": ["kolom"], "rows": [["waarde"]]}, "note": "De notatie staat in de Databricks-documentatie."}
```

Voorbeelden staan in `data/enrichment/60e7e131218f.json` en `data/deepdives/evals-ai-assistent.json`.

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

## Feedback van T

`data/feedback.json` bevat onder `reads` de artikelen die T helemaal las (een licht positief signaal), en onder `votes` T's duimpjes per artikel (`v`: 1 of -1) met soms een reden. De pipeline stuurt de score er al op bij: 👍 en gelezen duwen het onderwerp omhoog; alleen een 👎 met reden `geen_interesse` of `niet_mijn_stack` duwt het onderwerp omlaag. Een 👎 zonder reden of om de kwaliteit gaat over dát artikel, niet over het onderwerp: blijf zulke onderwerpen gewoon uitleggen. Gebruik het daarnaast zelf:

- Weeg ze zoals T ze bedoelt: een duim omhoog is een sterk signaal ("dit is echt interessant", telt dubbel in de score). Gelezen is maar een benadering; trek daar zelf geen conclusies uit als er duimpjes zijn die iets anders zeggen.
- Lees vóór het uitleggen de stemmen van de laatste 30 dagen. Kijk naar het soort artikel, niet alleen het onderwerp.

Redenen bij 👎:
- `te_basic`: wees strenger bij `depth` en sla aankondigingen zonder inhoud vaker over. Leg minder basis uit.
- `niet_mijn_stack` of `geen_interesse`: sla vergelijkbare artikelen vaker over (met die reden in het `skipped`-bestand).
- `te_vaag`: maak het verhaal concreter (hoe werkt het, met een voorbeeld) of sla het over als de bron zelf vaag is.
- `oud_nieuws`: let beter op of iets echt nieuw is; sla herhalingen van bekend nieuws over.

Redenen bij 👍:
- `praktisch` (praktisch toepasbaar): geef artikelen met een concrete toepassing voorrang; voeg vaker een `showcase` toe en maak "wat kun je ermee" concreet.
- `goed_uitgelegd`: deze uitleg werkte. Lees de uitleg van dat artikel (`data/enrichment/<id>.json`) en houd die opbouw en dat niveau aan.
- `nieuw_voor_mij`: T leerde er iets nieuws van. Kies vaker artikelen die een nieuw concept of nieuwe techniek uitleggen, en neem het onderwerp mee bij de verdiepingskeuzes.
- `mijn_stack` (past bij mijn stack): geef artikelen over T's eigen tools (`context/tech-stack.md`) voorrang en leg vaker de link naar zijn stack.
- `meer_hiervan`: geef zulke artikelen voorrang, en neem het onderwerp mee bij de verdiepingskeuzes.
