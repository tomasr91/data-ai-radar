# Taak voor Claude: artikelen uitleggen en verdiepingen schrijven

Deze taak draait elke nacht om 04:12 als geplande Claude-taak, nadat GitHub Actions om 02:47 de nieuwe artikelen heeft opgehaald. Jij (Claude) schrijft per artikel de uitleg die de app toont (tabblad **Actueel**), en de verdieping die T de dag ervoor koos (tabblad **Verdieping**). Daarna bouwt GitHub Actions de feed opnieuw en zet de app online.

## Stappen

1. **Bijwerken.** `git pull` op `main`, daarna `pip install -r requirements.txt`.
   - **Vers ophalen afdwingen.** De geplande GitHub-run start soms uren te laat of niet. Kijk naar `generated_at` in `data/feed.json`. Is die niet van vandaag (UTC), schrijf dan de datum van vandaag (`date -u +%F`) in `data/run-request`, commit alleen dat bestand ("Ophalen aangevraagd <datum>") en push. Die push start "Radar bijwerken" direct. Wacht daarna tot `data/feed.json` van vandaag is: elke 30 seconden `git pull`, hooguit 10 minuten. Lukt het niet binnen 10 minuten, ga dan door met de werklijst die er is en meld dat.
2. **Context lezen.** Lees `context/profile.md`, `context/tech-stack.md`, `context/projects.md`, `context/editorial-guide.md` en de onderwerp-id's in `context/interests.yml`. De redactiegids is leidend voor stijl en structuur.
3. **Werklijst lezen.** Open `data/to_enrich.json`. Is `items` leeg, sla stap 4 over en meld "Niets te verwerken" voor de artikelen.
4. **Per artikel** (in volgorde, **maximaal 15 per run**):
   1. Open de `url` en lees het **volledige artikel**. Werk nooit alleen op de titel of de `excerpt`.
   2. Is de pagina niet te lezen (betaalmuur, fout, geen inhoud)? Schrijf dan `data/enrichment/skipped/<id>.json` met `{"article_id", "url", "reason", "checked_at"}` en ga door naar het volgende artikel.
   3. Valt het artikel onder **"Niet uitleggen"** hieronder? Schrijf dan ook een `skipped`-bestand, met als `reason` welke regel het is, en ga door.
   4. Schrijf anders `data/enrichment/<id>.json` volgens het formaat hieronder. Gebruik precies de `id` uit de werklijst als bestandsnaam en als `article_id`.
5. **Verdieping.** Draai `python scripts/next_deepdive.py`.
   - `SCHRIJVEN: <id> (issue #n)`: schrijf één verdieping over die keuze volgens het hoofdstuk **Verdiepingen** hieronder. Onthoud het issuenummer.
   - `AL GESCHREVEN` of `ONBEKENDE KEUZE`: schrijf niets voor dat issue; noem het in de melding. Bij `AL GESCHREVEN` mag je het issue sluiten met `Closes #n` in de commit.
   - `GEEN KEUZE` of `ONBEKEND`: vandaag geen verdieping.
6. **Trends.** Werk `data/trends.json` bij volgens **Trends** hieronder (mag een lege lijst zijn).
6b. **Alleen op zondag (datum in Europe/Amsterdam): Jouw week.** Schrijf `data/weekly.json` volgens **Jouw week** hieronder, ná het uitleggen, zodat de artikelen van vannacht meetellen.
7. **Nieuwe keuzes.** Maak **altijd** 5 nieuwe keuzes voor morgen in `data/deepdive_options.json`, volgens **Dagelijkse keuzes** hieronder.
8. **Controleren.** Draai `python scripts/validate_enrichment.py`. Los elke fout op tot het resultaat `0 fout` is.
9. **Opslaan.** `git add data/enrichment data/deepdives data/deepdive_options.json data/trends.json` (op zondag ook `data/weekly.json`), commit met `Uitleg: <aantal> artikelen` (plus `, verdieping: <id>` als je er een schreef). Schreef je een verdieping, zet dan `Closes #<n>` op een eigen regel in de commitboodschap: GitHub sluit het issue dan vanzelf. Daarna `git pull --rebase` en `git push`.
10. **Melden.** Geef een korte samenvatting: hoeveel verwerkt, hoeveel overgeslagen en waarom, welke verdieping is geschreven, de trends, op zondag de 3 hoogtepunten van Jouw week, en de titels van de 5 nieuwe keuzes.

## Weekoverzicht Claude Code

Artikelen met een titel als "Claude Code: wat is er nieuw in week 43 (v2.1.304 t/m v2.1.310)" zijn weekoverzichten die de pipeline zelf maakt. De `excerpt` noemt de links naar de release notes.

- Open **elke** release-link uit de `excerpt` (of `CHANGELOG.md` in github.com/anthropics/claude-code) en lees alle wijzigingen van die week.
- Kies alleen wat T moet weten: nieuwe functies, gewijzigd gedrag, en dingen die je werkwijze met Claude Code veranderen (skills, hooks, subagents, MCP, contextbeheer, permissies). Laat bugfixes en kleine verbeteringen weg.
- Kop: de belangrijkste verandering, niet "Weekoverzicht". Het verhaal behandelt de 2 tot 4 belangrijkste wijzigingen. `key_facts` noemt per wijziging de versie.
- Waar het past: één zin over wat je ermee kunt bij dbt- of data-engineeringwerk.
- Alleen bugfixes en kleine verbeteringen die week? Dan overslaan met reden "alleen kleine wijzigingen".
- `availability_status`: `beschikbaar`, tenzij de release notes iets als preview of experimenteel noemen.

## Weekoverzicht Azure Databricks

Azure Databricks publiceert tientallen losse release notes per week. Die komen niet meer los in de app; de pipeline maakt per afgeronde week één artikel "Azure Databricks: wat is er nieuw in week 43". De `excerpt` noemt elke note met een stukje tekst en de links.

- Lees de notes in de `excerpt` en open de links van de notes die ertoe lijken te doen.
- Kies wat T moet weten voor zijn werk: wat algemeen beschikbaar wordt (GA) of standaard aangaat, wat gaat verdwijnen of anders werkt (end of life, wijzigingen in gedrag of API's), en nieuwe functies voor Lakeflow/pipelines, Unity Catalog, SQL, bundels, jobs en AI op het dataplatform. Laat losse modelnamen, prijs- en regio-meldingen en kleine UI-dingen weg.
- Kop: de belangrijkste verandering. Het verhaal behandelt de 3 tot 5 belangrijkste wijzigingen, met bij elke wijziging of het preview, bèta of GA is. `key_facts` noemt per wijziging de status en datum.
- Zit er iets bij dat T zelf iets moet doen (iets wordt uitgezet, een API-gedrag verandert)? Zet dat bovenaan.
- `availability_status`: de status van de belangrijkste wijziging.

## Zien: `showcase`

T leert het best als hij het ziet. Lezen alleen blijft te abstract. Voeg daarom waar het past dit blok toe (bij artikelen én verdiepingen):

**`showcase` – "Zo ziet het eruit"**: een klein stukje echte code (SQL, dbt-YAML, Python, een commando) met, als het kan, het resultaat eronder.
- Gebruik het als het artikel over iets gaat dat je in code of configuratie doet. Bij puur nieuws of een mening laat je het weg.
- **Verzin geen productnotatie.** Staat de exacte syntax in de bron of de officiële documentatie, gebruik die. Zo niet, laat dan het idee zien in gewone SQL of Python en zeg dat in `note` ("zo werkt het idee in gewone SQL; de notatie in X staat in de documentatie").
- Bij een SQL-voorbeeld met resultaat: draai het echt in DuckDB (`python -c "import duckdb; ..."`) op een klein verzonnen dataset en neem de echte uitkomst over (hooguit 12 rijen). Geen werk- of patiëntdata.
- Hooguit ongeveer 25 regels code. `note` zegt waar het vandaan komt of wat is nagebouwd.

```json
"showcase": {"caption": "Wat je ziet, in één of twee zinnen.", "language": "sql", "code": "SELECT ...",
             "result": {"columns": ["kolom"], "rows": [["waarde"]]}, "note": "Verzonnen data; ..."}
```

Voorbeelden staan in `data/enrichment/60e7e131218f.json` en `data/deepdives/evals-ai-assistent.json`.

## Niet uitleggen (overslaan met reden)

De radar toont alleen **must-knows**. Sla deze artikelen over:

- **Kleine updates**: een losse kleine functie, een UI-aanpassing, uitrol naar een extra regio, een nieuwe versie zonder inhoudelijke wijziging, een verzameloverzicht van veel kleine dingen.
- **Nieuwe connectoren** voor bronsystemen (bijv. "X connector is available in Beta"). Een driver of koppeling tussen tools uit de eigen stack (bijv. Power BI ↔ Databricks) is géén connector in deze zin en mag wel.
- **Klantverhalen zonder concrete aanpak**: het artikel moet noemen **welke tools** ze gebruiken en **wat de toepassing** is (wat bouwden ze, hoe werkt het). Alleen resultaten, citaten of marketing: overslaan.
- **Power BI en Fabric**: alleen grote functies die algemeen beschikbaar worden, wijzigingen in de koppeling met Databricks, of functies die stoppen. De rest overslaan.

**Opiniestukken mogen wel**, als de auteur een erkende vakpersoon is en de mening onderbouwd is (zie redactiegids §2, *Opiniestukken*). Zet dan `"article_type": "opinie"` en `"author"`. Sla over met reden: een opinie van een niet-erkende auteur, een stuk zonder onderbouwing, een verkooppraatje, of een stuk buiten het vakgebied (bijv. over sport of politiek).

Twijfel je? Vraag je af: "Moet T dit weten om zijn werk goed te blijven doen of een kans niet te missen?" Zo nee, overslaan.

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

## Feedback van T

`data/feedback.json` bevat onder `reads` de artikelen die T helemaal las (een licht positief signaal), en onder `votes` T's duimpjes per artikel (`v`: 1 of -1) met soms een reden: `te_basic`, `niet_mijn_stack`, `oud_nieuws`, `te_vaag`, `geen_interesse` of `meer_hiervan`. De pipeline stuurt de score er al op bij. Gebruik het daarnaast zelf:

- Lees vóór het uitleggen de stemmen van de laatste 30 dagen. Kijk naar het soort artikel, niet alleen het onderwerp.
- Veel `te_basic`: wees strenger bij `depth` en sla aankondigingen zonder inhoud vaker over. Leg minder basis uit.
- `niet_mijn_stack` of `geen_interesse`: sla vergelijkbare artikelen vaker over (met die reden in het `skipped`-bestand).
- `te_vaag`: maak het verhaal concreter (hoe werkt het, met een voorbeeld) of sla het over als de bron zelf vaag is.
- `meer_hiervan`: geef zulke artikelen voorrang, en neem het onderwerp mee bij de verdiepingskeuzes.

## Regels

- **Verzin niets.** Gebruik alleen wat in het artikel staat. Staat iets er niet in, laat het veld dan leeg (`""`) in plaats van te raden.
- Schrijf volgens **formaat 2** uit de redactiegids (§1 en §2): een Nederlandse kop, een doorlopend verhaal van 3 tot 5 korte alinea's, en de feiten apart in `key_facts`.
- `key_facts` bevat **alleen feiten uit de bron**: wat, sinds wanneer, welke status, welke cijfers. Elk feit dat in het verhaal staat, staat ook hier.
- Verbind het verhaal met het profiel, de stack en de projecten alleen als dat iets toevoegt. Herhaal niet bij elk artikel hetzelfde (bijvoorbeeld steeds hetzelfde project).
- **Centrale vraag bij elk artikel:** wat is er nieuw, waarom is het interessant, **hoe werkt het**, en welke mogelijkheden biedt het? Het verhaal legt altijd uit hoe het werkt, niet alleen dát het bestaat. Het doel is bijblijven én leren.
- **Concreet boven concept.** Staan er code, een repository, een benchmark of een reproduceerbaar experiment in het artikel, benoem dat dan en zet de link in `official_docs`.
- **Agents:** maak duidelijk welke taak de agent uitvoert, welke informatie hij nodig heeft en hoe gecontroleerd wordt of het resultaat klopt.
- **Claude en AI-ondersteunde ontwikkeling:** alleen Claude en het eigen ecosysteem (Claude Code, skills, hooks, subagents, MCP). Nieuwe modellen of tools van andere aanbieders alleen als het uitzonderlijk is (`general_ai_trends`). Laat waar het kan zien hoe je Claude inzet bij dbt, data engineering of context engineering.
- **Repositories en open source:** beoordeel of het echt iets nieuws toevoegt. Werkende code, goede uitleg en een duidelijke toepassing: ja. Een bestaand concept opnieuw verpakt: overslaan.
- **Marketingclaims** zijn geen bewezen mogelijkheden. Zeg het als iets alleen beweerd wordt.
- **Klantverhaal?** Noem in het verhaal en in `key_facts` welke tools ze gebruiken en wat ze ermee bouwden. Begin met de toepassing, niet met het bedrijf.
- `experiment` is een suggestie. Een experiment past binnen een middag en gebruikt **nooit patiëntgegevens of werkdata**, alleen synthetische of openbare data. Externe AI (zoals Claude zelf) alleen zonder werkdata. AI binnen Databricks mag wel met werkdata.
- `availability_status`: `beschikbaar` (GA), `preview` (Beta/Public Preview), `aangekondigd`, `experimenteel` of `onbekend`. Zegt het artikel het niet, dan `onbekend`.
- `official_docs`: alleen links die in het artikel staan of die je op de officiële documentatiesite hebt geopend. Nooit zelf een URL opbouwen.
- `topics`: alleen id's uit `interests.yml`, de best passende eerst. Kies er 1 tot 4.
- `quality` (0 tot 1), wees streng:
  - `depth`: 0,2 = aankondiging zonder details · 0,5 = enige uitleg · 0,8+ = code, cijfers of architectuur
  - `practicality`: hoe direct toepasbaar in deze stack
  - `novelty`: 0,2 = herhaling van iets ouds · 0,8+ = echt nieuw
- `development_key`: een korte sleutel voor de ontwikkeling (bijv. `uc-data-classification-okt-2026`). Gebruik dezelfde sleutel als een ander artikel over dezelfde ontwikkeling gaat. De pipeline groepeert ze dan.
- `date_note`: vul in als de datum twijfelachtig is (bijv. alleen 'laatst bewerkt', of een herpublicatie).
- `article_type`: `nieuws` (standaard, mag je weglaten) of `opinie`. Bij `opinie` is `author` verplicht: naam plus waarom erkend, bijv. `"Benn Stancil, oprichter van Mode"`. Schrijf de mening altijd toe aan de auteur en zet in `key_facts` zijn kernpunten.
- `exceptional: true` alleen bij een grote, bevestigde wijziging in een tool uit de eigen stack.
- Schrijf in eenvoudig Nederlands. Zet de Engelse vakterm bij het eerste gebruik tussen haakjes. Geen marketingtaal.
- Wijzig nooit iets in `context/`, `app/` of `pipeline/`. Deze taak schrijft alleen in `data/enrichment/`.

## Formaat van `data/enrichment/<id>.json`

```json
{
  "format_version": 2,
  "article_id": "<id uit de werklijst>",
  "url": "<url uit de werklijst>",
  "headline": "Nederlandse kop, hooguit ongeveer 70 tekens",
  "summary": "Eén of twee zinnen voor de kaart in de lijst.",
  "story": [
    "Alinea 1: wat gebeurde er.",
    "Alinea 2: hoe werkt het, met een vergelijking.",
    "Alinea 3: wat betekent het voor deze stack of dit project."
  ],
  "key_facts": ["Feit uit de bron met precieze cijfers of datum.", "..."],
  "personal_relevance": "Eén zin: waarom dit telt voor mij.",
  "experiment": "Een klein experiment van hooguit een middag, zonder werk- of patiëntdata.",
  "limitations": ["Korte zin", "Korte zin"],
  "availability_status": "beschikbaar | preview | aangekondigd | experimenteel | onbekend",
  "official_docs": [{"label": "Naam", "url": "https://..."}],
  "topics": ["ai_context_engineering", "dbt_analytics_engineering"],
  "quality": {"depth": 0.7, "practicality": 0.8, "novelty": 0.6},
  "development_key": "korte-sleutel",
  "date_note": "",
  "exceptional": false,
  "article_type": "nieuws | opinie",
  "author": "Alleen bij opinie: naam, en waarom erkend",
  "processed_by": "Claude (geplande taak)",
  "processed_at": "2026-10-29T06:20:00Z",
  "prompt_version": "taak-v2"
}
```

Voorbeelden van goede uitleg staan al in `data/enrichment/` (bestanden met `"format_version": 2`). Kijk er één of twee na voordat je begint.

## Verdiepingen

Een verdieping is een langer stuk over een onderwerp dat T nog minder goed kent. Heeft het onderwerp `level: beginner` (of gaat het over ingestion, release pipelines of bundles, zie `context/profile.md` §2), begin dan bij de basis: wat is het, waarom bestaat het, een vergelijking uit het dagelijks leven, en dan pas de details en de eigen stack. T kiest het onderwerp zelf in de app, uit de 5 keuzes van gisteren. Het script geeft de gekozen keuze terug: de `question` en `why` bepalen waar het stuk over gaat.

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
- `showcase`: volgens **Zien** hierboven, als het onderwerp zich ervoor leent.
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
