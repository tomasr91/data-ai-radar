# Examens (tabblad Leren): onderhoud

Het Claude-examen (Claude Certification Academy) staat sinds 31 oktober 2026 in deze map en draait in de Radar onder **Leren**. Het oude artifact op claude.ai blijft voorlopig bestaan als reserve, maar wordt niet meer bijgewerkt.

## Opbouw

| Pad | Wat |
|---|---|
| `index.html` | Pagina, opmaak en de lijst met scripts (volgorde telt). Onderaan het blok "Data & AI Radar" met de donkere kleuren. |
| `js/core.js` | Opslag (browser), herhaalsysteem (bakken 0–5, wachttijden 0/1/3/7/16/35 dagen), statistiek, meldingen. Geen DOM-code. |
| `js/app.js` | Schermen en knoppen. |
| `content/registry.js` | Per certificering: examengegevens, domeinen met wegingen en subonderwerpen, bronnen, `guideVersion`, `verifiedOn`. |
| `content/<cert>/modules-*.js` | Uitleg per subonderwerp. |
| `content/<cert>/questions-*.js` | Oefenvragen. Velden: `id`, `s` (subonderwerp), `t` (`"s"` één antwoord, `"m"` meerdere), `q`, `o` (opties), `a` (indexen juiste opties), `w` (uitleg per optie), `ex` (kernles). |

Een nieuw inhoudsbestand moet ook als `<script>` in `index.html` staan, vóór `js/core.js`.

## dbt Analytics Engineering (`dbtae`, sinds 24 november 2026)

- Examen van dbt Labs over **dbt Core 1.11** (65 vragen, 2 uur, slagen bij 65%). Bronnen: de examenpagina en de studiegids op getdbt.com (staan in `registry.js`).
- De studiegids geeft **geen wegingen**; de wegingen in `registry.js` zijn een schatting naar het aantal leerdoelen.
- T werkt met **dbt v2**. Uitleg noemt verschillen onder "In v2"; domein 8 (`d8`) is geen examenstof maar v2-kennis voor het werk. Bron: docs.getdbt.com, "Upgrading to v2".
- Vragen: `content/dbtae/questions-1.js` (domein 1) en `questions-2.js` (domein 2–8); uitleg: `content/dbtae/modules-1.js`.

## Databricks Data Engineer Associate (`dbxdea`, sinds 25 november 2026)

- Examen sinds 4 mei 2026; examengids bijgewerkt 6 augustus 2026. Wegingen komen uit de officiële gids; de gids noemt geen slaaggrens.
- Bron: de examengids-PDF op databricks.com (staat in `registry.js`) en docs.databricks.com.
- Vragen: `content/dbxdea/questions-1.js`; uitleg: `content/dbxdea/modules-1.js`.

## Get Started with Databricks for Data Engineering (`dbxgs`, sinds 26 november 2026)

- Geen examen: een korte beginnerscursus van Databricks Academy (onboarding, ongeveer 2 uur). De onderwerpen volgen de cursuspagina (staat in `registry.js`); de weging is gelijk verdeeld.
- Vragen: `content/dbxgs/questions-1.js`; uitleg: `content/dbxgs/modules-1.js`.

## Opslag en meldingen

- **Voortgang**: in de browser (`localStorage`, sleutel `cca-academy-v2`). Export/import via "Voortgang en back-up".
- **Meldingen**: de knop "Klopt deze vraag niet?" opent een GitHub-issue met titel `Examenmelding: <cert> <vraag-id>`. Alleen issues van de eigenaar van de repository tellen.

## Maandcontrole (geplande taak)

1. Lees de open issues met titel `Examenmelding:` van de eigenaar. Beoordeel elke melding; pas de vraag aan als de melding klopt.
2. Controleer de officiële bronnen (examengidsen op anthropic-partners.skilljar.com) tegen `content/registry.js`: gidsversie, aantal vragen, tijd, slaaggrens, domeinen en wegingen.
3. Controleer productfeiten in vragen en uitleg tegen support.claude.com, docs.claude.com / platform.claude.com, code.claude.com en de Anthropic-nieuwspagina. Zoek ook naar nieuwe functies die in de examenstof horen.
3c. **Databricks**: zoek de actuele examengids van de Data Engineer Associate op databricks.com en vergelijk datum, aantal vragen, tijd, onderwerpen en wegingen met `dbxdea` in `registry.js`. Controleer feiten tegen docs.databricks.com.
3b. **dbt**: vergelijk de examenpagina en studiegids van dbt Labs (versie, aantal vragen, tijd, slaaggrens, onderwerpen) met `registry.js` (`dbtae`). Komt er een nieuwe examenversie, pas de onderwerpen aan. Controleer feiten tegen docs.getdbt.com, ook wat er in dbt v2 verandert (domein 8 en de regels "In v2").
4. Pas aan wat nodig is. Zet `verifiedOn` in `registry.js` op de datum van vandaag.
5. Controleer: `node scripts/validate_leren.js` moet 0 fouten geven (unieke id's, antwoorden binnen bereik, één antwoord bij `t:"s"`, minstens twee bij `t:"m"`, `w` even lang als `o`, elk subonderwerp heeft vragen, juiste antwoord niet systematisch het langste).
6. Commit alleen bestanden in `app/leren/`, met `Closes #<n>` per verwerkte melding op een eigen regel. Push naar `main`; GitHub Actions zet het binnen een minuut online.

Twijfel je of een productfeit veranderd is en kun je het niet in een officiële bron bevestigen: pas de vraag niet aan, maar noem het in de samenvatting.
