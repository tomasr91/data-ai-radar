# Data & AI Radar

Een persoonlijke nieuwsapp die ontwikkelingen in data engineering, data-architectuur en AI verzamelt en vertaalt naar **praktische inzichten in eenvoudig Nederlands**. Per ontwikkeling beantwoordt de radar vier vragen:

1. Wat is er nieuw?
2. Waarom is dit relevant voor mijn werk?
3. Wat kan ik ermee in mijn eigen stack?
4. Welk experiment of proof of concept is mogelijk?

Versie 1 bestaat uit drie delen: de **context** (wat relevant is en hoe er geschreven wordt), een **pipeline** die artikelen ophaalt, uitlegt en scoort, en een **mobiele web-app** die het resultaat toont.

## Structuur

```
README.md                    ← dit bestand
context/
  profile.md                 ← wie ik ben, kennisniveau, leerwijze (stabiel)
  tech-stack.md              ← technologie per categorie (redelijk stabiel)
  projects.md                ← projecten en projectthema's (tijdelijk)
  interests.yml              ← onderwerpen, prioriteiten, scoringsregels
  verdieping.yml             ← ideeën en regels voor verdiepingen
  sources.yml                ← nieuwsbronnen en hun betrouwbaarheid
  editorial-guide.md         ← schrijfstijl, artikelstructuur, betrouwbaarheid
scripts/
  validate_context.py        ← controleert YAML en onderlinge verwijzingen
  validate_enrichment.py     ← controleert de uitlegbestanden
  make_site.py               ← maakt de map voor GitHub Pages
pipeline/                    ← ophalen → normaliseren → ontdubbelen → verrijken → scoren
  providers/feeds.py         ← live RSS/Atom/GitHub-releases
  providers/snapshot.py      ← vastgelegde momentopname
  build.py                   ← schrijft data/feed.json
data/
  snapshot/raw_items.json    ← momentopname van echte artikelen (28-10-2026)
  raw/                       ← ruwe laag: elke run ongewijzigd bewaard
  enrichment/<id>.json       ← uitleg per artikel (één keer verwerkt, daarna hergebruikt)
  archive.json               ← alle opgehaalde artikelen (60 dagen), zodat ze niet verdwijnen uit de feed
  to_enrich.json             ← werklijst voor Claude: welke artikelen nog uitleg nodig hebben
  enrichment/skipped/        ← artikelen die Claude niet kon lezen, met reden
  deepdives/<id>.json        ← verdiepingen (tabblad Verdieping), één per dag als je er een kiest
  deepdive_options.json      ← de 5 keuzes voor morgen (Claude maakt ze elke ochtend)
  feed.json                  ← klaar voor de app; het enige bestand dat de app leest
app/
  index.html                 ← de mobiele app (leest feed.json ernaast)
TAAK_VERRIJKEN.md            ← werkinstructie voor de geplande Claude-taak
.github/workflows/radar.yml  ← dagelijks ophalen, feed bouwen, app publiceren
tests/
  test_pipeline.py           ← unit tests pipeline
  e2e_app.py                 ← gebruikersstroom in headless Chromium op telefoonformaat
```

## Versie 1 gebruiken

```bash
pip install pyyaml                         # pipeline
python scripts/validate_context.py         # context controleren
python -m pipeline.build --provider feeds  # live ophalen (netwerk nodig)
python -m pipeline.build --provider snapshot   # of: de vastgelegde momentopname
cp data/feed.json app/feed.json            # app en feed naast elkaar
python -m http.server -d app 8000          # bekijk op http://localhost:8000
```

- **AI-uitleg** gebeurt alleen als `ANTHROPIC_API_KEY` is ingesteld (model te kiezen met `RADAR_MODEL`). Zonder sleutel werkt alles, maar nieuwe artikelen blijven 'onverwerkt' (titel, bron, datum, link). Bestaande uitleg in `data/enrichment/` wordt altijd hergebruikt; per run worden maximaal 15 nieuwe artikelen verwerkt (`--max-enrich`).
- **Testen:** `python -m unittest discover -s tests -t .` en `python tests/e2e_app.py` (vereist `pip install playwright && playwright install chromium`).
- **Modus** staat in de feed en bovenaan de app: `live`, `partial` (gedeeltelijk), `snapshot` (momentopname), `stale` (ophalen mislukt, vorige feed) of `demo`.
- **Feedcontrole** (icoon rechtsboven in de app) laat per bron zien of hij werkt, wat er is weggefilterd en waarom, en welke datums verdacht zijn.

### Relevantiescore

`score = 55% onderwerp + 20% inhoudelijke kwaliteit + 15% actualiteit + 10% bron`, met de prioriteiten uit `interests.yml`. Een artikel dat alleen een productnaam noemt, telt als zwakke match. Onder `min_relevance_score` komt niets in de feed, ook niet bij prioriteit 5. Uitgesloten onderwerpen vallen altijd weg. Details staan bovenaan `pipeline/score.py`.

## Draaien op GitHub (dagelijks, automatisch)

Zo werkt het elke ochtend:

1. **05:30 – GitHub Actions** (`.github/workflows/radar.yml`) haalt de feeds op, voegt nieuwe artikelen toe aan `data/archive.json` en bouwt `data/feed.json`. Onverwerkte artikelen die de moeite waard lijken, komen op de werklijst `data/to_enrich.json`. De app op GitHub Pages wordt bijgewerkt.
2. **Daarna – de geplande Claude-taak** voert `TAAK_VERRIJKEN.md` uit: leest elk artikel op de werklijst volledig, schrijft de uitleg naar `data/enrichment/<id>.json`, schrijft ongeveer twee keer per week een verdieping naar `data/deepdives/<id>.json` (onderwerp via `scripts/next_deepdive.py`), controleert die met `scripts/validate_enrichment.py` en pusht.
3. **Na die push** draait de workflow opnieuw. De nieuwe uitleg komt in de feed, en de app is bijgewerkt.

Een fout uitlegbestand komt nooit in de app: de pipeline negeert het en meldt het in de feedcontrole. Een artikel dat Claude niet kan lezen, komt in `data/enrichment/skipped/` en niet terug op de werklijst.

### Eenmalig instellen

1. Maak een repository aan en push deze map naar `main`.
2. **Settings → Pages → Source: GitHub Actions.** Pages vanuit een privé-repo vraagt een betaald GitHub-account; bij een openbare repo zijn ook `context/` en de code zichtbaar.
3. **Settings → Actions → General → Workflow permissions: Read and write.**
4. **Actions → Radar bijwerken → Run workflow** voor de eerste run. Daarna staat de app op `https://<gebruiker>.github.io/<repo>/`.
5. Laat Claude de geplande taak aanmaken (bijv. dagelijks om 07:10) met deze opdracht:

> Voeg de GitHub-repository `<gebruiker>/<repo>` toe met push-toegang en clone hem. Voer daarna de taak uit die beschreven staat in `TAAK_VERRIJKEN.md` in die repository, van stap 1 tot en met 8. Wijzig niets buiten `data/enrichment/` en `data/deepdives/`.

### Bron van artikelen vervangen

Een provider levert altijd dezelfde vorm (`ProviderResult`, zie `pipeline/providers/__init__.py`). Wil je later artikelen aanleveren als bestanden in de repo, dan schrijf je `providers/files.py` die dezelfde ruwe items teruggeeft. Normaliseren, verrijken, scoren, `feed.json` en de app blijven ongewijzigd.

## Functie per bestand

| Bestand | Bepaalt | Gelezen door | Hoe vaak wijzigen |
|---|---|---|---|
| `profile.md` | Voor wie wordt geschreven en welk niveau | AI-verrijking | Zelden |
| `tech-stack.md` | Koppeling van nieuws aan mijn tools | AI-verrijking | Bij stackwijziging |
| `projects.md` | Koppeling aan lopend werk | AI-verrijking, scoring | Maandelijks |
| `interests.yml` | Wat relevant is en hoe zwaar het weegt | Scoring (code) | Wanneer interesses veranderen |
| `sources.yml` | Waar nieuws vandaan komt | Verzameling (code) | Bij nieuwe bronnen |
| `editorial-guide.md` | Hoe een artikel eruitziet | AI-verrijking | Zelden |

**Afspraken in alle bestanden**
- Labels `[bekend]`, `[aanname]`, `[aanvullen]` geven aan hoe zeker informatie is.
- Onderwerpen worden overal aangeduid met hun `id` uit `interests.yml`.
- Markdown-bestanden hebben een frontmatter-kop (`id`, `schema_version`, `updated`) zodat software ze kan herkennen.

## Handmatig wijzigen

Alle zes contextbestanden zijn bedoeld om handmatig te wijzigen. Na een wijziging:

```bash
pip install pyyaml
python scripts/validate_context.py
```

### Nieuwe interesse toevoegen
1. Voeg in `interests.yml` onder `topics:` een blok toe met `id`, `name`, `description`, `enabled`, `priority` (1–5), `keywords` en `related_topics`.
2. Gebruik een unieke `id` in `snake_case`; `related_topics` mag alleen bestaande `id`'s bevatten.
3. Koppel eventueel bronnen door de `id` toe te voegen aan `topics:` in `sources.yml`.
4. Draai de validatie.

Uitzetten kan met `enabled: false`, zonder het onderwerp te verwijderen.

### Nieuwe bron toevoegen
1. Controleer het adres en de feed zelf (open de URL).
2. Voeg een blok toe in `sources.yml` met alle velden, inclusief `verification`.
3. Nog niet gecontroleerd? Zet `status: to_verify` en `enabled: false`.
4. Kies het juiste `type` en `trust_level` (definities staan bovenaan `sources.yml`).

## Wat nog ontbreekt

Zie de `[aanvullen]`- en `[aanname]`-labels in de bestanden. De belangrijkste:

- **Profiel:** teamgrootte en verantwoordelijkheden.
- **Stack:** versies (dbt, runtime), welke taken in dbt Core en welke in het dbt-platform draaien, compute en orchestratie, omgevingen en branchingstrategie, Power BI-capaciteit en -connectiemodus.
- **Bronnen:** geen bron voor AI in de zorg en onderzoeksdata; governance alleen via de Azure-feed. Vijf bronnen hebben status `user_supplied` en kunnen nog worden gecontroleerd.

## Scheiding van context, data en code

| Map | Inhoud | Wie schrijft | In versiebeheer |
|---|---|---|---|
| `context/` | Mijn voorkeuren en kennis | Ik (handmatig) | Ja |
| `data/` | Ruwe artikelen, uitleg en feed.json | De pipeline | `enrichment/` en `snapshot/` wel, `raw/` niet |
| `feedback/` (later) | Mijn reacties: nuttig, niet nuttig | De app | Nee, of apart |
| `app/`, `pipeline/`, `tests/` | Applicatiecode | Ik (ontwikkeling) | Ja |

Regels:
- De pipeline **leest** `context/`, maar **schrijft er nooit in**.
- Feedback wordt eerst opgeslagen als data. Pas als ik het bevestig, wordt het een wijziging in `interests.yml` of `profile.md`. Zo blijft de context controleerbaar.
- Geen geheimen of API-sleutels in deze repository; gebruik omgevingsvariabelen.

## Inlezen door een app of AI-pipeline

- **YAML** (`interests.yml`, `sources.yml`): inlezen als configuratie, valideren met `scripts/validate_context.py` (later eventueel met een JSON Schema of Pydantic-model).
- **Markdown** (`profile.md`, `tech-stack.md`, `projects.md`, `editorial-guide.md`): als tekst meegeven aan het taalmodel. De frontmatter wordt gebruikt voor versie en datum.
- **Reproduceerbaarheid:** sla bij elk verrijkt artikel een hash van de gebruikte contextbestanden op, plus model- en promptversie. Dan is altijd na te gaan waarom een artikel zo is geschreven.

---

## Architectuur (versie 1 gebouwd, uitbreidbaar)

Gedacht als een kleine datapipeline met dezelfde lagen als een dataplatform: **ruw → getransformeerd → klaar voor gebruik**.

```
 sources.yml                 interests.yml + profile/tech-stack/projects + editorial-guide
     │                                   │
 [1] Verzamelen ──► [2] raw_articles ──► [3] stg_articles ──► [4] AI-verrijking ──► [5] Scoring ──► [6] app_feed ──► [7] Mobiele app
                     (ruw, onveranderd)   (opgeschoond,        (samenvatting,       (relevantie,    (klaar voor        (lezen,
                                           ontdubbeld)          labels, status)      diversiteit)    gebruik)           feedback)
```

| Stap | Wat | Laag | Kerndefinitie |
|---|---|---|---|
| 1. Nieuwsverzameling | Feeds en pagina's ophalen volgens `sources.yml` | — | Eén run = één `fetch_run_id` |
| 2. Ruwe opslag | Inhoud ongewijzigd opslaan met ophaalmoment en bron | Ruw | Nooit overschrijven; alleen toevoegen |
| 3. Deduplicatie en metadata | URL normaliseren, dubbelingen samenvoegen, datum/titel/auteur extraheren | Getransformeerd | `article_id` = hash van genormaliseerde URL |
| 4. AI-verrijking | Samenvatting en artikel volgens `editorial-guide.md`, status en onderwerpen bepalen | Getransformeerd | Opslaan met model-, prompt- en contextversie |
| 5. Relevantiescore | Score op basis van `interests.yml`: prioriteit, gerelateerde onderwerpen, actualiteit, betrouwbaarheid, nieuwheid, diversiteit, uitzonderingsregel | Getransformeerd | Score is herberekenbaar zonder opnieuw AI aan te roepen |
| 6. Verrijkte opslag | Tabel met precies wat de app toont | Klaar voor gebruik | Eén rij per artikel per feed-datum |
| 7. Mobiele interface | Feed lezen, filteren, feedback geven | — | Feedback gaat naar `feedback/`, niet naar `context/` |

**Datakwaliteitscontroles** (eenvoudig te beginnen):
- Elk artikel heeft een bron-URL, bron-`id` en publicatiedatum.
- Geen dubbele `article_id` in de verrijkte laag.
- Elk verrijkt artikel heeft alle verplichte secties uit de redactiegids en een geldige statuswaarde.
- Elk onderwerp-label bestaat in `interests.yml`.
- Waarschuwing als een ingeschakelde bron dagen niets oplevert of als `to_verify`-bronnen aan staan.

### Eerste versie: zo eenvoudig mogelijk
- Python-script, dagelijks gedraaid (bijv. via een geplande GitHub Action of lokaal).
- Opslag in **SQLite of DuckDB** — één bestand, geen server.
- Eén aanroep naar een taalmodel per nieuw artikel; scoring in gewone Python.
- Interface: eerst een simpele webpagina of gegenereerde Markdown, daarna pas een mobiele app.
- **Geen vector database** nodig: met tientallen artikelen per dag volstaan zoekwoorden en onderwerp-labels. Overweeg semantisch zoeken pas als je over duizenden opgeslagen artikelen wilt zoeken of "vergelijkbare artikelen" wilt tonen.

### Wanneer dbt waarde toevoegt
Zodra de transformaties tussen ruw en "klaar voor gebruik" groeien (meerdere bronnen met eigen opschoning, historie van scores, feedback-analyses). dbt geeft dan herbruikbare modellen, tests (uniek, niet-leeg, toegestane waarden), documentatie en lineage. **dbt-duckdb** maakt dat mogelijk zonder zware infrastructuur.

### Wanneer Databricks gerechtvaardigd is
Voor een persoonlijke app meestal niet. Wel als:
- de radar onderdeel wordt van het dataplatform op het werk (bijv. voor een team),
- het volume of de rekenkracht buiten een laptop of klein script groeit,
- governance via Unity Catalog nodig is, of de verrijking moet draaien binnen de beveiligde omgeving van de organisatie.

Houd een persoonlijke variant en een werkvariant gescheiden: geen werkdata in een persoonlijke omgeving.
