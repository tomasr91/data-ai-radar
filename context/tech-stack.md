---
id: tech-stack
type: context
schema_version: 1
updated: 2026-10-29
---

# Technische stack

Overzicht van mijn technische omgeving, gegroepeerd per categorie. Per categorie: wat **bekend** is, welke **ontwikkelingen** de radar moet volgen, welke **toepassingen** interessant zijn en wat nog **ontbreekt**.

**Labels:** `[bekend]` · `[aanname]` · `[aanvullen]` — zie `profile.md`.
**Let op:** "Ontwikkelingen om te volgen" zijn zoekrichtingen voor de radar, geen claims over wat ik gebruik. Versies en configuraties staan hier pas als ik ze zelf invul.

Elke categorie verwijst naar een `id` in `interests.yml`.

---

## 1. dbt en analytics engineering
`interest: dbt_analytics_engineering`

- **Bekend:**
  - `[bekend]` dbt wordt gebruikt voor transformaties in een Bronze/Silver/Gold-opzet.
  - `[bekend]` Zowel dbt Core als het dbt-platform (Cloud) zijn in gebruik.
  - `[bekend]` Eigen Python-scripts genereren dbt-modellen en metadata-YAML voor bronze en silver.
- **Ontwikkelingen om te volgen:** nieuwe dbt-releases en engine-ontwikkelingen, functies die alleen in het dbt-platform zitten versus Core, wijzigingen in tests en contracts, semantische laag/metrics, AI-functies binnen dbt, wijzigingen in de dbt–Databricks-adapter.
- **Toepassingen:** de generatorscripts uitbreiden met AI-voorstellen voor beschrijvingen en tests, dbt-metadata als context voor AI.
- **Ontbreekt:** `[aanvullen]` welke taken in Core en welke in het platform draaien · versies · gebruikte packages · aantal modellen.

## 2. Databricks, Spark en Spark SQL
`interest: databricks_data_engineering`, `sql_spark_sql`

- **Bekend:**
  - `[bekend]` Azure Databricks.
  - `[bekend]` Opslag in Delta Lake, beheer via Unity Catalog.
  - `[bekend]` AI binnen Databricks (AI-functies, model serving) mag worden gebruikt.
- **Ontwikkelingen om te volgen:** Azure Databricks release notes, Unity Catalog, Spark SQL-functies, serverless compute, pipelines/orchestratie, ingebouwde AI-functies in SQL, Databricks Asset Bundles voor deployment.
- **Toepassingen:** AI-functies direct in SQL op Silver-data, kostenoptimalisatie, betere orchestratie.
- **Ontbreekt:** `[aanvullen]` gebruikte compute-type · orchestratietool · runtime-versies.

## 3. SQL Server en datamodellering
`interest: data_architecture_modeling`, `sql_spark_sql`

- **Bekend:**
  - `[bekend]` SQL Server is onderdeel van de omgeving.
- **Ontwikkelingen om te volgen:** modelleringspatronen (dimensioneel, Data Vault, wide tables) in een lakehouse.
- **Toepassingen:** AI-ondersteunde SQL-review, consistente modelconventies afdwingen.
- **Ontbreekt:** `[aanvullen]` modelleringsmethode per laag.

## 4. Bronze-, Silver- en Gold-architectuur
`interest: data_architecture_modeling`

- **Bekend:** `[bekend]` Medaillonarchitectuur in gebruik.
- `[bekend]` Bronsystemen o.a. HiX (Chipsoft) en AFAS.
- **Ontwikkelingen om te volgen:** ontwerppatronen per laag, historisering, incrementele verwerking, "AI-ready" gold-lagen.
- **Toepassingen:** heldere laagdefinities als context voor AI, automatische controle op laagconventies.
- **Ontbreekt:** `[aanvullen]` definitie per laag (wat mag wel/niet) · naamgevingsconventies · historiseringsaanpak.

## 5. Power BI en semantische modellen
`interest: powerbi_semantic_models`

- **Bekend:** `[bekend]` Power BI en semantische modellen in gebruik, binnen Microsoft Fabric.
- **Ontwikkelingen om te volgen:** Power BI feature-updates, Fabric-ontwikkelingen die Power BI raken, Copilot in Power BI, semantische modellen als bron voor AI, koppeling Fabric–Databricks/Unity Catalog.
- **Toepassingen:** vragen stellen aan semantische modellen, metrics eenduidig definiëren tussen dbt en Power BI.
- **Ontbreekt:** `[aanvullen]` licentievorm/capaciteit · connectiemodus naar Databricks · of Copilot in Power BI is toegestaan.

## 6. GitHub, CI/CD en deployment
`interest: cicd_data_deployment`

- **Bekend:** `[bekend]` GitHub voor versiebeheer; CI/CD via Azure DevOps.
- **Ontwikkelingen om te volgen:** CI-patronen voor dbt (slim CI, state-aware runs), Azure DevOps-pipelines voor dbt en Databricks, deployment van Databricks-assets, AI-code-review van data-code.
- **Toepassingen:** automatische PR-review van dbt-modellen, kwaliteitschecks in de pipeline.
- **Ontbreekt:** `[aanvullen]` omgevingen (dev/test/prod) · branchingstrategie · hoe dbt Core-runs worden aangestuurd.

## 7. AI op het dataplatform
`interest: ai_on_data_platform`

- **Bekend:** `[bekend]` Ik onderzoek toepassingen van AI op het dataplatform.
- **Ontwikkelingen om te volgen:** AI-functies in Databricks en dbt, model serving, AI voor data-engineeringtaken (genereren, testen, documenteren).
- **Toepassingen:** classificeren of samenvatten van vrije tekst in een gecontroleerde omgeving, AI-hulp bij modelontwikkeling.
- **Toegestaan:** `[bekend]` AI binnen Databricks; externe AI (zoals Claude of ChatGPT) alleen **zonder werkdata**.
- **Ontbreekt:** `[aanvullen]` of er een formeel AI-beleid komt · of Microsoft Copilot/Azure OpenAI later beschikbaar komt.

## 8. Context engineering, RAG en AI-agents
`interest: ai_context_engineering`, `ai_agents_rag`

- **Bekend:** `[bekend]` Interesse in context engineering, AI-agents, RAG en betrouwbare data voor AI.
- **Ontwikkelingen om te volgen:** contextlagen op dbt/Unity Catalog-metadata, MCP-koppelingen naar data-tools, evaluatie van agents, retrieval-patronen.
- **Toepassingen:** een agent die vragen beantwoordt op basis van dbt-documentatie en lineage, een "data-assistent" voor collega's.
- **Ontbreekt:** `[aanvullen]` bestaande experimenten · gebruikte LLM-aanbieders of frameworks.

## 9. Data governance, metadata en lineage
`interest: metadata_lineage_catalogs`, `data_governance_privacy`, `data_quality_observability`

- **Bekend:** `[bekend]` Interesse in governance, metadata, lineage en datakwaliteit.
- **Ontwikkelingen om te volgen:** catalogusfuncties, kolom-lineage, tags en classificatie, privacy-by-design, observability-tools.
- **Toepassingen:** automatisch tags en beschrijvingen voorstellen, lineage gebruiken voor impactanalyse.
- **Ontbreekt:** `[aanvullen]` welke catalogus leidend is · hoe gevoelige data wordt geclassificeerd · bestaande kwaliteitsmonitoring.
