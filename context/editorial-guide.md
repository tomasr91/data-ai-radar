---
id: editorial-guide
type: context
schema_version: 1
updated: 2026-10-28
---

# Redactiegids

Dit bestand bepaalt **hoe** de AI nieuws verwerkt en presenteert. **Wat** relevant is, staat in `interests.yml`; **voor wie**, in `profile.md`, `tech-stack.md` en `projects.md`.

## 1. Schrijfstijl

- Eenvoudig, natuurlijk Nederlands — alsof je het uitlegt aan een slimme twaalfjarige.
- Korte alinea's (2–4 zinnen) en concrete voorbeelden.
- Leg een moeilijke term direct uit, één keer, met een vergelijking uit het dagelijks leven.
- Begrippen die in `profile.md` §2 als bekend staan, leg je **niet** uit. Eenvoudige taal is iets anders dan basisuitleg.
- Geen marketingtaal ("revolutionair", "game changer"), geen overdreven claims.
- Gebruik Nederlandse woorden waar die gangbaar zijn. Zet de Engelse vakterm **bij het eerste gebruik** tussen haakjes, bijv. "herkomst van data (lineage)"; daarna mag je één van beide gebruiken.
- Productnamen blijven zoals ze zijn (dbt, Unity Catalog, Azure DevOps).

## 2. Structuur van een artikel

1. **Titel** — kort, met de kern erin.
2. **Samenvatting** — maximaal drie zinnen.
3. **Wat is er nieuw?** — feitelijk, met status (zie §3).
4. **Uitleg** — in eenvoudige taal.
5. **Voorbeeld** — herkenbaar, liefst uit een dataplatform zoals het mijne.
6. **Waarom relevant voor mijn stack?** — koppel aan `tech-stack.md` en waar mogelijk een project uit `projects.md`.
7. **Wat kan ik ermee?** — praktische toepassing.
8. **Experiment of PoC** — één concreet, klein idee met een duidelijke eerste stap.
9. **Beperkingen en aandachtspunten** — risico's, kosten, volwassenheid, zorgcontext.
10. **Bron** — naam, publicatiedatum, link. Plus beschikbaarheidsdatum als die afwijkt.

**Lengte past zich aan:**
- *Kort* (kleine release of fix): stap 1–3, 6 en 10.
- *Middel* (standaard): alle stappen, compact.
- *Lang* (nieuw concept of grote wijziging): alle stappen, met een extra kopje **Verdieping** voor technische details.

### Dagelijks overzicht
De radar levert één kort dagelijks overzicht (leesritme uit `profile.md`):
- Bovenaan maximaal 5 artikelen, gesorteerd op relevantiescore; per artikel titel + samenvatting + link naar het volledige artikel.
- Is er een dag weinig relevant nieuws? Dan een korter overzicht, niet aanvullen met minder relevante items.
- Experimentideeën passen binnen een middag of minder (er is 1–3 uur per week beschikbaar).

## 3. Betrouwbaarheid

- **Verzin niets**: geen feiten, functies, bronnen of citaten die niet in de bron staan.
- **Markeer de herkomst** van uitspraken:
  - `Bron:` — staat zo in het originele artikel.
  - `Interpretatie:` — jouw uitleg of conclusie uit de bron.
  - `Suggestie:` — jouw eigen idee voor toepassing (altijd bij stap 7 en 8).
- **Geef de status** van een functie:
  - `beschikbaar` (algemeen beschikbaar)
  - `preview` (publiek of beperkt)
  - `aangekondigd` (nog niet te gebruiken)
  - `experimenteel` (onderzoek, prototype of open-source project in vroege fase)
  - `onbekend` (bron zegt het niet)
- **Datums**: gebruik de originele publicatiedatum, en waar mogelijk de datum waarop iets echt beschikbaar werd.
- **Nieuwheidscheck**: gaat het artikel over iets wat al eerder is verschenen? Meld dat dan ("dit is al sinds … beschikbaar") of laat het weg.
- **Onzekerheid**: zeg het als iets onzeker is of bronnen elkaar tegenspreken.
- **Bronnen met trust_level `medium` of `low`** (zie `sources.yml`): controleer productclaims bij een primaire bron of vermeld dat dit niet is gecontroleerd.
- **Altijd** een link naar de oorspronkelijke bron.

## 4. Personalisatie

- Gebruik `profile.md`, `tech-stack.md`, `projects.md` en `interests.yml`.
- Geef voorrang aan toepassingen die passen bij mijn stack en lopende projecten.
- Gebruik informatie met label `[aanname]` voorzichtig: formuleer als "als je … gebruikt".
- Wissel voorbeelden en invalshoeken af; herhaal niet steeds hetzelfde voorbeeld of project.
- Bied verdieping aan, maar dring het niet op.

## 5. Zorgcontext

- Gebruik **nooit** patiëntgegevens in prompts, voorbeelden of experimenten. Gebruik verzonnen of synthetische voorbeelden die duidelijk als zodanig herkenbaar zijn.
- Benoem bij elk idee dat zorg- of onderzoeksdata raakt: privacy, informatiebeveiliging, toegangsrechten, datakwaliteit en verantwoord AI-gebruik.
- Maak onderscheid tussen:
  - **Experiment** — op openbare, synthetische of niet-gevoelige data, in een afgeschermde omgeving.
  - **Productiegeschikt** — pas na toetsing aan interne regels, beveiliging en eigenaarschap.
- Externe AI-diensten (zoals Claude of ChatGPT) mogen alleen **zonder werkdata** worden gebruikt; AI binnen Databricks mag wel met werkdata, binnen de geldende toegangsrechten. Stel geen toepassingen voor die hiertegen ingaan.

## 6. Wat níet in de feed hoort

- Alles uit `excluded_topics` in `interests.yml` (funding en overnames, AI voor beeld/video/muziek, crypto en blockchain). Ook niet via de uitzonderingsregel.
- Artikelen zonder technische inhoud of praktische toepassing.
- Personeelsnieuws, tenzij het directe gevolgen heeft voor een tool uit mijn stack.
- Herhalingen van eerder getoonde ontwikkelingen zonder nieuwe informatie.
