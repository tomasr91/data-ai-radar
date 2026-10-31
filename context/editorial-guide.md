---
id: editorial-guide
type: context
schema_version: 2
updated: 2026-10-29
---

# Redactiegids

Dit bestand bepaalt **hoe** de AI nieuws verwerkt en presenteert. **Wat** relevant is, staat in `interests.yml`; **voor wie**, in `profile.md`, `tech-stack.md` en `projects.md`.

## 1. Schrijfstijl

- Eenvoudig, natuurlijk Nederlands, alsof je het uitlegt aan een slimme twaalfjarige.
- **Korte zinnen**: gemiddeld 12 tot 15 woorden, nooit meer dan 25. Eén gedachte per zin.
- **Korte alinea's** van 2 tot 4 zinnen, één gedachte per alinea. Begin elke alinea met een zin die aansluit op de vorige.
- **Actief en concreet**: wie doet wat. Liever "Databricks heeft een hulpmiddel gemaakt" dan "Er is een hulpmiddel beschikbaar gemaakt".
- **Hooguit één productnaam per zin**, en niet meer cijfers dan nodig. Rond cijfers af in het verhaal (14,9 miljoen); de precieze cijfers staan bij de bronfeiten.
- Leg een moeilijke term één keer uit, met een vergelijking uit het dagelijks leven, op de plek waar hij voor het eerst voorkomt.
- Begrippen die in `profile.md` §2 als bekend staan, leg je **niet** uit. Eenvoudige taal is iets anders dan basisuitleg.
- Gebruik Nederlandse woorden waar die gangbaar zijn. Zet de Engelse vakterm **bij het eerste gebruik** tussen haakjes, bijv. "herkomst van data (lineage)".
- Productnamen blijven zoals ze zijn (dbt, Unity Catalog, Azure DevOps).
- Geen marketingtaal ("revolutionair", "game changer"), geen overdreven claims, geen opsommingen in het verhaal.

**Zien:** waar het past krijgt een stuk een klein codevoorbeeld met resultaat ("Zo ziet het eruit"). Zie `TAAK_VERRIJKEN.md`.

**Centrale vraag:** wat is er nieuw, waarom is het interessant, hoe werkt het en welke mogelijkheden biedt het? Leg altijd uit *hoe* iets werkt. Concrete implementaties en codevoorbeelden gaan voor op alleen het concept.

## 2. Opbouw van een artikel

Een artikel is **één doorlopend verhaal**, geen formulier met losse vakjes.

1. **Kop** (`headline`): Nederlands, hooguit ongeveer 70 tekens. Zegt wat het betekent, niet wat het product heet. Bijv. *"Laat AI geen omzet uitrekenen zonder vaste definities"*. De originele titel toont de app er klein onder.
2. **Samenvatting** (`summary`): één of twee zinnen voor de kaart in de lijst.
3. **Verhaal** (`story`): 3 tot 5 alinea's met deze lijn:
   - *Wat gebeurde er?* Begin met de kern, het liefst concreet of verrassend.
   - *Hoe werkt het?* Uitleg met een vergelijking of voorbeeld, verweven in de tekst.
   - *Wat betekent het voor mij?* Koppel aan stack of project, alleen als dat iets toevoegt.
   - Eventueel een slotalinea met een belangrijke kanttekening.
4. **Probeer dit** (`experiment`): één klein experiment van hooguit een middag.
5. **Let op** (`limitations`): 1 tot 3 korte zinnen over beperkingen, risico's of onzekerheid.
6. **Bronfeiten** (`key_facts`): 3 tot 6 korte feiten uit de bron, met precieze cijfers, datums en status.
7. **Bron**: naam, publicatiedatum en link toont de app automatisch.

**Lengte past zich aan:** een kleine release krijgt 3 alinea's, een diepgaand praktijkverhaal 4 of 5. Liever kort en helder dan volledig.

### Opiniestukken (`article_type: "opinie"`)
Een onderbouwde mening van een **erkende vakpersoon** is welkom, ook zonder nieuwe functie of release.

- **Erkend** betekent: een bron in `sources.yml` met type `expert_blog`, of een auteur met een aantoonbare staat van dienst in het vak (bijv. oprichter of maintainer van een tool uit de stack, auteur van een vakboek, of iemand die bij een leverancier aan het product werkt). Anonieme stukken, gastblogs om een product te verkopen en algemene "AI verandert alles"-stukken vallen hier niet onder.
- De mening moet over het vakgebied gaan en **onderbouwd** zijn: met argumenten, ervaring of voorbeelden. Een losse stelling zonder uitleg is niet genoeg.
- **Kop**: geef de mening weer, met de naam erbij, bijv. *"Stancil: de semantische laag lost het AI-probleem niet op"*.
- **Verhaal** (3 tot 5 alinea's): *Wat vindt de auteur?* · *Waarom? Zijn belangrijkste argumenten* · *Wat betekent dat voor mij, en waar ben je het mee eens of niet?* · eventueel *het tegengeluid of de zwakke plek in het argument*.
- Schrijf de mening altijd toe aan de auteur ("Stancil vindt…", "volgens Reis…"). Presenteer een mening nooit als feit.
- **Bronfeiten** (`key_facts`) worden hier **de kernpunten van de auteur**: zijn stellingen en argumenten, toegeschreven en zo dicht mogelijk bij de tekst. Feiten die hij noemt, zoals cijfers, alleen als hij ze zelf geeft.
- **Let op** (`limitations`): noem belangen (werkt de auteur bij een leverancier?) en wat het stuk niet onderbouwt.
- `availability_status` is meestal `onbekend`; `practicality` en `novelty` gaan over de bruikbaarheid en frisheid van het idee.

### Verdiepingen
Naast het nieuws (tabblad *Actueel*) schrijft de radar ongeveer twee keer per week een **verdieping** (tabblad *Verdieping*): een langer stuk over een onderwerp uit `verdieping.yml`. Dezelfde schrijfstijl, maar met ruimte voor uitleg. Harde regel: **alleen wat nu actueel is**, geen verouderde technieken of tools. Details staan in `TAAK_VERRIJKEN.md`, hoofdstuk Verdiepingen.

### Dagelijks overzicht
De radar levert één kort dagelijks overzicht (leesritme uit `profile.md`):
- Bovenaan maximaal 5 artikelen, gesorteerd op relevantiescore; per artikel titel + samenvatting + link naar het volledige artikel.
- Is er een dag weinig relevant nieuws? Dan een korter overzicht, niet aanvullen met minder relevante items.
- Experimentideeën passen binnen een middag of minder (er is 1–3 uur per week beschikbaar).

## 3. Betrouwbaarheid

- **Verzin niets**: geen feiten, functies, bronnen of citaten die niet in de bron staan.
- **Herkomst blijft herleidbaar**: alles wat als feit in het verhaal staat, staat ook in `key_facts` en komt uit de bron. Interpretaties en suggesties formuleer je herkenbaar als zodanig ("dat betekent dat...", "je zou kunnen..."). Het experiment is altijd een suggestie.
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

- Alles uit `excluded_topics` in `interests.yml` (funding en overnames, AI voor beeld/video/muziek, crypto en blockchain, nieuwe connectoren, patches en dev-builds, maandoverzichten). Ook niet via de uitzonderingsregel.
- **Alleen must-knows.** Geen kleine updates: losse kleine functies, UI-aanpassingen, uitrol naar extra regio's of verzameloverzichten.
- **Klantverhalen** alleen als ze concreet maken welke tools er gebruikt worden en wat de toepassing is. Het verhaal begint dan bij de toepassing, niet bij het bedrijf.
- **Power BI en Fabric**: alleen grote functies die algemeen beschikbaar worden, wijzigingen in de koppeling met Databricks, of functies die stoppen.
- **dbt-releases**: grote en kleine releases en bèta's wel; patches en dev-builds niet.
- Artikelen zonder technische inhoud of praktische toepassing. Uitzondering: onderbouwde opinies van erkende vakmensen (zie §2, Opiniestukken).
- Personeelsnieuws, tenzij het directe gevolgen heeft voor een tool uit mijn stack.
- Herhalingen van eerder getoonde ontwikkelingen zonder nieuwe informatie.
