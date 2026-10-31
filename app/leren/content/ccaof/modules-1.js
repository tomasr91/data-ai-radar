/* CCAO-F leermodules, domein 1–3.
   Structuur per module: intro, sections (één per officieel subonderwerp), terms, examples, pitfalls, scenarios, advice.
   'body' is HTML. Officiële examenstof = de leerdoelen (subs) in registry.js; de rest is aanvullende uitleg. */
Academy.addModules("ccaof", {

/* ===================================================== D1 */
d1: {
  intro: "Prompting is de basisvaardigheid waarop alle andere domeinen leunen. Op Associate-niveau gaat het niet om trucjes, maar om het vertalen van een zakelijke vraag naar een opdracht die Claude zonder giswerk kan uitvoeren: doel, context, randvoorwaarden en gewenst resultaat. Het examen toetst daarnaast of je complexe opdrachten kunt opknippen, gericht kunt bijsturen en je aanpak kunt aanpassen aan het soort taak.",
  sections: [
    { sub: "d1.1", title: "De anatomie van een effectieve prompt", body: `
<p>Een effectieve prompt bevat alles wat een slimme nieuwe collega nodig heeft om de taak in één keer goed te doen. Claude weet niets van je organisatie, je publiek of je bedoeling tenzij je dat vertelt. De meeste slechte output is terug te voeren op ontbrekende context, niet op een slecht model.</p>
<p>Werk met deze bouwstenen:</p>
<ul>
<li><b>Taak en doel</b>: wat moet er gebeuren en waarvoor wordt het resultaat gebruikt? "Vat samen" is een taak; "vat samen zodat de directie in twee minuten kan beslissen of we doorgaan" is een taak met doel.</li>
<li><b>Context</b>: achtergrond, doelgroep, eerdere besluiten, het bronmateriaal zelf. Plak of upload bronnen in plaats van ze te beschrijven.</li>
<li><b>Randvoorwaarden (constraints)</b>: lengte, toon, taal, wat er níet in mag, welke bronnen leidend zijn.</li>
<li><b>Outputformaat</b>: tabel, opsomming, e-mail, JSON, een document. Een voorbeeld van het gewenste formaat werkt beter dan een beschrijving.</li>
<li><b>Voorbeelden (few-shot / multishot)</b>: één tot drie voorbeelden van goede output sturen stijl en structuur sterk. Varieer ze, anders kopieert Claude één voorbeeld te letterlijk.</li>
<li><b>Rol</b> (optioneel): "Je bent een ervaren HR-adviseur" helpt de toon en het perspectief te bepalen, maar vervangt geen context.</li>
</ul>
<p>Structuur helpt Claude om onderdelen uit elkaar te houden. Scheid instructies van bronmateriaal, bijvoorbeeld met XML-achtige tags of duidelijke kopjes:</p>
<pre class="prompt">Je helpt het marketingteam met een nieuwsbriefintro.

&lt;doel&gt;Lezers (bestaande B2B-klanten) aanzetten tot aanmelden voor het webinar van 12 november.&lt;/doel&gt;
&lt;bron&gt;[productnotities geplakt]&lt;/bron&gt;
&lt;eisen&gt;
- Maximaal 90 woorden, je-vorm, geen superlatieven
- Noem precies één voordeel uit de bron
- Sluit af met de aanmeldlink: {LINK}
&lt;/eisen&gt;
Geef drie varianten met elk een andere openingszin.</pre>
<p>Wees expliciet over wat je wilt in plaats van wat je niet wilt. "Schrijf in korte alinea's van maximaal drie zinnen" werkt beter dan "niet te lange tekst". En vertel waarom een eis bestaat; met de reden erbij kan Claude de bedoeling ook toepassen in situaties die je niet voorzag.</p>` },
    { sub: "d1.2", title: "Task decomposition: complexe opdrachten opknippen", body: `
<p>Een grote opdracht in één prompt ("analyseer deze 40 klantinterviews, bedenk een strategie en schrijf een presentatie") levert vaak oppervlakkige output op die moeilijk te controleren is. Door de taak op te knippen krijg je per stap betere kwaliteit én controlepunten.</p>
<p>Gangbare technieken:</p>
<ul>
<li><b>Sequentiële stappen (prompt chaining)</b>: de output van stap 1 is de input voor stap 2. Bijvoorbeeld: (1) thema's uit interviews halen, (2) thema's prioriteren op frequentie en impact, (3) aanbevelingen formuleren, (4) presentatie opzetten.</li>
<li><b>Opsplitsen naar onderdeel</b>: bij een lang rapport elk hoofdstuk apart laten beoordelen en daarna samenvoegen.</li>
<li><b>Eerst plannen, dan uitvoeren</b>: vraag Claude eerst een aanpak of outline voor te stellen, keur die goed of pas hem aan, en laat dan pas uitwerken.</li>
<li><b>Ruimte om na te denken</b>: bij analyse- of afwegingsvragen helpt het om Claude eerst te laten redeneren of de opties naast elkaar te laten zetten voordat er een conclusie volgt.</li>
</ul>
<p>Het grootste voordeel is <b>tussentijdse validatie</b>: je controleert de thema's voordat er een strategie op wordt gebouwd. Een fout in stap 1 die je pas in de eindpresentatie ontdekt, kost veel meer werk.</p>
<p>Knip niet onnodig op. Een eenvoudige taak (een e-mail herschrijven) in vijf stappen verdelen kost alleen tijd. De vuistregel: knip op wanneer de taak uit duidelijk verschillende denkstappen bestaat, wanneer tussenresultaten gecontroleerd moeten worden, of wanneer de output te groot wordt om in één keer goed te beoordelen.</p>` },
    { sub: "d1.3", title: "Itereren: van eerste versie naar bruikbaar resultaat", body: `
<p>De eerste output is een concept. Itereren is een vaardigheid op zich: je stuurt gericht bij in plaats van opnieuw te beginnen met "probeer het nog eens".</p>
<ul>
<li><b>Benoem concreet wat er mis is</b>: "De toon is te formeel voor ons interne Slack-kanaal; schrijf zoals een collega praat, maximaal 4 zinnen" in plaats van "maak het beter".</li>
<li><b>Behoud wat goed is</b>: "Houd de structuur en de drie punten aan, pas alleen de inleiding aan."</li>
<li><b>Voeg ontbrekende context toe</b>: vaak blijkt pas uit de output welke informatie je vergat (doelgroep, budget, eerdere besluiten).</li>
<li><b>Verbeter de prompt zelf</b> wanneer je de taak vaker gaat uitvoeren. Een feedbackronde in de chat helpt eenmalig; een aangepaste prompt of Project-instructie helpt elke keer.</li>
<li><b>Vergelijk varianten</b>: vraag twee of drie alternatieven en kies, in plaats van één versie eindeloos bij te schaven.</li>
</ul>
<p>Als een gesprek na veel correcties rommelig wordt en Claude oude, verworpen instructies blijft meenemen, is het vaak effectiever om een nieuw gesprek te starten met een verbeterde prompt waarin alle lessen verwerkt zijn. Dit raakt aan domein 3 (contextbeheer) en domein 7 (probleemoplossing).</p>` },
    { sub: "d1.4", title: "Promptstrategie afstemmen op het type taak", body: `
<p>Het examen noemt vier taaktypen. Elk vraagt om een andere aanpak:</p>
<div class="tbl"><table>
<thead><tr><th>Taaktype</th><th>Wat werkt</th><th>Let op</th></tr></thead>
<tbody>
<tr><td><b>Analysis</b></td><td>Lever de data of het document aan, geef het analysekader (criteria, vergelijkingspunten), vraag om onderbouwing per conclusie en citaten uit de bron.</td><td>Laat Claude onderscheid maken tussen wat in de data staat en wat het afleidt.</td></tr>
<tr><td><b>Research</b></td><td>Formuleer een duidelijke onderzoeksvraag en scope, vraag om bronvermelding, gebruik zoek- of researchfuncties voor actuele informatie.</td><td>Zonder zoekfunctie werkt Claude met trainingskennis met een afkapdatum. Bronnen altijd controleren.</td></tr>
<tr><td><b>Drafting</b></td><td>Doelgroep, toon, lengte, kernboodschap, een voorbeeld van de gewenste stijl, verplichte elementen.</td><td>Feitelijke claims in een concept blijven jouw verantwoordelijkheid.</td></tr>
<tr><td><b>Brainstorming</b></td><td>Vraag om veel en uiteenlopende ideeën, eventueel vanuit verschillende perspectieven, en filter daarna. Beperk vroege kritiek.</td><td>Brainstorm-output is niet gevalideerd: ideeën zijn startpunten, geen aanbevelingen.</td></tr>
</tbody></table></div>
<p>Kernprincipe: bij <b>convergente</b> taken (analyse, een concept met harde eisen) wil je precisie, bronnen en strakke randvoorwaarden. Bij <b>divergente</b> taken (brainstormen) wil je juist ruimte en variatie. Een prompt die voor de ene taak perfect is, kan de andere smoren.</p>` }
  ],
  terms: [
    ["Prompt", "De opdracht of invoer die je aan Claude geeft."],
    ["Context", "Achtergrondinformatie die Claude nodig heeft om de taak goed te doen."],
    ["Constraints", "Randvoorwaarden: lengte, toon, wat wel/niet mag."],
    ["Few-shot / multishot prompting", "Voorbeelden van gewenste output meegeven."],
    ["Role prompting", "Claude een rol of perspectief geven."],
    ["Task decomposition", "Een complexe taak opdelen in kleinere stappen."],
    ["Prompt chaining", "De output van de ene prompt gebruiken als input voor de volgende."],
    ["Iteration / refinement", "Output stapsgewijs verbeteren met gerichte feedback."],
    ["Output format", "De vorm van het resultaat (tabel, lijst, JSON, document)."],
    ["XML tags", "Labels zoals &lt;bron&gt; om onderdelen van een prompt te scheiden."]
  ],
  examples: [
    { title: "Samenvatting voor de directie",
      bad: "Vat dit rapport samen.",
      good: "Vat het bijgevoegde kwartaalrapport samen voor het MT, dat donderdag beslist over het budget voor Q1. Maximaal 200 woorden. Begin met de conclusie, noem daarna de drie belangrijkste afwijkingen ten opzichte van de begroting met bedragen, en sluit af met openstaande risico's. Neem alleen cijfers over die letterlijk in het rapport staan.",
      why: "De goede prompt geeft doelgroep, beslismoment, lengte, structuur en een validatie-eis (alleen cijfers uit de bron). De slechte laat alles open, waardoor Claude moet raden wat belangrijk is." },
    { title: "Bijsturen na de eerste versie",
      bad: "Nee, dit is niet goed. Probeer opnieuw.",
      good: "De structuur klopt. Twee aanpassingen: de toon is te verkoopachtig voor bestaande klanten, maak hem informatief. En het tweede punt over prijzen klopt niet, die staan nog niet vast; laat dat punt weg.",
      why: "Gerichte feedback benoemt wat blijft, wat moet veranderen en waarom. Zonder richting produceert Claude een willekeurige andere versie." }
  ],
  pitfalls: [
    "Denken dat een langere prompt altijd beter is. Relevante context helpt; ruis en tegenstrijdige eisen schaden.",
    "Bronmateriaal beschrijven in plaats van het aanleveren. 'Het beleid zegt ongeveer...' leidt tot gokwerk.",
    "Alleen zeggen wat niet mag. Positieve, concrete instructies werken beter.",
    "Een complexe meerstapstaak in één prompt proppen en daarna niet meer kunnen zien waar het misging.",
    "Na een slechte output het hele gesprek opnieuw beginnen zonder de prompt te verbeteren, waardoor dezelfde fout terugkomt.",
    "Een rolprompt ('je bent een jurist') zien als garantie voor juiste inhoud. Een rol stuurt stijl en perspectief, niet de feitelijke juistheid."
  ],
  scenarios: [
    { title: "De klantonderzoek-opdracht",
      situation: "Je hebt 25 transcripties van klantinterviews en moet volgende week een advies voor productverbeteringen presenteren. Hoe pak je dit met Claude aan?",
      options: [
        { t: "Upload alles en vraag in één prompt om een complete presentatie met aanbevelingen.", ok: false, fb: "Je krijgt snel iets, maar je kunt niet controleren of de thema's en aanbevelingen echt uit de interviews komen. Een fout in de analyse zit verborgen in de eindpresentatie." },
        { t: "Eerst thema's laten extraheren met citaten per thema, die controleren, daarna prioriteren, dan aanbevelingen en tot slot de presentatie.", ok: true, fb: "Dit is task decomposition met tussentijdse validatie. Citaten maken de thema's controleerbaar en elke stap bouwt voort op een gecontroleerd resultaat." },
        { t: "Claude vragen om eerst zelf aanbevelingen te bedenken en daarna de interviews te gebruiken als onderbouwing.", ok: false, fb: "Dit draait de redenering om en nodigt uit tot bevestigingsbias: Claude zoekt dan bewijs bij vooraf bedachte conclusies." }
      ] },
    { title: "Brainstorm versus beleidstekst",
      situation: "Je gebruikt dezelfde strakke prompt (max 100 woorden, formele toon, alleen feiten uit de bron) voor zowel het herschrijven van beleidstekst als het bedenken van namen voor een nieuw intern programma. De namen vallen tegen. Wat is de beste aanpassing?",
      options: [
        { t: "Voor de brainstorm de randvoorwaarden loslaten, om 20 uiteenlopende opties vragen vanuit verschillende invalshoeken en daarna zelf selecteren.", ok: true, fb: "Brainstormen is een divergente taak. Strakke constraints die bij beleidstekst passen, beperken hier juist de creativiteit." },
        { t: "Overstappen naar een ander model, want dit model is niet creatief genoeg.", ok: false, fb: "Het probleem zit in de promptstrategie, niet in het model. Eerst de aanpak aanpassen aan het taaktype." },
        { t: "De prompt nog strakker maken zodat Claude precies weet wat je wilt.", ok: false, fb: "Meer beperkingen maken de output bij een creatieve taak nog eenvormiger." }
      ] }
  ],
  advice: [
    "Oefen met echte werktaken: schrijf voor drie taken eerst een snelle prompt en daarna een volledige versie met doel, context, constraints en formaat. Vergelijk de output.",
    "Leer de vier taaktypen (analysis, research, drafting, brainstorming) herkennen in scenariovragen: het juiste antwoord past bijna altijd de aanpak aan het taaktype aan.",
    "Bij examenvragen over iteratie is het beste antwoord meestal specifieke, gerichte feedback, niet 'opnieuw genereren' of 'ander model kiezen'."
  ]
},

/* ===================================================== D2 */
d2: {
  intro: "Dit is het zwaarst gewogen domein (21%, ongeveer 12–13 van de 60 vragen). Het examen gaat ervan uit dat Claude's output altijd een concept is waarvoor jij verantwoordelijk blijft. Je moet kunnen beoordelen of iets klopt en compleet is, typische fouten van taalmodellen herkennen, weten hoe je controleert, inschatten wanneer een mens moet meekijken, en output geschikt maken voor de lezer en het juiste formaat kiezen.",
  sections: [
    { sub: "d2.1", title: "Juistheid en volledigheid beoordelen", body: `
<p>Beoordeel output altijd tegen de opdracht en de bron, niet tegen je gevoel. Een tekst die vloeiend en zelfverzekerd leest, is daarmee nog niet juist. Taalmodellen schrijven overtuigend, ook als de inhoud niet klopt.</p>
<p>Twee aparte vragen:</p>
<ul>
<li><b>Accuracy (juistheid)</b>: kloppen de feiten, cijfers, namen, data, citaten en conclusies? Volgen de conclusies logisch uit de gegevens?</li>
<li><b>Completeness (volledigheid)</b>: zijn alle onderdelen van de opdracht beantwoord? Zijn belangrijke punten uit de bron weggelaten? Een samenvatting kan volledig juist zijn en toch het belangrijkste risico missen.</li>
</ul>
<p>Een praktische werkwijze is een <b>checklist afgeleid van de opdracht</b>. Vroeg je om drie risico's met bedragen en een aanbeveling? Controleer dan: drie risico's aanwezig, bedragen aanwezig en terug te vinden in de bron, aanbeveling aanwezig en logisch.</p>
<p>Let extra op bij lange documenten: informatie uit het midden van een lang document wordt soms minder goed meegenomen dan begin en eind. Vraag bij twijfel gericht: "Welke onderdelen van hoofdstuk 4 heb je niet in de samenvatting opgenomen?" en controleer zelf steekproefsgewijs.</p>` },
    { sub: "d2.2", title: "Hallucinaties, inconsistenties en bias herkennen", body: `
<p><b>Hallucinatie</b>: Claude produceert informatie die plausibel klinkt maar niet waar is of niet in de bron staat. Typische signalen:</p>
<ul>
<li>Zeer specifieke details die je niet hebt aangeleverd: artikelnummers, percentages, publicatiejaren, namen van onderzoeken, URL's.</li>
<li>Citaten tussen aanhalingstekens die je niet letterlijk terugvindt in de bron.</li>
<li>Bronverwijzingen naar rapporten of artikelen die niet bestaan of iets anders zeggen.</li>
<li>Antwoorden over recente gebeurtenissen of interne zaken waarover Claude geen informatie kan hebben.</li>
</ul>
<p><b>Inconsistentie</b>: tegenstrijdigheden binnen het antwoord of met de bron. Bijvoorbeeld een totaal dat niet optelt, een conclusie die het tegenovergestelde zegt van een eerdere alinea, of een naam die halverwege verandert.</p>
<p><b>Bias</b>: eenzijdigheid in perspectief, aannames of stereotypen. Voorbeelden: een vacaturetekst die onbewust één doelgroep aanspreekt, een marktanalyse die alleen voordelen noemt, of een samenvatting die de mening van één stakeholder zwaarder laat wegen. Bias kan ook uit jouw prompt komen: een sturende vraag ("leg uit waarom optie A beter is") levert een eenzijdig antwoord.</p>
<p>Belangrijk voor het examen: <b>het zelfvertrouwen van Claude is geen betrouwbaarheidssignaal</b>. Claude vragen hoe zeker het is, of het antwoord te laten "dubbelchecken" in hetzelfde gesprek, vervangt geen controle tegen een onafhankelijke bron.</p>` },
    { sub: "d2.3", title: "Factchecken en valideren", body: `
<p>Validatietechnieken, van licht naar zwaar:</p>
<ul>
<li><b>Grounding in de bron</b>: lever het brondocument aan en vraag Claude om antwoorden te baseren op dat document, met letterlijke citaten per bewering. Dan kun je elke claim terugvinden.</li>
<li><b>Toestemming om "weet ik niet" te zeggen</b>: instrueer expliciet dat Claude mag aangeven dat iets niet in de bron staat. Dit vermindert verzonnen antwoorden.</li>
<li><b>Bronvermelding laten geven en controleren</b>: bij gebruik van web search of Research krijg je bronnen. Open ze en controleer of ze echt zeggen wat Claude beweert.</li>
<li><b>Controleren tegen de primaire bron</b>: wetteksten, officiële cijfers, contracten en beleidsdocumenten zijn de maatstaf, niet een samenvatting ervan.</li>
<li><b>Berekeningen narekenen</b>: laat cijfers uitrekenen met code-uitvoering of reken zelf na in een spreadsheet; tel totalen op.</li>
<li><b>Steekproeven</b>: bij grote hoeveelheden output (bijvoorbeeld 200 geclassificeerde tickets) een representatieve steekproef handmatig controleren.</li>
<li><b>Onafhankelijke review</b>: een vakexpert of collega laten meelezen bij inhoud met gevolgen.</li>
</ul>
<p>Valideren is evenredig aan het risico. Een interne brainstorm hoeft niet gefactcheckt; een tekst voor compliance, klanten, publicatie of besluitvorming wel.</p>` },
    { sub: "d2.4", title: "Wanneer menselijke review of extra verificatie nodig is", body: `
<p>De kernvraag: <b>wat gebeurt er als dit fout is?</b> Hoe groter de impact, hoe zwaarder de review. Menselijke review (human-in-the-loop) is in elk geval nodig bij:</p>
<ul>
<li><b>Juridische, financiële, medische of compliance-inhoud</b>: contractclausules, regelgeving, financiële rapportage, gezondheidsadvies.</li>
<li><b>Externe communicatie</b>: persberichten, klantcommunicatie namens de organisatie, publicaties.</li>
<li><b>Besluiten over mensen</b>: werving en selectie, beoordelingen, ontslag, toekenning van voorzieningen.</li>
<li><b>Onomkeerbare acties</b>: iets versturen, publiceren of verwijderen.</li>
<li><b>Gebieden buiten je eigen expertise</b>: als je zelf niet kunt beoordelen of het klopt, moet iemand anders dat doen.</li>
</ul>
<p>Review is ook het moment om te <b>escaleren</b>. De examengids beschrijft dat een Associate grenzen herkent en complex of technisch werk doorschuift naar Claude Architects en Developers. Een Associate bouwt bijvoorbeeld geen API-integratie die automatisch beslissingen neemt; dat ontwerp hoort bij een Developer of Architect.</p>
<p>Lage-risicotaken (een eerste opzet voor een interne notitie, ideeën voor een workshop) mogen met lichte controle. Het examen beloont evenredigheid: niet alles verbieden, niet alles blind vertrouwen.</p>` },
    { sub: "d2.5", title: "Output aanpassen, verfijnen en vergelijken voor de doelgroep", body: `
<p>Dezelfde inhoud moet er voor een CFO anders uitzien dan voor een klantenservicemedewerker. Pas aan op:</p>
<ul>
<li><b>Niveau en jargon</b>: vakjargon uitleggen of vermijden voor leken, juist precies zijn voor experts.</li>
<li><b>Lengte en volgorde</b>: managers willen de conclusie eerst (BLUF: bottom line up front); uitvoerders willen stappen.</li>
<li><b>Toon</b>: formeel, informeel, empathisch, neutraal. Passend bij kanaal (e-mail, Slack, rapport).</li>
<li><b>Taal en culturele context</b>: vertalingen nalopen op betekenis en toon, niet alleen grammatica.</li>
</ul>
<p>Na het aanpassen opnieuw controleren: bij herschrijven of inkorten kunnen nuances verdwijnen of kan de betekenis verschuiven ("mogelijk" wordt "zeker").</p>
<p><b>Vergelijken</b>: laat twee of meer varianten maken en beoordeel ze op vooraf bepaalde criteria (helderheid, juistheid, toon, lengte). Zo kies je op argumenten in plaats van op voorkeur, en kun je de beste elementen combineren.</p>` },
    { sub: "d2.6", title: "Informatie ordenen en het juiste outputformaat kiezen", body: `
<p>Het examen noemt expliciet drie vormen: <b>artifacts</b>, <b>inline</b> antwoorden en <b>structured data</b>.</p>
<div class="tbl"><table>
<thead><tr><th>Formaat</th><th>Wanneer</th><th>Voorbeeld</th></tr></thead>
<tbody>
<tr><td><b>Inline</b> (in het gesprek)</td><td>Korte antwoorden, uitleg, iets wat je één keer leest.</td><td>Een snelle vraag beantwoorden, een korte e-mail.</td></tr>
<tr><td><b>Artifact</b></td><td>Zelfstandige inhoud die je bewaart, bewerkt, deelt of hergebruikt.</td><td>Een document, presentatie, interactieve tool, diagram of webpagina.</td></tr>
<tr><td><b>Structured data</b></td><td>Output die verder verwerkt wordt of vergeleken moet worden.</td><td>Tabellen, CSV, JSON voor import, een vergelijkingsmatrix.</td></tr>
</tbody></table></div>
<p>Kies het formaat vanuit het gebruik: wat gaat de lezer of het volgende systeem ermee doen? Een vergelijking van vijf leveranciers op acht criteria is als tabel veel beter te beoordelen dan als lopende tekst. Een draaiboek dat het team gaat bijwerken hoort in een artifact of document, niet verstopt in een chatbericht.</p>
<p><b>Curatie</b> betekent ook weglaten: alleen de informatie die de lezer nodig heeft, gegroepeerd in een logische volgorde, met duplicaten verwijderd.</p>` }
  ],
  terms: [
    ["Hallucination", "Plausibele maar onjuiste of verzonnen informatie."],
    ["Accuracy / completeness", "Juistheid / volledigheid van de output."],
    ["Fact-checking", "Beweringen controleren tegen betrouwbare bronnen."],
    ["Grounding", "Antwoorden baseren op aangeleverd bronmateriaal."],
    ["Citations / quotes", "Letterlijke verwijzingen naar de bron als bewijs."],
    ["Human-in-the-loop / human review", "Een mens controleert of keurt goed vóór gebruik."],
    ["Bias", "Eenzijdigheid of vooringenomenheid in output of prompt."],
    ["Inconsistency", "Tegenstrijdigheid binnen de output of met de bron."],
    ["Escalation", "Werk doorzetten naar een expert, Developer of Architect."],
    ["Artifact", "Zelfstandige output (document, code, app) naast het gesprek."],
    ["Structured data", "Gestructureerde output zoals tabellen, CSV of JSON."],
    ["Intended audience", "De beoogde lezer voor wie je de output aanpast."]
  ],
  examples: [
    { title: "Samenvatting van een regeling voor compliance",
      bad: "Claude geeft een stellige samenvatting met 'artikel 14 lid 3'. Je stuurt hem door omdat het zeker klinkt.",
      good: "Je vraagt Claude bij elke bewering het letterlijke citaat uit de aangeleverde regeling te geven, zoekt artikel 14 lid 3 op in de officiële tekst en laat de compliance officer meelezen voordat het wordt verspreid.",
      why: "Specifieke verwijzingen zijn precies het soort detail dat verzonnen kan zijn. Controle tegen de primaire bron plus review door een expert past bij een compliance-publiek." },
    { title: "Classificatie van 300 klantklachten",
      bad: "Je laat Claude alle klachten categoriseren en neemt de aantallen per categorie direct over in het managementrapport.",
      good: "Je controleert eerst een steekproef van 30 klachten handmatig, past de categoriedefinities aan waar Claude twijfelde, laat opnieuw classificeren en rekent de aantallen na in een spreadsheet.",
      why: "Bij grote volumes is een steekproef de praktische validatietechniek. Narekenen voorkomt telfouten in het rapport." },
    { title: "Formaatkeuze",
      bad: "Een vergelijking van vier CRM-pakketten op prijs, integraties, AVG en gebruiksgemak als vier lange alinea's in de chat.",
      good: "Een tabel met de pakketten als kolommen en criteria als rijen, met bron per cel, als artifact zodat het team hem kan aanvullen.",
      why: "Vergelijkingen zijn gestructureerde informatie. Een tabel maakt verschillen zichtbaar; een artifact maakt het deelbaar en bewerkbaar." }
  ],
  pitfalls: [
    "Claude laten beoordelen hoe zeker het is en dat als validatie zien. Self-reported confidence is geen bewijs.",
    "Alleen op stijl en taal reviewen ('klinkt professioneel') en de feiten overslaan.",
    "Een bron die Claude noemt niet openen. Een bronvermelding kan bestaan en toch iets anders zeggen.",
    "Bij herschrijven voor een andere doelgroep niet opnieuw controleren of de betekenis gelijk is gebleven.",
    "Alles even zwaar controleren, of juist niets. Validatie hoort evenredig te zijn aan het risico.",
    "Denken dat aangeleverde bronnen hallucinaties volledig uitsluiten. Ze verkleinen het risico; controle blijft nodig.",
    "Vergeten dat bias ook in je eigen vraagstelling kan zitten."
  ],
  scenarios: [
    { title: "Het marktonderzoek met cijfers",
      situation: "Claude levert een marktanalyse voor een investeringsvoorstel met daarin '37% jaarlijkse groei volgens het rapport van Branchevereniging X uit 2025'. Jij hebt dat rapport niet aangeleverd. Wat doe je?",
      options: [
        { t: "Het rapport zelf opzoeken en controleren of het bestaat en dit cijfer bevat, voordat het in het voorstel komt.", ok: true, fb: "Een specifiek cijfer met een bron die je niet aanleverde is een klassiek hallucinatiesignaal. Controle tegen de primaire bron is de juiste stap." },
        { t: "Claude vragen of het cijfer klopt; als het bevestigt, kun je het gebruiken.", ok: false, fb: "Een bevestiging uit hetzelfde model is geen onafhankelijke controle." },
        { t: "Het cijfer laten staan maar 'circa' toevoegen.", ok: false, fb: "Een mogelijk verzonnen cijfer wordt daar niet betrouwbaarder van; je verspreidt het alleen voorzichtiger." }
      ] },
    { title: "Welke review past?",
      situation: "Je gebruikt Claude voor twee taken: (a) tien ideeën voor een teamuitje, (b) een brief aan een klant over een wijziging in de algemene voorwaarden. Welke aanpak is passend?",
      options: [
        { t: "Beide door de juridische afdeling laten checken voor de zekerheid.", ok: false, fb: "Niet evenredig: het teamuitje heeft geen juridisch risico. Zo maak je review een bottleneck." },
        { t: "(a) zelf snel beoordelen; (b) inhoud laten controleren door juridisch of de verantwoordelijke en de wijziging toetsen aan de nieuwe voorwaarden.", ok: true, fb: "Review evenredig aan de impact: externe communicatie met juridische gevolgen krijgt menselijke expertreview, een interne brainstorm niet." },
        { t: "Beide direct gebruiken; Claude is goed in schrijven.", ok: false, fb: "De klantbrief is externe communicatie met juridische gevolgen en vraagt om review." }
      ] }
  ],
  advice: [
    "Dit domein weegt het zwaarst. Besteed er ongeveer een vijfde van je studietijd aan, en oefen extra met scenariovragen.",
    "Leer de drie examensignalen herkennen: (1) specifieke details die je niet aanleverde, (2) zelfvertrouwen als schijnbewijs, (3) impact bepaalt de zwaarte van review.",
    "In antwoordopties is 'controleer tegen de officiële/primaire bron' vaak juist, en 'vraag Claude om zijn zekerheid' bijna altijd een afleider.",
    "Oefen met echte output: laat Claude een document samenvatten en zoek bewust naar weglatingen, verschuivingen in betekenis en niet-onderbouwde claims."
  ]
},

/* ===================================================== D3 */
d3: {
  intro: "Een Associate kiest het juiste gereedschap: welke productfunctie past bij de taak, welk modeltype hoort daarbij, en hoe ga je om met de grenzen van het contextvenster en geheugen. Het examen toetst begrip van afwegingen (kwaliteit, snelheid, kosten), niet het uit je hoofd kennen van prijslijsten. Productfunctionaliteit verandert snel; de feiten hieronder zijn gecontroleerd op 16 oktober 2026 tegen support.claude.com en de platformdocumentatie.",
  sections: [
    { sub: "d3.1", title: "Productfuncties: chat, Projects, research en artifacts", body: `
<p>Het examen noemt vier functies. Weet waarvoor elk dient:</p>
<ul>
<li><b>Chat</b>: losse gesprekken voor eenmalige vragen en taken. Snel en flexibel, maar context uit een gesprek gaat niet automatisch mee naar het volgende.</li>
<li><b>Projects</b>: werkruimtes rond een onderwerp met <b>project knowledge</b> (geüploade documenten, tekst, code) en <b>project instructions</b> die in elk gesprek binnen het project gelden. Ideaal voor terugkerend werk met dezelfde bronnen en richtlijnen. Op Team- en Enterprise-plannen kun je Projects delen met collega's. Volgens de helpdocumentatie schakelt Claude op betaalde plannen automatisch <b>RAG-modus</b> in als de projectkennis het contextvenster nadert, zodat een project meer informatie kan bevatten. De projectnaam en -beschrijving zijn niet zichtbaar voor Claude; instructies en kennis wel.</li>
<li><b>Research</b>: een modus waarin Claude meerdere zoekopdrachten uitvoert over het web (en, als gekoppeld, interne bronnen) en een rapport met bronvermeldingen oplevert. Geschikt voor vragen die actuele of brede informatie vragen. Bronnen blijven controleren.</li>
<li><b>Artifacts</b>: zelfstandige output naast het gesprek, zoals documenten, code, diagrammen en interactieve apps. Geschikt voor iets wat je bewaart, verder bewerkt of deelt.</li>
</ul>
<p>Verwante functies die de examengids noemt bij de voorbereiding: <b>Memory</b>, <b>Skills</b> en <b>Code Execution</b>. Skills zijn pakketjes instructies (en eventueel scripts) die Claude laadt wanneer een taak erom vraagt, bijvoorbeeld voor een vast documentformaat. Code-uitvoering laat Claude berekeningen doen en bestanden maken en analyseren, wat betrouwbaarder is dan rekenen "uit het hoofd".</p>
<p><b>Keuzelogica</b>: eenmalig en kort → chat. Terugkerend met vaste bronnen en instructies → Project. Actuele informatie uit veel bronnen → Research of web search. Iets om te bewaren, bewerken of delen → artifact. Rekenen of data analyseren → code-uitvoering.</p>` },
    { sub: "d3.2", title: "Modeltypen: Haiku, Sonnet en Opus", body: `
<p>Claude-modellen komen in families met een vaste rolverdeling. Het examen gaat uit van drie typen:</p>
<div class="tbl"><table>
<thead><tr><th>Type</th><th>Profiel</th><th>Typische taken</th></tr></thead>
<tbody>
<tr><td><b>Haiku</b></td><td>Snelst en goedkoopst</td><td>Grote volumes eenvoudige taken: classificeren, gegevens extraheren, routeren, korte standaardantwoorden.</td></tr>
<tr><td><b>Sonnet</b></td><td>Balans tussen snelheid en intelligentie</td><td>Het meeste dagelijkse kenniswerk: schrijven, analyseren, samenvatten.</td></tr>
<tr><td><b>Opus</b></td><td>Meest capabel van deze drie, langzamer en duurder</td><td>Complexe redenering, lange meerstaps- en analysetaken, lastige afwegingen.</td></tr>
</tbody></table></div>
<p>Actuele stand (platformdocumentatie, oktober 2026): de huidige generatie bestaat uit Claude Haiku 5.5, Sonnet 5.5 en Opus 5.5, en daarboven een nog zwaardere klasse (Fable 5.1) voor de meest veeleisende redeneertaken. De documentatie adviseert Opus 5.5 als standaardstartpunt voor de meeste werklasten. Het examen vraagt naar de afweging tussen de typen, niet naar versienummers of prijzen; die veranderen.</p>
<p>In de Claude-app kies je het model in de modelkiezer. Niet elk model is op elk plan beschikbaar; controleer dat in je eigen omgeving.</p>` },
    { sub: "d3.3", title: "Modelkeuze afstemmen op kosten, snelheid en kwaliteit", body: `
<p>Er is geen "beste model", alleen een best passend model. Stel drie vragen:</p>
<ul>
<li><b>Hoe complex is de redenering?</b> Meerdere stappen, nuance, afwegingen, lange documenten → een capabeler model.</li>
<li><b>Hoeveel en hoe snel?</b> Duizenden korte, eenvoudige taken of realtime reacties → een sneller, goedkoper model.</li>
<li><b>Wat kost een fout?</b> Hoge impact rechtvaardigt een capabeler model én extra review.</li>
</ul>
<p>Een veelgebruikt patroon is <b>mixen</b>: een snel model voor de eerste triage of classificatie, een capabeler model voor de gevallen die echt nadenken vragen. Begin bij twijfel met een redelijk model, test op een paar representatieve voorbeelden en schaal op of af op basis van resultaat.</p>
<p>Valkuil in examenvragen: "altijd het krachtigste model" klinkt veilig, maar verspilt budget en tijd bij eenvoudige volumetaken. Omgekeerd is het goedkoopste model kiezen voor een complexe juridische analyse een kwaliteitsrisico.</p>` },
    { sub: "d3.4", title: "Contextlimieten en geheugen beheren", body: `
<p>Het <b>contextvenster</b> is de hoeveelheid tekst (in tokens) die Claude in één gesprek tegelijk kan meenemen: je berichten, de antwoorden, geüploade bestanden en projectkennis. Het venster is groot, maar niet oneindig. Lange gesprekken hebben bovendien praktische nadelen: oude, verworpen instructies blijven meewegen en de focus kan verwateren.</p>
<p>Het examen noemt drie beslissingen: <b>restart, summarize, persist</b>.</p>
<ul>
<li><b>Restart</b>: begin een nieuw gesprek wanneer het onderwerp wisselt, het gesprek rommelig is geworden of Claude oude instructies blijft volgen.</li>
<li><b>Summarize</b>: laat Claude de stand van zaken (besluiten, open punten, kernfeiten) samenvatten en neem die samenvatting mee naar een nieuw gesprek.</li>
<li><b>Persist</b>: informatie die je steeds nodig hebt, hoort in projectkennis of projectinstructies, niet in elk gesprek opnieuw geplakt.</li>
</ul>
<p><b>Memory</b> (volgens support.claude.com): Claude onthoudt losse onderwerpen uit je gesprekken en kan op betaalde plannen eerdere gesprekken doorzoeken. Elk Project heeft een eigen geheugen dat gescheiden is van andere projecten; binnen een project gebruikt Claude daarnaast je accountgeheugen, tenzij je "Use account memory" voor dat project uitzet. Je kunt memory bekijken, aanpassen, pauzeren of resetten, en een incognitogesprek wordt niet in geschiedenis of memory opgenomen. Op Enterprise kan een beheerder memory organisatiebreed uitschakelen.</p>
<p>Praktisch gevolg: wil je dat Claude iets betrouwbaar weet in elk gesprek over een onderwerp, zet het dan expliciet in projectinstructies of -kennis. Memory is een gemak, geen gecontroleerde kennisbron.</p>` }
  ],
  terms: [
    ["Projects", "Werkruimte met eigen kennis, instructies en geheugen."],
    ["Project knowledge", "Documenten en tekst die in elk projectgesprek beschikbaar zijn."],
    ["Research (mode)", "Meerstaps zoeken met een rapport en bronvermelding."],
    ["Artifacts", "Zelfstandige output naast het gesprek."],
    ["Haiku / Sonnet / Opus", "Modeltypen: snel en goedkoop / balans / meest capabel."],
    ["Context window", "Maximale hoeveelheid tekst die in één gesprek meeweegt."],
    ["Tokens", "Eenheden waarin tekst wordt gemeten (ongeveer een woorddeel)."],
    ["Latency", "Reactietijd."],
    ["Memory", "Wat Claude over gesprekken heen onthoudt."],
    ["RAG (retrieval)", "Alleen relevante delen van een grote kennisbank ophalen."],
    ["Restart / summarize / persist", "Nieuw gesprek / samenvatten / vastleggen in project."]
  ],
  examples: [
    { title: "Wekelijkse rapportage",
      bad: "Elke maandag een nieuw chatgesprek starten en opnieuw het sjabloon, de huisstijlregels en de KPI-definities plakken.",
      good: "Een Project 'Weekrapportage' met de KPI-definities en een voorbeeldrapport als projectkennis, en instructies over structuur, toon en controles.",
      why: "Terugkerend werk met vaste bronnen hoort in een Project (persist). Dat bespaart tijd en zorgt voor consistente output." },
    { title: "Modelkeuze voor ticketlabels",
      bad: "Het meest capabele model gebruiken om 5.000 supporttickets een van zes labels te geven.",
      good: "Een snel, goedkoop model voor het labelen, met een steekproef ter controle; alleen twijfelgevallen naar een capabeler model.",
      why: "Eenvoudige classificatie in hoog volume past bij een sneller model. Capaciteit inzetten waar die nodig is." }
  ],
  pitfalls: [
    "Denken dat het duurste model altijd de beste keuze is.",
    "Verwachten dat Claude iets uit een vorig gesprek weet terwijl het niet in een Project of memory is vastgelegd.",
    "Eén eindeloos gesprek voor alles gebruiken, waardoor oude instructies blijven doorwerken.",
    "Research-output zonder controle van de bronnen overnemen.",
    "Ervan uitgaan dat de projectnaam of -beschrijving iets over de taak vertelt aan Claude; gebruik daarvoor instructies.",
    "Versienummers en prijzen uit het hoofd leren: die veranderen. Leer de afwegingen."
  ],
  scenarios: [
    { title: "Het lange strategiegesprek",
      situation: "Je werkt al dagen in één gesprek aan een strategie. Claude begint terug te vallen op een doelgroep die je twee dagen geleden hebt laten vallen. Wat doe je?",
      options: [
        { t: "Laat Claude de actuele besluiten en open punten samenvatten, controleer die, en start een nieuw gesprek met die samenvatting.", ok: true, fb: "Summarize + restart: je neemt alleen de geldende stand mee en laat de verworpen sporen achter." },
        { t: "Overschakelen naar een capabeler model in hetzelfde gesprek.", ok: false, fb: "Het probleem is de vervuilde context, niet het model. De oude instructies blijven in het gesprek staan." },
        { t: "In elk bericht herhalen dat de oude doelgroep niet meer geldt.", ok: false, fb: "Werkt soms, maar is foutgevoelig en lost de onderliggende oorzaak niet op." }
      ] },
    { title: "Concurrentieanalyse",
      situation: "Je wilt een overzicht van recente productlanceringen van vijf concurrenten in de afgelopen zes maanden. Welke functie past het best?",
      options: [
        { t: "Een gewone chat zonder zoekfunctie, want Claude kent de markt.", ok: false, fb: "Zonder zoekfunctie werkt Claude met trainingskennis tot een afkapdatum; recente lanceringen kunnen ontbreken of verzonnen worden." },
        { t: "Research (of web search) gebruiken, de bronnen controleren en het resultaat als tabel laten opleveren.", ok: true, fb: "Actuele, brede informatie vraagt om zoeken met bronnen. Een tabel maakt de vergelijking overzichtelijk." },
        { t: "Een Project aanmaken met je eigen notities over de concurrenten.", ok: false, fb: "Een Project is zinvol voor terugkerend werk, maar levert geen nieuwe actuele informatie op." }
      ] }
  ],
  advice: [
    "Maak voor jezelf een beslisboom: eenmalig/terugkerend, actueel/stabiel, bewaren/lezen, eenvoudig/complex. De meeste vragen in dit domein vallen daarin.",
    "Oefen in de app: maak een Project met instructies en kennis, gebruik Research voor een actuele vraag en laat een artifact maken. Ervaring met de functies maakt de vragen veel makkelijker.",
    "Bij modelvragen: zoek in het scenario naar volume, snelheid, complexiteit en impact. Die vier woorden bepalen het antwoord."
  ]
}

});
