---
id: profile
type: context
schema_version: 1
updated: 2026-10-31
---

# Profiel

Dit bestand beschrijft wie ik ben, wat ik al weet en hoe de Data & AI Radar uitleg op mij moet afstemmen. Het bevat **stabiele persoonlijke context**. Tijdelijke projectinformatie staat in `projects.md`, technologie in `tech-stack.md`.

**Labels:** `[bekend]` = door mij opgegeven · `[aanname]` = redelijke afleiding, nog bevestigen · `[aanvullen]` = ontbreekt nog.

## 1. Rol en achtergrond

- `[bekend]` Analytics engineer, met focus op datamodellering, data-engineering en visualisatie.
- `[bekend]` Werkzaam in een zorginstelling waar zorgdata en onderzoeksdata beschikbaar zijn.
- `[bekend]` Werk met datawarehouse-lagen volgens Bronze, Silver en Gold.
- `[aanvullen]` Teamgrootte, mijn verantwoordelijkheden binnen het team, en wie de AI-initiatieven in de organisatie trekt.

## 2. Kennisniveau

### Wat ik al goed ken — niet opnieuw uitleggen
- `[bekend]` Dagelijks gebruik van dbt, SQL, Power BI, semantische modellen en Git.
- `[bekend]` Medaillonarchitectuur (Bronze/Silver/Gold).
- `[bekend]` Gevorderd niveau in dimensioneel modelleren, SQL en dbt-basisbegrippen (models, tests, sources, macros).
- `[bekend]` Werkende kennis van Databricks en Spark SQL; diepere Spark-internals mogen kort worden uitgelegd.

### Waar ik mij verder in wil ontwikkelen
Vooral: hoe moderne data-engineeringtechnieken en AI elkaar versterken.
- `[bekend]` Context engineering.
- `[bekend]` AI-agents en toolgebruik (o.a. MCP).
- `[bekend]` RAG: embeddings, chunking en retrieval.
- `[bekend]` Metadata en lineage als context voor AI.
- `[bekend]` Kennisrepresentatie en knowledge graphs.
- `[bekend]` Evaluatie, tracing en observability van AI-systemen.
- `[bekend]` AI-ondersteunde softwareontwikkeling met Claude en Claude Code.
- `[bekend]` Data-architectuur, datakwaliteit, lineage, metadata, governance en automatisering.
- `[bekend]` Betrouwbare data beschikbaar maken voor AI.

Nieuwe begrippen mogen geïntroduceerd worden, maar zonder onnodig bij de basis te beginnen.

### Nog beginnersniveau — wel bij de basis beginnen
Hier heb ik nog weinig kennis. Leg de basis uit, met een vergelijking en een klein voorbeeld, en bouw rustig op.
- `[bekend]` **Data ingestion**: hoe data uit bronsystemen in het platform komt (batch/streaming, incrementeel laden, CDC, Auto Loader, Lakeflow).
- `[bekend]` **Release pipelines**: van ontwikkeling naar productie in Azure DevOps (stages, omgevingen, goedkeuringen).
- `[bekend]` **Databricks Asset Bundles**: een Databricks-project als code beschrijven en uitrollen.
- `[aanvullen]` Welke van deze onderwerpen het meest urgent zijn de komende 6–12 maanden.

## 3. Wat ik met de app wil bereiken

- **Op de hoogte blijven**: weten welke nieuwe technologieën, releases, tools en toepassingen relevant zijn, zonder alles zelf te hoeven lezen.
- **Blijven leren**: begrijpen hoe nieuwe concepten werken, welke mogelijkheden ze bieden en hoe ze aansluiten op wat ik al weet.
- Ook nieuwe technieken, onverwachte toepassingen en minder bekende projecten ontdekken die bij mijn interesses passen.
- Per ontwikkeling snappen: **wat is nieuw, waarom telt het voor mij, wat kan ik ermee**.
- Ideeën opdoen voor concrete experimenten en proof of concepts in mijn eigen omgeving.
- Mijn kennis verbreden buiten wat ik dagelijks doe, zonder basisuitleg over wat ik al ken.

## 4. Nieuws dat ik waardevol vind

**Wel:**
- Nieuwe of gewijzigde functies in tools die ik gebruik, met codevoorbeelden of releasedetails.
- Praktijkverhalen: hoe een team iets concreet heeft gebouwd, inclusief afwegingen.
- Patronen en architectuurkeuzes die herbruikbaar zijn.
- Ontwikkelingen rond AI + data die direct toepasbaar zijn op een dbt/Databricks-platform.
- Zorg- en privacy-relevante ontwikkelingen rond data en AI.
- `[bekend]` Onderbouwde meningen van erkende vakmensen over het vakgebied, ook zonder nieuwe functie of release.

**Niet:**
- Hype en algemene "AI verandert alles"-stukken.
- Funding- en overnamenieuws.
- AI voor beeld, video of muziek.
- Crypto en blockchain.
- Marketing zonder technische inhoud.
- Herhaling van oud nieuws in een nieuw jasje.

De harde uitsluitingen staan als `excluded_topics` in `interests.yml`.

**Richtverdeling** (flexibel, geen quota; details in `interests.yml` → `interest_areas`):

| Interessegebied | Richtpercentage |
|---|---|
| dbt, data engineering en data-architectuur | 30% |
| Context engineering en AI-agents | 30% |
| Claude en AI-ondersteunde ontwikkeling | 20% |
| Nieuwe technologieën en architectuurpatronen | 20% |

## 5. Hoe de AI mijn kennisniveau gebruikt

1. **Taal is altijd eenvoudig** (zie `editorial-guide.md`), ook bij gevorderde onderwerpen. Eenvoudige taal ≠ basisuitleg.
2. **Bekende begrippen** (zie §2) worden gebruikt zonder uitleg.
3. **Nieuwe begrippen** krijgen één korte uitleg met een vergelijking, op de plek waar ze voor het eerst voorkomen.
4. **Verdieping** (technische details, code, configuratie) staat los onder een kopje, zodat ik zelf kies of ik het lees.
5. **Koppel aan mijn situatie**: vergelijk nieuwe dingen met wat ik al gebruik ("dit lijkt op een dbt-test, maar dan…").

## 6. Manier van leren

- `[bekend]` Ik leer het liefst door te ontdekken hoe iets praktisch toepasbaar is in mijn eigen omgeving.
- `[aanname]` Een klein experiment werkt beter dan een lange theoretische uitleg.
- `[bekend]` Tijd voor lezen en experimenteren: 1–3 uur per week. Experimentideeën moeten dus klein zijn (een middag of minder).
- `[bekend]` Leesritme: een dagelijks kort overzicht.
- `[bekend]` Engelse vakterm tussen haakjes bij het eerste gebruik, bijv. "herkomst van data (lineage)".
