# Taak 1: artikelen uitleggen (04:12)

Lees eerst `taken/REGELS.md`. Deze taak schrijft per nieuw artikel de uitleg die de app toont (Actueel).

## Stappen

1. **Vers ophalen afdwingen.** Kijk naar `last_successful_update` in `data/feed.json` (wanneer de bronnen voor het laatst zijn opgehaald; `generated_at` zegt alleen wanneer de feed opnieuw is samengesteld). Is die niet van vandaag (UTC), schrijf dan de datum van vandaag (`date -u +%F`) in `data/run-request`, commit alleen dat bestand ("Ophalen aangevraagd <datum>") en push. Wacht daarna tot `last_successful_update` in `data/feed.json` van vandaag is: elke 30 seconden `git pull`, hooguit 10 minuten. Lukt het niet, ga door met de werklijst die er is en zet dat in het taakverslag.
1b. **Dataflow-voortgang.** Voeg `tomasr91/personal-data-platform` toe met add_repo (access **read**) en clone hem met `--depth 200` naast de radar. Draai `python scripts/dataflow_status.py <pad naar die clone>`: dat werkt `data/voortgang.json` bij. Controleer dat `stap` alleen een korte stapnaam is (geen paden, adressen of instellingen; anders maak je hem korter of leeg). Lukt toevoegen of clonen niet: sla deze stap over en ga door. **Uit die repository komt verder niets in de radar**: geen code, bestandsnamen of inhoud. Wijzig er niets in.
2. **Context lezen.** `context/profile.md`, `context/tech-stack.md`, `context/projects.md`, `context/editorial-guide.md` de onderwerp-id's in `context/interests.yml` en `context/rode-draad.yml` en `data/voortgang.json` (zie **Dataflow**). De redactiegids is leidend. Lees ook `data/feedback.json` (zie **Feedback van T**) en `data/taste.json` (zie **Past bij jou**).
3. **Werklijst.** Open `data/to_enrich.json`. Is `items` leeg: schrijf het taakverslag ("niets te verwerken") en stop.
4. **Per artikel** (in volgorde): ga door tot je **10 artikelen** hebt uitgelegd (vol en kort samen) of de lijst op is (er staan er hooguit 40). T wil elke dag hooguit 10 nieuwe artikelen. Overslaan telt niet mee: zo vult het volgende artikel de plek op. Artikelen met `"volledig": true` tellen niet mee voor de 10. De werklijst staat al in de goede volgorde (actueel eerst, een ouder artikel met een hoge score mag voor). Kies per artikel **vol**, **kort** of **overslaan** (zie **Vol, kort of overslaan**). Staat bij een artikel `"volledig": true`, dan vroeg T zelf om de volle uitleg: altijd vol, en overschrijf het bestaande korte bestand.
   0. Valt een artikel op titel en `excerpt` al **duidelijk** onder **overslaan** (buiten het vakgebied, dubbel)? Sla het dan over zonder de pagina te openen, met de regel als `reason`. Bij twijfel: openen.
   1. Open de `url` en lees het artikel: bij vol het **volledige artikel**, bij kort mag je vlotter lezen. Uitleggen nooit alleen op titel of `excerpt`.
   2. Niet te lezen (betaalmuur, fout, geen inhoud)? Schrijf `data/enrichment/skipped/<id>.json` met `{"article_id", "url", "reason", "checked_at"}` en ga door. Begin `reason` dan met "Niet te lezen": zo'n artikel komt na een week nog één keer terug op de werklijst (staat er al een `skipped`-bestand, overschrijf het).
   3. Moet het worden overgeslagen (zie **Vol, kort of overslaan**)? Ook een `skipped`-bestand, met de regel als `reason`.
   4. Anders: `data/enrichment/<id>.json` volgens **Formaat** hieronder. Vol: met begrippen (`terms`) en waar het past een `showcase`. Kort: alleen de velden van **Korte uitleg**.
   5. **Na elke 5 artikelen opslaan** (zie REGELS: tussendoor opslaan), commit `Uitleg: <aantal> artikelen`.
5. **Aanvullen.** Staan er artikelen in `data/to_tag.json`: zet in hun `data/enrichment/<id>.json` alleen de ontbrekende velden `soort`, `fit`, `labels` en/of `project_ref` (de rest niet aanraken; bij `project_ref` mag je één zin aan het verhaal toevoegen, zie **Dataflow**). Hooguit 20, opslaan met commit `Aanvullen: <aantal> artikelen`.
6. **Afronden.** Laatste artikelen opslaan, taakverslag `data/runs/<datum>-uitleggen.json` schrijven en opslaan.

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

## Vol, kort of overslaan

T wil meer artikelen zien en kiest zelf wat hij leest (5-11-2026). Daarom:

- **Vol**: de must-knows hieronder. Een volle uitleg zoals altijd.
- **Kort**: wel binnen T's vakgebied, maar geen must-know: een kleine update, een preview, een klantverhaal met weinig aanpak, een kleinere Power BI- of Fabric-functie. Kort = een Nederlandse kop, twee zinnen samenvatting, `soort`, `fit` en `labels` (zie **Korte uitleg**). Wil T meer, dan tikt hij op "Volledig uitleggen".
- **Overslaan** (met reden): buiten het vakgebied (bijv. een plugin voor financieel adviseurs), een nieuwe connector voor een bronsysteem (T wil die niet zien), dubbel (bijv. de video bij een artikel dat al is uitgelegd), niet te lezen, of pure marketing zonder inhoud.

Hieronder: wat **vol** krijgt. Wat daar niet onder valt maar wel binnen het vakgebied ligt, wordt **kort** (niet meer overslaan).

## Korte uitleg

```json
{
  "format_version": 2, "diepte": "kort",
  "article_id": "<id>", "url": "<url>",
  "headline": "Nederlandse kop, hooguit ongeveer 70 tekens",
  "summary": "Twee zinnen: wat is het en voor wie is het handig.",
  "topics": ["..."], "availability_status": "preview",
  "quality": {"depth": 0.3, "practicality": 0.4, "novelty": 0.4},
  "soort": "aankondiging", "fit": {"score": 0.5, "why": "..."}, "labels": ["..."], "project_ref": null,
  "development_key": "korte-sleutel",
  "processed_by": "Claude (geplande taak)", "processed_at": "2026-11-05T03:20:00Z", "prompt_version": "taak-v3-kort"
}
```

Dezelfde regels: niets verzinnen, `quality` streng. Geen `story`, `key_facts`, `terms` of `showcase` nodig.

## Wat vol krijgt (anders kort)

Let op de **ondergrens per gebied** (`min_articles` bij `interest_areas` in `interests.yml`): de werklijst zet artikelen uit gebieden die te weinig in de app hebben (vaak Claude en nieuwe technologie) vooraan. Sla die niet over omdat ze minder bij dbt aansluiten; alleen om de regels hieronder.

Een volle uitleg krijgen alleen de **must-knows**. Deze artikelen worden **kort** (niet vol):

- **Kleine updates**: een losse kleine functie, een UI-aanpassing, uitrol naar een extra regio, een nieuwe versie zonder inhoudelijke wijziging, een verzameloverzicht van veel kleine dingen.
- **Nieuwe connectoren** voor bronsystemen (bijv. "X connector is available in Beta"): overslaan, niet kort. Een driver of koppeling tussen tools uit de eigen stack (bijv. Power BI ↔ Databricks) is géén connector in deze zin en mag wel.
- **Klantverhalen zonder concrete aanpak**: het artikel moet noemen **welke tools** ze gebruiken en **wat de toepassing** is (wat bouwden ze, hoe werkt het). Alleen resultaten, citaten of marketing: overslaan.
- **Power BI en Fabric**: vol alleen bij grote functies die algemeen beschikbaar worden, wijzigingen in de koppeling met Databricks, of functies die stoppen. De rest kort.

**Opiniestukken mogen wel vol**, als de auteur een erkende vakpersoon is en de mening onderbouwd is (zie redactiegids §2, *Opiniestukken*). Zet dan `"article_type": "opinie"` en `"author"`. Een opinie van een niet-erkende auteur of zonder onderbouwing: kort. Een verkooppraatje of een stuk buiten het vakgebied (bijv. over sport of politiek): overslaan.

Twijfel je tussen vol en kort? Vraag je af: "Moet T dit weten om zijn werk goed te blijven doen of een kans niet te missen?" Zo nee: kort.

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

## Past bij jou

`data/taste.json` bevat T's laatste 20 duimpjes (met reden) en 10 gelezen artikelen, elk met titel, onderwerpen, bron, soort, labels en `score` (de score op het moment van de duim). Een duim omhoog bij een lage score (bijv. 55) zegt het meest: T vond het veel interessanter dan de radar dacht. Een duim bij 90 zegt weinig. Geef elk artikel dat je uitlegt een `fit`: hoe goed past het bij wat T daar waardeert?

- `score` 0 tot 1: 0,5 = geen idee of neutraal, 0,8+ = lijkt sterk op zijn duimen omhoog, 0,2- = lijkt op zijn duimen omlaag. Telt hooguit 10 punten mee.
- `why`: één korte zin met de vergelijking, bijv. "Praktisch dbt-stuk met code, zoals je incrementele-modellenartikel."
- Kijk naar de inhoud en de soort, niet alleen het onderwerp: een aankondiging over dbt is niet hetzelfde als een praktische dbt-uitleg. Weinig duimen? Blijf dicht bij 0,5.

## Dataflow (rode draad)

T bouwt in zijn eigen tijd een persoonlijk data-engineering- en AI-platform: "Dataflow" (`context/rode-draad.yml`, 8 fases, van inrichting tot eigen agent). Hij wil artikelen daaraan kunnen ophangen.

- Helpt een artikel **duidelijk** bij een fase (iets wat hij in die fase moet doen, kiezen of begrijpen)? Laat dat dan **in de tekst** aan bod komen: één zin in het verhaal (bij kort: in `summary`) die het verband concreet maakt, bijv. "Voor Dataflow is dit de manier om in fase 4 de historie van KNMI-metingen bij te houden." Zet daarna `project_ref`:
  `"project_ref": {"fase": 4, "quote": "<die zin, of een stuk ervan van minstens 15 tekens, letterlijk>", "why": "Eén korte zin waarom."}`
- Geen duidelijk verband? Zet `"project_ref": null`. Niet forceren: liever geen verwijzing dan een gezochte.
- Let bij fase 1, 2, 5, 6 en 7 extra op wat wel en niet kan in **Databricks Free Edition**: dat is in het project een belangrijke vraag. Noem het als het artikel het zegt; verzin het niet.
- **Hoe ver T is** staat in `data/voortgang.json` (`huidig` = de fase waar hij nu aan werkt, `stap` = zijn laatste stap, `fases` = klaar/bezig/open). Helpt een artikel bij de fase waar hij **nu** zit of de volgende, maak de zin dan zo concreet mogelijk voor die stap (bijv. "Dit is precies wat je na het ophalen van KNMI-data nodig hebt om Bronze te laden."). Bij een fase die al klaar is: hooguit "handig om je fase 2 nog eens langs te lopen". Verzin geen details over zijn repository: je kent alleen de fase en de stapnaam.
- Een artikel met `project_ref` krijgt voorrang: 8 punten bij de huidige fase, 6 bij de volgende, 5 bij latere en 3 bij een afgeronde fase. De app markeert de zin en noemt de fase ("hier ben je nu").

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
- `soort`: `praktisch` (hoe je iets doet, met stappen of code), `aankondiging` (nieuwe functie of product), `release` (versie- of releasenotes), `achtergrond` (uitleg van een concept of architectuur), `praktijk` (hoe een organisatie het deed) of `mening`. Kies de beste.
- `labels`: 2 tot 4 korte labels voor waar het artikel precies over gaat, fijner dan een onderwerp. Kleine letters met streepjes, bijv. `metric-views`, `dbt-semantic-layer`, `lakeflow`, `unity-catalog-abac`, `claude-code-skills`. **Hergebruik** een label uit `labels_in_use` in `data/taste.json` als dat hetzelfde bedoelt; maak alleen een nieuw label voor iets nieuws. Geen algemene labels als `databricks`, `ai` of `data`. De radar leert hiermee wat T binnen een onderwerp wel en niet interessant vindt.
- `exceptional: true` alleen bij een grote, bevestigde wijziging in een tool uit de eigen stack.
- Schrijf in eenvoudig Nederlands. Zet de Engelse vakterm bij het eerste gebruik tussen haakjes. Geen marketingtaal.

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
  "soort": "praktisch | aankondiging | release | achtergrond | praktijk | mening",
  "fit": {"score": 0.7, "why": "Eén korte zin: lijkt op welke duimen van T."},
  "labels": ["metric-views", "dbt-semantic-layer"],
  "project_ref": {"fase": 4, "quote": "Letterlijk stuk uit het verhaal", "why": "Eén korte zin."},
  "author": "Alleen bij opinie: naam, en waarom erkend",
  "terms": [{"term": "Zoals in de tekst", "explanation": "Eén of twee korte zinnen."}],
  "processed_by": "Claude (geplande taak)",
  "processed_at": "2026-10-29T06:20:00Z",
  "prompt_version": "taak-v2"
}
```

Voorbeelden van goede uitleg staan al in `data/enrichment/` (bestanden met `"format_version": 2`). Kijk er één of twee na voordat je begint.
