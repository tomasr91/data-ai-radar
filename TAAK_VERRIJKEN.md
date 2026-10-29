# Taak voor Claude: artikelen uitleggen

Deze taak draait elke ochtend als geplande Claude-taak, nadat GitHub Actions de nieuwe artikelen heeft opgehaald. Jij (Claude) schrijft per artikel de uitleg die de app toont. Daarna bouwt GitHub Actions de feed opnieuw en zet de app online.

## Stappen

1. **Bijwerken.** `git pull` op `main`, daarna `pip install -r requirements.txt`.
2. **Context lezen.** Lees `context/profile.md`, `context/tech-stack.md`, `context/projects.md`, `context/editorial-guide.md` en de onderwerp-id's in `context/interests.yml`. De redactiegids is leidend voor stijl en structuur.
3. **Werklijst lezen.** Open `data/to_enrich.json`. Is `items` leeg, stop dan en meld "Niets te verwerken".
4. **Per artikel** (in volgorde, **maximaal 15 per run**):
   1. Open de `url` en lees het **volledige artikel**. Werk nooit alleen op de titel of de `excerpt`.
   2. Is de pagina niet te lezen (betaalmuur, fout, geen inhoud)? Schrijf dan `data/enrichment/skipped/<id>.json` met `{"article_id", "url", "reason", "checked_at"}` en ga door naar het volgende artikel.
   3. Valt het artikel onder **"Niet uitleggen"** hieronder? Schrijf dan ook een `skipped`-bestand, met als `reason` welke regel het is, en ga door.
   4. Schrijf anders `data/enrichment/<id>.json` volgens het formaat hieronder. Gebruik precies de `id` uit de werklijst als bestandsnaam en als `article_id`.
5. **Controleren.** Draai `python scripts/validate_enrichment.py`. Los elke fout op tot het resultaat `0 fout` is.
6. **Opslaan.** `git add data/enrichment`, commit met `Uitleg: <aantal> artikelen`, `git pull --rebase`, `git push`.
7. **Melden.** Geef een korte samenvatting: hoeveel verwerkt, hoeveel overgeslagen en waarom.

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
