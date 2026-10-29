# Taak voor Claude: artikelen uitleggen en verdiepingen schrijven

Deze taak draait elke ochtend als geplande Claude-taak, nadat GitHub Actions de nieuwe artikelen heeft opgehaald. Jij (Claude) schrijft per artikel de uitleg die de app toont (tabblad **Actueel**), en ongeveer twee keer per week een verdieping (tabblad **Verdieping**). Daarna bouwt GitHub Actions de feed opnieuw en zet de app online.

## Stappen

1. **Bijwerken.** `git pull` op `main`, daarna `pip install -r requirements.txt`.
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
6. **Nieuwe keuzes.** Maak **altijd** 5 nieuwe keuzes voor morgen in `data/deepdive_options.json`, volgens **Dagelijkse keuzes** hieronder.
7. **Controleren.** Draai `python scripts/validate_enrichment.py`. Los elke fout op tot het resultaat `0 fout` is.
8. **Opslaan.** `git add data/enrichment data/deepdives data/deepdive_options.json`, commit met `Uitleg: <aantal> artikelen` (plus `, verdieping: <id>` als je er een schreef). Schreef je een verdieping, zet dan `Closes #<n>` op een eigen regel in de commitboodschap: GitHub sluit het issue dan vanzelf. Daarna `git pull --rebase` en `git push`.
9. **Melden.** Geef een korte samenvatting: hoeveel verwerkt, hoeveel overgeslagen en waarom, welke verdieping is geschreven, en de titels van de 5 nieuwe keuzes.

## Weekoverzicht Claude Code

Artikelen met een titel als "Claude Code: wat is er nieuw in week 43 (v2.1.304 t/m v2.1.310)" zijn weekoverzichten die de pipeline zelf maakt. De `excerpt` noemt de links naar de release notes.

- Open **elke** release-link uit de `excerpt` (of `CHANGELOG.md` in github.com/anthropics/claude-code) en lees alle wijzigingen van die week.
- Kies alleen wat T moet weten: nieuwe functies, gewijzigd gedrag, en dingen die je werkwijze met Claude Code veranderen (skills, hooks, subagents, MCP, contextbeheer, permissies). Laat bugfixes en kleine verbeteringen weg.
- Kop: de belangrijkste verandering, niet "Weekoverzicht". Het verhaal behandelt de 2 tot 4 belangrijkste wijzigingen. `key_facts` noemt per wijziging de versie.
- Waar het past: één zin over wat je ermee kunt bij dbt- of data-engineeringwerk.
- Alleen bugfixes en kleine verbeteringen die week? Dan overslaan met reden "alleen kleine wijzigingen".
- `availability_status`: `beschikbaar`, tenzij de release notes iets als preview of experimenteel noemen.

## Niet uitleggen (overslaan met reden)

De radar toont alleen **must-knows**. Sla deze artikelen over:

- **Kleine updates**: een losse kleine functie, een UI-aanpassing, uitrol naar een extra regio, een nieuwe versie zonder inhoudelijke wijziging, een verzameloverzicht van veel kleine dingen.
- **Nieuwe connectoren** voor bronsystemen (bijv. "X connector is available in Beta"). Een driver of koppeling tussen tools uit de eigen stack (bijv. Power BI ↔ Databricks) is géén connector in deze zin en mag wel.
- **Klantverhalen zonder concrete aanpak**: het artikel moet noemen **welke tools** ze gebruiken en **wat de toepassing** is (wat bouwden ze, hoe werkt het). Alleen resultaten, citaten of marketing: overslaan.
- **Power BI en Fabric**: alleen grote functies die algemeen beschikbaar worden, wijzigingen in de koppeling met Databricks, of functies die stoppen. De rest overslaan.

**Opiniestukken mogen wel**, als de auteur een erkende vakpersoon is en de mening onderbouwd is (zie redactiegids §2, *Opiniestukken*). Zet dan `"article_type": "opinie"` en `"author"`. Sla over met reden: een opinie van een niet-erkende auteur, een stuk zonder onderbouwing, een verkooppraatje, of een stuk buiten het vakgebied (bijv. over sport of politiek).

Twijfel je? Vraag je af: "Moet T dit weten om zijn werk goed te blijven doen of een kans niet te missen?" Zo nee, overslaan.

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

Een verdieping is een langer stuk over een onderwerp dat T nog minder goed kent. T kiest het onderwerp zelf in de app, uit de 5 keuzes van gisteren. Het script geeft de gekozen keuze terug: de `question` en `why` bepalen waar het stuk over gaat.

### Dagelijkse keuzes

Elke run zet je 5 nieuwe keuzes klaar. T kiest er in de app één; die schrijf je de volgende ochtend.

- **Waar komen ze vandaan?** Combineer:
  - het nieuws van de afgelopen dagen (`data/feed.json` en de werklijst): wat roept een "hoe werkt dat eigenlijk?"-vraag op;
  - de interessegebieden en hun richtverdeling in `context/interests.yml` (`interest_areas`) en de leerdoelen in `context/profile.md` §2;
  - de ideeënlijst in `context/verdieping.yml` (onderwerpen en regels).
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
  "currency_check": "Gecontroleerd op <datum>: ...",
  "topics": ["<1 tot 4 id's uit interests.yml>"],
  "written_at": "2026-10-29T06:30:00Z",
  "processed_by": "Claude (geplande taak)",
  "prompt_version": "verdieping-v1"
}
```

Een voorbeeld staat in `data/deepdives/evals-ai-assistent.json`.
