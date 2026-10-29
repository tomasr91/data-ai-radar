---
id: projects
type: context
schema_version: 1
updated: 2026-10-29
---

# Projecten en projectthema's

Dit bestand bevat **tijdelijke context**: projecten veranderen, profiel en stack minder. De radar gebruikt alleen projecten met status `actief` of `idee` om nieuws te koppelen.

## Zo beheer je dit bestand

- **Toevoegen:** kopieer het sjabloon onderaan en vul het in. Kies een unieke `id` (kleine letters, koppeltekens).
- **Wijzigen:** pas velden aan en werk `bijgewerkt` bij.
- **Archiveren:** zet `status` op `gearchiveerd` en verplaats het blok naar "Archief". De radar negeert het dan.
- **Verwijderen:** verwijder het blok volledig.

**Statuswaarden:** `idee` · `actief` · `gepauzeerd` · `afgerond` · `gearchiveerd`.
**Stand 2026-10-29:** vier projecten zijn `actief`; `migratie-moderne-dataplatformen` is `gepauzeerd` en wordt door de radar genegeerd.

---

## Actieve en mogelijke projecten

### ai-contextlaag-dbt-databricks
- **Naam:** AI-contextlaag op dbt en Databricks
- **Status:** actief
- **Bijgewerkt:** 2026-10-28
- **Doel:** Metadata uit dbt en de catalogus zo ontsluiten dat een AI-assistent betrouwbare antwoorden kan geven over data: wat betekent een tabel, waar komt het vandaan, mag ik het gebruiken.
- **Technologieën:** dbt, Databricks, Unity Catalog, Power BI semantische modellen (Fabric)
- **Mogelijke AI-toepassingen:** vraag-en-antwoord over datasets; agent die dbt-documentatie en lineage raadpleegt; automatisch aanvullen van ontbrekende beschrijvingen.
- **Randvoorwaarde:** AI binnen Databricks mag; externe AI alleen zonder werkdata.
- **Open vragen:** welke metadata is nu compleet genoeg? Wie gaat de assistent gebruiken?
- **Radar let op:** `ai_context_engineering`, `metadata_lineage_catalogs`, `ai_agents_rag`, `dbt_analytics_engineering`

### ai-voor-data-engineering-en-kwaliteit
- **Naam:** AI voor data-engineering en datakwaliteit
- **Status:** actief
- **Bijgewerkt:** 2026-10-28
- **Doel:** Repetitief werk (modellen, tests, documentatie) sneller en consistenter maken, en kwaliteitsproblemen eerder vinden.
- **Technologieën:** dbt (Core en platform), Databricks, GitHub, Azure DevOps, eigen dbt-generatorscripts
- **Mogelijke AI-toepassingen:** testvoorstellen per model; afwijkingen in data signaleren en uitleggen; AI-review van pull requests.
- **Open vragen:** welke kwaliteitsproblemen kosten nu de meeste tijd? Hoe wordt kwaliteit nu gemeten?
- **Radar let op:** `data_quality_observability`, `ai_on_data_platform`, `cicd_data_deployment`

### metadata-lineage-vindbaarheid
- **Naam:** Metadata, lineage en vindbaarheid van data
- **Status:** actief
- **Bijgewerkt:** 2026-10-28
- **Doel:** Collega's (en AI) laten vinden welke data er is, wat het betekent en waar het vandaan komt.
- **Technologieën:** dbt docs, Unity Catalog, Power BI (Fabric)
- **Mogelijke AI-toepassingen:** beschrijvingen en tags laten voorstellen; zoeken in gewone taal; impactanalyse via lineage.
- **Open vragen:** welke catalogus is leidend? Wie is eigenaar van definities?
- **Radar let op:** `metadata_lineage_catalogs`, `data_governance_privacy`

### ai-in-de-zorg-zorg-en-onderzoeksdata
- **Naam:** AI binnen de zorginstelling (zorg- en onderzoeksdata)
- **Status:** actief
- **Bijgewerkt:** 2026-10-28
- **Doel:** Verkennen welke AI-toepassingen verantwoord kunnen op zorg- en onderzoeksdata, en welke randvoorwaarden daarvoor nodig zijn.
- **Technologieën:** Azure Databricks, Unity Catalog, `[aanvullen]` governance-tooling
- **Mogelijke AI-toepassingen:** kennisontsluiting van onderzoeksdocumentatie; ondersteuning bij datasetselectie voor onderzoek; gepseudonimiseerde analyses.
- **Open vragen:** welke regels en interne processen gelden (privacy, ethiek, toestemming)? Welke data mag naar welke omgeving?
- **Radar let op:** `ai_in_healthcare`, `ai_research_data`, `data_governance_privacy`

### migratie-moderne-dataplatformen
- **Naam:** Migratie en ontwikkeling van moderne dataplatformen
- **Status:** gepauzeerd — tijdelijk niet volgen (op verzoek, 2026-10-29)
- **Bijgewerkt:** 2026-10-28
- **Doel:** Het platform toekomstbestendig maken: schaalbaar, beheersbaar en klaar voor AI.
- **Technologieën:** dbt, Databricks, Spark SQL, SQL Server, GitHub
- **Mogelijke AI-toepassingen:** SQL-dialectvertaling met AI; automatisch vergelijken van uitkomsten oud vs. nieuw; documentatie genereren tijdens migratie.
- **Open vragen:** wat blijft na de migratie op SQL Server? Wat is de volgende stap voor het platform?
- **Radar let op:** `databricks_data_engineering`, `sql_spark_sql`, `data_architecture_modeling`, `dbt_analytics_engineering`

---

## Archief

_(leeg)_

---

## Sjabloon

```markdown
### <project-id>
- **Naam:**
- **Status:** idee | actief | gepauzeerd | afgerond | gearchiveerd
- **Bijgewerkt:** JJJJ-MM-DD
- **Doel:**
- **Technologieën:**
- **Mogelijke AI-toepassingen:**
- **Open vragen:**
- **Radar let op:** <interest-ids uit interests.yml>
```
