/* CCAO-F leermodules, domein 4–7. */
Academy.addModules("ccaof", {

/* ===================================================== D4 */
d4: {
  intro: "Een Associate gebruikt Claude niet alleen voor losse taken, maar herkent kansen om processen te verbeteren. Dit domein toetst of je use cases kunt analyseren, Claude kunt inzetten voor onderzoek en planning, oplossingen iteratief kunt ontwerpen, Claude zinvol in bestaande werkprocessen kunt inpassen en de waarde én grenzen eerlijk kunt uitleggen aan stakeholders. Het ontwerpen van technische integraties of agentsystemen valt buiten dit examen; dat hoort bij Developer en Architect.",
  sections: [
    { sub: "d4.1", title: "Eisen en use cases analyseren", body: `
<p>Begin bij het probleem, niet bij de tool. Een goede use case-analyse beantwoordt:</p>
<ul>
<li><b>Wat is het knelpunt?</b> Tijd, kwaliteit, consistentie, capaciteit? Hoe vaak komt de taak voor?</li>
<li><b>Wat is de input en wat de gewenste output?</b> Zijn de bronnen beschikbaar en mag je ze gebruiken (zie domein 6)?</li>
<li><b>Wat is het risico bij fouten?</b> Bepaalt de mate van review.</li>
<li><b>Hoe meet je succes?</b> Tijdsbesparing, minder fouten, snellere doorlooptijd, tevredenheid.</li>
</ul>
<p>Claude zelf kan helpen bij de analyse: laat ruwe aantekeningen uit stakeholdergesprekken ordenen tot eisen, laat ontbrekende vragen of tegenstrijdige eisen signaleren, of laat use cases prioriteren op een raster van impact en haalbaarheid.</p>
<p><b>Goede kandidaten</b> voor Claude: terugkerend tekstwerk, samenvatten en ordenen van informatie, eerste concepten, vergelijken van documenten, analyseren van ongestructureerde feedback. <b>Minder geschikt</b>: taken die exacte, gegarandeerd foutloze output vereisen zonder controle, beslissingen over mensen zonder menselijke tussenkomst, of taken waarvoor de data niet gedeeld mag worden.</p>` },
    { sub: "d4.2", title: "Onderzoek, planning en procesoptimalisatie", body: `
<ul>
<li><b>Onderzoek</b>: Research of web search voor een verkenning met bronnen; geüploade documenten voor analyse van interne stukken. Formuleer de onderzoeksvraag scherp en controleer de bronnen.</li>
<li><b>Planning</b>: projectplannen, tijdlijnen, risicoregisters, RACI-opzetten en draaiboeken als eerste versie laten opstellen, die het team daarna aanscherpt. Laat Claude ook afhankelijkheden en risico's benoemen die je over het hoofd ziet.</li>
<li><b>Procesoptimalisatie</b>: beschrijf het huidige proces stap voor stap en vraag Claude om knelpunten, dubbel werk en automatiseringskansen te markeren. Laat Claude een toekomstig proces voorstellen, maar toets dat aan de praktijk met de mensen die het werk doen.</li>
</ul>
<p>Claude is hier een denkpartner die versnelt, geen vervanging van kennis van de organisatie. De output is een startpunt dat je valideert met data en betrokkenen.</p>` },
    { sub: "d4.3", title: "Oplossingsontwerp, ontwikkeling en iteratie", body: `
<p>Werk iteratief: klein beginnen, testen met echte voorbeelden, verbeteren, dan opschalen.</p>
<ol>
<li><b>Prototype</b>: test de aanpak op een handvol representatieve gevallen, inclusief lastige randgevallen.</li>
<li><b>Evalueren</b>: beoordeel de output op vooraf bepaalde criteria. Wat gaat goed, wat structureel mis?</li>
<li><b>Bijstellen</b>: verbeter prompt, instructies, bronnen of werkverdeling.</li>
<li><b>Pilot</b>: gebruik in een beperkte groep met feedback.</li>
<li><b>Uitrollen en onderhouden</b>: documenteer de werkwijze, train gebruikers, plan periodieke review.</li>
</ol>
<p>Artifacts helpen bij het ontwerpen: een interactieve mockup, een checklist-tool of een proceskaart maak je snel om met stakeholders te bespreken.</p>
<p><b>Grens van de rol</b>: als een oplossing vraagt om API-koppelingen, automatische verwerking zonder menselijke controle, maatwerkcode in productie of agentarchitectuur, escaleer je naar een Developer of Architect. Jij levert dan de procesanalyse en eisen aan.</p>` },
    { sub: "d4.4", title: "Claude integreren in bestaande workflows", body: `
<p>Twee manieren om Claude in te passen:</p>
<ul>
<li><b>Augmenteren</b>: het bestaande proces blijft, Claude versnelt stappen. Bijvoorbeeld: een recruiter laat vacatureteksten opstellen, maar selectie blijft menselijk werk.</li>
<li><b>Herontwerpen</b>: het proces verandert omdat Claude nieuwe mogelijkheden biedt. Bijvoorbeeld: in plaats van een maandelijks handmatig rapport een Project waarin het team op elk moment vragen kan stellen over actuele documenten.</li>
</ul>
<p>Begin meestal met augmenteren: lager risico, snelle winst, en je leert waar Claude goed en minder goed werkt. Herontwerp volgt op basis van bewijs.</p>
<p>Ontwerpprincipes:</p>
<ul>
<li>Plaats <b>controlepunten</b> waar fouten de meeste schade doen (vóór verzenden, publiceren, besluiten).</li>
<li>Gebruik <b>connectors</b> (bijvoorbeeld Google Drive of Gmail) om informatie op te halen waar die al staat, in plaats van kopiëren en plakken, voor zover beleid dat toestaat.</li>
<li>Leg vast <b>wie</b> verantwoordelijk is voor de output in elke stap.</li>
<li>Meet het effect: vergelijk doorlooptijd of kwaliteit vóór en na.</li>
</ul>` },
    { sub: "d4.5", title: "Waarde en grenzen communiceren aan stakeholders", body: `
<p>Verwachtingen managen is een kerntaak. Zowel overschatten ("AI doet dit volledig automatisch") als onderschatten ("AI is onbetrouwbaar, niet aan beginnen") leidt tot slechte beslissingen.</p>
<ul>
<li><b>Waarde concreet maken</b>: tijdsbesparing per taak, snellere doorlooptijd, meer consistentie, gemeten in een pilot in plaats van beloofd.</li>
<li><b>Grenzen eerlijk benoemen</b>: kans op fouten en hallucinaties, behoefte aan review, afkapdatum van kennis, datagevoeligheid, contextlimieten.</li>
<li><b>Afstemmen op het publiek</b>: een CFO wil kosten en risico's, een teamleider wil weten wat er verandert in het werk, juridische zaken wil weten hoe data wordt behandeld.</li>
<li><b>Mensen centraal</b>: leg uit dat Claude werk ondersteunt en dat verantwoordelijkheid bij mensen blijft.</li>
</ul>` }
  ],
  terms: [
    ["Use case", "Concrete toepassing met doel, input, output en gebruiker."],
    ["Requirements", "Eisen waaraan een oplossing moet voldoen."],
    ["Augment vs. redesign", "Een proces ondersteunen versus herinrichten."],
    ["Pilot", "Beperkte proefperiode om effect te meten."],
    ["Stakeholder", "Belanghebbende die geraakt wordt of beslist."],
    ["Checkpoint", "Controlemoment in een proces."],
    ["Connectors", "Koppelingen met apps zoals Google Drive of Gmail."],
    ["Process optimization", "Een proces efficiënter of effectiever maken."],
    ["Escalate", "Werk doorgeven aan een Developer/Architect of expert."]
  ],
  examples: [
    { title: "Pitch aan het MT",
      bad: "'Met Claude automatiseren we de hele klantenservice en besparen we 80% van de kosten.'",
      good: "'In een pilot van vier weken met twee medewerkers daalde de tijd om een antwoord op te stellen van gemiddeld 12 naar 5 minuten. Elk antwoord wordt nog door de medewerker gecontroleerd. Voorstel: uitbreiden naar het hele team met dezelfde controle.'",
      why: "De goede pitch is gebaseerd op gemeten resultaten, benoemt de controle en doet een stapsgewijs voorstel. De slechte belooft ongetoetste resultaten en verzwijgt grenzen." },
    { title: "Inpassen in een werkproces",
      bad: "Claude schrijft offertes en die worden automatisch naar klanten gestuurd om tijd te besparen.",
      good: "Claude stelt een conceptofferte op uit een Project met prijslijst en voorwaarden; de accountmanager controleert prijzen en voorwaarden en verstuurt zelf.",
      why: "Een controlepunt vóór externe verzending voorkomt dat fouten bij klanten terechtkomen. Automatisch verzenden zou bovendien technische integratie vragen buiten de Associate-rol." }
  ],
  pitfalls: [
    "Starten bij de tool ('wat kunnen we met AI?') in plaats van bij het probleem.",
    "Meteen het hele proces herontwerpen zonder kleinschalige test.",
    "Waarde beloven zonder meting, of grenzen verzwijgen om draagvlak te krijgen.",
    "Controlepunten vergeten bij stappen met externe impact.",
    "Zelf een technische integratie willen bouwen terwijl dat bij een Developer of Architect hoort."
  ],
  scenarios: [
    { title: "Waar begin je?",
      situation: "Je afdeling vraagt je 'iets met Claude te doen' om de werkdruk te verlagen. Wat is de beste eerste stap?",
      options: [
        { t: "Alle medewerkers een licentie geven en ze zelf laten uitzoeken wat werkt.", ok: false, fb: "Zonder analyse van taken, risico's en beleid ontstaat wildgroei en weet je niet wat het oplevert." },
        { t: "Inventariseren welke terugkerende taken veel tijd kosten, die beoordelen op geschiktheid en risico, en met één of twee kansrijke use cases een kleine pilot starten.", ok: true, fb: "Probleemgericht, risicobewust en meetbaar. Dit is de verwachte aanpak op Associate-niveau." },
        { t: "Een ontwikkelaar vragen een chatbot te bouwen die alle vragen beantwoordt.", ok: false, fb: "Een technische oplossing kiezen voordat je weet wat het probleem is. Bovendien een groot project zonder bewezen waarde." }
      ] }
  ],
  advice: [
    "Herken in scenariovragen het woord 'eerste stap': het antwoord is meestal analyseren of klein testen, niet groot uitrollen.",
    "Onthoud de rolgrens: Associates ontwerpen workflows en escaleren technische implementatie.",
    "Oefen een korte pitch voor een use case uit je eigen werk met waarde, grenzen, controle en meting."
  ]
},

/* ===================================================== D5 */
d5: {
  intro: "Configuratie is wat losse prompts verandert in een betrouwbare werkomgeving. Dit domein gaat over het inrichten van Claude Projects met instructies en kennisbronnen, het beheren van geüploade documenten en connectors, het schrijven van goede instructies op projectniveau, en het onderhouden daarvan als bronnen en eisen veranderen.",
  sections: [
    { sub: "d5.1", title: "Projects inrichten met instructies en kennisbronnen", body: `
<p>Een Project bestaat (volgens support.claude.com) uit:</p>
<ul>
<li><b>Project instructions</b>: vaste richtlijnen die in alle gesprekken binnen het project gelden.</li>
<li><b>Project knowledge</b>: geüploade bestanden, tekst of code die in elk gesprek als context beschikbaar zijn.</li>
<li>Een eigen <b>projectgeheugen</b>, gescheiden van andere projecten (je accountgeheugen kan wel meedoen, tenzij je dat per project uitzet).</li>
</ul>
<p>Belangrijke details: context uit losse gesprekken gaat niet over naar andere gesprekken tenzij je het aan de kennis toevoegt. De projectnaam en beschrijving ziet Claude niet. Projects zijn standaard privé; op Team- en Enterprise-plannen kun je ze delen met collega's met bewerk- of alleen-gebruiksrechten.</p>
<p>Inrichtingsstappen:</p>
<ol>
<li>Bepaal het doel en de gebruikers van het project.</li>
<li>Verzamel de <b>gezaghebbende</b> bronnen: actuele versies, geen concepten of dubbele versies.</li>
<li>Schrijf instructies (zie d5.3).</li>
<li>Test met realistische vragen, inclusief vragen waarop het antwoord niet in de kennis staat.</li>
<li>Deel met het team en verzamel feedback.</li>
</ol>` },
    { sub: "d5.2", title: "Geüploade kennis en connectors beheren", body: `
<p><b>Kennisbeheer</b>:</p>
<ul>
<li><b>Kwaliteit boven kwantiteit</b>: tien actuele, relevante documenten werken beter dan vijftig documenten met verouderde en tegenstrijdige versies.</li>
<li><b>Geen tegenstrijdigheden</b>: staan er twee versies van een beleid in, dan kan Claude de verkeerde gebruiken. Verwijder oude versies of markeer duidelijk welke geldt.</li>
<li><b>Duidelijke namen en structuur</b>: "Reiskostenbeleid_2026_v3_geldig" zegt meer dan "beleid(2).pdf".</li>
<li><b>Gevoelige data</b>: upload alleen wat het beleid toestaat; kennis in een gedeeld project is zichtbaar voor iedereen met toegang (zie domein 6).</li>
</ul>
<p><b>Connectors</b> koppelen Claude aan apps zoals Google Drive, Gmail of agenda's, zodat Claude informatie kan ophalen waar die staat. Voordelen: actuele informatie zonder kopiëren. Aandachtspunten:</p>
<ul>
<li>Claude werkt met de rechten van de gebruiker die de connector koppelt: wat jij kunt zien, kan Claude via de connector ophalen.</li>
<li>Koppel alleen wat nodig is (least privilege) en volg het organisatiebeleid; beheerders kunnen bepalen welke connectors beschikbaar zijn.</li>
<li>Controleer of opgehaalde informatie de juiste en actuele bron is.</li>
</ul>
<p>Gebruik een connector voor informatie die verandert en elders wordt beheerd; gebruik projectkennis voor stabiele referentiedocumenten die bij het project horen.</p>` },
    { sub: "d5.3", title: "Effectieve instructies op projectniveau", body: `
<p>Projectinstructies werken als een vaste briefing (vergelijkbaar met een system prompt). Goede instructies bevatten:</p>
<ul>
<li><b>Doel en context</b>: waar is dit project voor, wie gebruikt het, voor welk publiek is de output?</li>
<li><b>Werkwijze</b>: welke bronnen leidend zijn, hoe om te gaan met ontbrekende informatie ("zeg dat het niet in de kennisbank staat en verwijs naar HR").</li>
<li><b>Outputformaat en toon</b>: structuur, lengte, taal, huisstijl.</li>
<li><b>Grenzen</b>: waar het project niet voor is, wanneer naar een mens verwezen moet worden.</li>
</ul>
<pre class="prompt">Doel: medewerkers helpen met vragen over het verlof- en reisbeleid.
Bronnen: gebruik alleen de documenten in de projectkennis. Noem bij elk
antwoord het document en de paragraaf.
Ontbreekt het antwoord in de bronnen? Zeg dat duidelijk en verwijs naar
hr@voorbeeld.nl. Ga niet gissen.
Toon: vriendelijk en zakelijk, je-vorm, maximaal 150 woorden.
Buiten scope: individuele salarissen, medische situaties en juridisch
advies. Verwijs daarvoor naar HR.</pre>
<p>Valkuilen: tegenstrijdige instructies ("wees uitgebreid" en "maximaal 50 woorden"), vage instructies ("wees behulpzaam"), en instructies die in elk gesprek anders geïnterpreteerd kunnen worden. Schrijf de reden erbij waar een eis niet vanzelfsprekend is.</p>` },
    { sub: "d5.4", title: "Configuraties onderhouden en bijwerken", body: `
<p>Een project is nooit af. Kennis veroudert, beleid verandert, en gebruikers vinden randgevallen.</p>
<ul>
<li><b>Eigenaarschap</b>: wijs een eigenaar aan die verantwoordelijk is voor de inhoud.</li>
<li><b>Versiebeheer</b>: vervang een document bij een nieuwe versie en verwijder de oude, zodat er nooit twee geldende versies naast elkaar staan.</li>
<li><b>Periodieke review</b>: plan een vast moment (bijvoorbeeld elk kwartaal) om bronnen en instructies te controleren.</li>
<li><b>Feedbacklus</b>: verzamel voorbeelden van slechte antwoorden en vertaal die naar betere instructies of ontbrekende kennis.</li>
<li><b>Gebruikers informeren</b>: laat het team weten wanneer instructies of bronnen veranderen en wat dat betekent.</li>
<li><b>Testen na wijziging</b>: stel na een update een vaste set testvragen opnieuw om te zien of de antwoorden nog kloppen.</li>
</ul>` }
  ],
  terms: [
    ["Project instructions", "Vaste richtlijnen die in elk projectgesprek gelden."],
    ["Project knowledge / knowledge base", "Bronnen die in elk projectgesprek beschikbaar zijn."],
    ["System-level instructions", "Instructies op een hoger niveau dan het losse bericht."],
    ["Connectors", "Koppelingen met externe apps (Google Drive, Gmail)."],
    ["Least privilege", "Alleen de toegang geven die nodig is."],
    ["Source of truth", "De gezaghebbende, geldende bron."],
    ["Version control", "Bijhouden welke versie van een document geldt."],
    ["Sharing permissions", "Rechten om een project te bewerken of te gebruiken."]
  ],
  examples: [
    { title: "Kennisbank voor een HR-project",
      bad: "Alle bestanden uit de HR-map uploaden, inclusief drie oude versies van het verlofbeleid en een concept dat nooit is vastgesteld.",
      good: "Alleen de vastgestelde, actuele versies uploaden met heldere bestandsnamen, en een eigenaar die bij elke beleidswijziging de oude versie vervangt.",
      why: "Tegenstrijdige versies leiden tot onjuiste antwoorden die met overtuiging worden gegeven." },
    { title: "Instructie bij ontbrekende informatie",
      bad: "'Beantwoord alle vragen van medewerkers.'",
      good: "'Beantwoord vragen alleen op basis van de projectkennis. Staat het antwoord er niet in, zeg dat en verwijs naar HR.'",
      why: "De goede instructie geeft Claude toestemming om aan te geven dat iets ontbreekt. Dat vermindert gissen en hallucinaties." }
  ],
  pitfalls: [
    "Denken dat meer documenten altijd betere antwoorden opleveren.",
    "Oude versies laten staan naast nieuwe.",
    "Belangrijke informatie in de projectnaam of beschrijving zetten in plaats van in de instructies.",
    "Connectors met brede toegang koppelen zonder te controleren wat Claude dan kan inzien.",
    "Een project inrichten en nooit meer onderhouden.",
    "Tegenstrijdige of vage instructies schrijven."
  ],
  scenarios: [
    { title: "Verkeerde antwoorden na beleidswijziging",
      situation: "Na een wijziging van het thuiswerkbeleid geeft het HR-project soms de oude regels. Wat is de meest waarschijnlijke oorzaak en oplossing?",
      options: [
        { t: "De oude versie staat nog in de projectkennis naast de nieuwe; verwijder de oude versie en test met een paar vragen.", ok: true, fb: "Tegenstrijdige bronnen zijn de meest voorkomende oorzaak. Opschonen en testen na een update is goed onderhoud." },
        { t: "Overstappen naar een capabeler model.", ok: false, fb: "Ook een capabeler model kan niet weten welke van twee documenten geldt als beide aanwezig zijn." },
        { t: "Gebruikers vragen in elke vraag te vermelden dat het nieuwe beleid geldt.", ok: false, fb: "Een workaround die de oorzaak laat bestaan en afhankelijk is van discipline van gebruikers." }
      ] }
  ],
  advice: [
    "Richt zelf een Project in met instructies en twee of drie documenten. Stel daarna vragen waarvan het antwoord wél, niet en half in de bronnen staat.",
    "Onthoud het onderscheid: instructies sturen gedrag, kennis levert inhoud, connectors halen actuele informatie op.",
    "In examenvragen over slechte projectantwoorden: kijk eerst naar bronkwaliteit en instructies, pas daarna naar het model."
  ]
},

/* ===================================================== D6 */
d6: {
  intro: "Verantwoord gebruik weegt 15% en komt in veel scenario's terug, ook in andere domeinen. Het examen verwacht dat je geschikte en ongeschikte toepassingen herkent, zorgvuldig omgaat met gevoelige gegevens en regelgeving, het AI-beleid van je organisatie volgt, en de ethische kant van AI-gebruik begrijpt. Typisch is het 'evenredige' antwoord: het werk laten doorgaan met de juiste waarborgen, in plaats van blind doorgaan of alles stoppen.",
  sections: [
    { sub: "d6.1", title: "Geschikte en ongeschikte use cases", body: `
<p>Een use case is geschikt wanneer het risico beheersbaar is met de beschikbare controle. Vragen om te stellen:</p>
<ul>
<li>Wat is de impact op mensen als de output fout is?</li>
<li>Kan een mens de output betekenisvol beoordelen voordat er iets gebeurt?</li>
<li>Mag de benodigde data volgens beleid en wet gebruikt worden?</li>
<li>Is transparantie nodig richting de mensen die geraakt worden?</li>
</ul>
<p><b>Doorgaans geschikt</b> (met passende review): concepten schrijven, samenvatten, brainstormen, informatie ordenen, analyses voorbereiden, leren en uitleg.</p>
<p><b>Vereisen extra waarborgen of zijn ongeschikt</b>: geautomatiseerde beslissingen over mensen (aanname, ontslag, kredietwaardigheid) zonder menselijke tussenkomst; medische, juridische of financiële adviezen die zonder expert worden opgevolgd; content die misleidt (nep-reviews, je voordoen als iemand anders); toepassingen die het beleid of de gebruiksvoorwaarden van Anthropic schenden.</p>` },
    { sub: "d6.2", title: "Gevoelige data, regelgeving en privacy", body: `
<p>Uitgangspunt: deel niet meer data dan nodig is (<b>dataminimalisatie</b>) en volg wat beleid en wet toestaan.</p>
<ul>
<li><b>Persoonsgegevens (PII)</b>: namen, adressen, klantnummers, BSN, gezondheidsgegevens. Vraag je af of de identificatie nodig is voor de taak. Vaak kan het met <b>anonimiseren</b> of <b>pseudonimiseren</b>: namen vervangen door codes, identificerende kolommen verwijderen.</li>
<li><b>Bijzondere categorieën</b> onder de AVG/GDPR (zoals gezondheid, etniciteit, religie) vragen extra bescherming.</li>
<li><b>Vertrouwelijke bedrijfsinformatie</b>: ongepubliceerde cijfers, contracten, strategie. Gebruik alleen goedgekeurde omgevingen (bijvoorbeeld het zakelijke plan van je organisatie) volgens beleid.</li>
<li><b>Sectorregels</b>: zorg, financiële sector en overheid hebben vaak aanvullende eisen.</li>
</ul>
<p>Een instructie aan Claude als "onthoud dit niet" is <b>geen</b> privacymaatregel die beleid vervangt. De controle zit vóór het uploaden: verwijder of anonimiseer wat er niet in hoort, of gebruik een goedgekeurde omgeving.</p>
<p>Het examen beloont de oplossing die de taak mogelijk maakt <b>en</b> het beleid respecteert: anonimiseren en dan analyseren, in plaats van "toch uploaden" of "dan maar niet".</p>` },
    { sub: "d6.3", title: "Organisatiebeleid en governance volgen", body: `
<p>Veel organisaties hebben een AI-beleid met onder meer: welke tools en plannen zijn goedgekeurd, welke data in welke tool mag, wanneer review verplicht is, hoe AI-gebruik wordt vermeld, en wie je bij twijfel benadert.</p>
<ul>
<li><b>Gebruik goedgekeurde tools en accounts</b>: geen privé-account voor werkdata ('shadow AI').</li>
<li><b>Volg datarichtlijnen</b> en de instellingen die beheerders hebben gekozen (connectors, delen, memory).</li>
<li><b>Transparantie</b>: vermeld AI-ondersteuning waar beleid of context dat vereist.</li>
<li><b>Bij twijfel escaleren</b> naar de beleidseigenaar, privacy officer of compliance in plaats van zelf een uitzondering te maken.</li>
<li><b>Verantwoordelijkheid blijft bij de mens</b>: "Claude heeft het geschreven" is geen excuus voor fouten.</li>
</ul>` },
    { sub: "d6.4", title: "Ethische implicaties van AI-gebruik", body: `
<ul>
<li><b>Eerlijkheid en bias</b>: output kan stereotypen of eenzijdige perspectieven bevatten. Controleer extra bij teksten over of voor diverse groepen en bij alles wat mensen beoordeelt.</li>
<li><b>Transparantie</b>: mensen hebben er belang bij te weten wanneer ze met AI-gegenereerde inhoud of een AI-systeem te maken hebben, zeker bij beslissingen die hen raken.</li>
<li><b>Verantwoording</b>: er is altijd een mens eigenaar van het resultaat.</li>
<li><b>Intellectueel eigendom</b>: wees voorzichtig met het overnemen van beschermd materiaal van anderen.</li>
<li><b>Impact op werk en mensen</b>: communiceer zorgvuldig over veranderingen in taken.</li>
<li><b>Misleiding vermijden</b>: geen nep-content, geen gefabriceerde citaten of onderzoeken, geen imitatie van echte personen.</li>
</ul>` }
  ],
  terms: [
    ["PII (personally identifiable information)", "Gegevens die een persoon identificeren."],
    ["Anonymization / pseudonymization", "Identificatie verwijderen / vervangen door codes."],
    ["Data minimization", "Alleen de data delen die voor de taak nodig is."],
    ["GDPR / AVG", "Europese privacywetgeving."],
    ["AI policy / governance", "Regels en toezicht op AI-gebruik in de organisatie."],
    ["Shadow AI", "AI-gebruik buiten goedgekeurde tools om."],
    ["Responsible AI", "Verantwoord, eerlijk en transparant AI-gebruik."],
    ["Accountability", "Verantwoording: een mens is eigenaar van het resultaat."],
    ["Acceptable use / Usage Policy", "Regels over wat wel en niet mag met een AI-dienst."]
  ],
  examples: [
    { title: "Klantdata analyseren",
      bad: "Een export met klantnamen, e-mailadressen en rekeningnummers uploaden 'omdat de analyse intern is', met de instructie 'gebruik dit alleen voor deze analyse'.",
      good: "Namen, e-mailadressen en rekeningnummers verwijderen of vervangen door klant-ID's, alleen de kolommen houden die voor de trendanalyse nodig zijn, en uploaden in de goedgekeurde zakelijke omgeving.",
      why: "Dataminimalisatie en anonimiseren laten de analyse doorgaan zonder beschermde gegevens bloot te stellen. Een instructie aan het model vervangt geen beleidsmaatregel." },
    { title: "Selectie van sollicitanten",
      bad: "Claude een ranglijst van 80 sollicitanten laten maken en de top 10 automatisch uitnodigen.",
      good: "Claude helpt bij het opstellen van objectieve selectiecriteria en een gestructureerd interviewformat; recruiters beoordelen de cv's zelf aan de hand van die criteria.",
      why: "Beslissingen over mensen vragen om menselijke beoordeling en bias-bewustzijn. Claude ondersteunt het proces zonder de beslissing te nemen." }
  ],
  pitfalls: [
    "Een instructie als 'bewaar dit niet' zien als vervanging van data-anonimisering of beleid.",
    "Persoonlijke accounts gebruiken voor werkdata omdat het sneller is.",
    "Het hele project stoppen bij een datarisico, terwijl anonimiseren de taak mogelijk maakt.",
    "Geautomatiseerde beslissingen over mensen zonder menselijke tussenkomst.",
    "Ervan uitgaan dat 'intern' betekent dat beleid niet geldt.",
    "Bij twijfel zelf een uitzondering maken in plaats van te escaleren."
  ],
  scenarios: [
    { title: "Medewerkerstevredenheid",
      situation: "Je wilt open antwoorden uit een medewerkersenquête laten analyseren. Sommige antwoorden noemen collega's bij naam en beschrijven gezondheidsklachten. Wat doe je?",
      options: [
        { t: "Upload alles; het is intern onderzoek.", ok: false, fb: "Namen en gezondheidsinformatie zijn gevoelige persoonsgegevens. 'Intern' heft beleid en wetgeving niet op." },
        { t: "Namen en herleidbare details verwijderen of vervangen, gezondheidsinformatie generaliseren, en controleren of het beleid deze analyse in de goedgekeurde omgeving toestaat.", ok: true, fb: "Dataminimalisatie en anonimisering, binnen beleid. De analyse kan doorgaan zonder onnodige risico's." },
        { t: "De analyse niet doen; enquêtes zijn te gevoelig voor AI.", ok: false, fb: "Onnodig: met anonimisering en binnen beleid is deze analyse goed mogelijk." }
      ] }
  ],
  advice: [
    "Zoek in governance-vragen het antwoord dat de taak mogelijk maakt met een waarborg: anonimiseren, goedgekeurde omgeving, menselijke review, escaleren.",
    "Herken drie standaardafleiders: 'het is intern dus prima', 'instrueer Claude om het niet te bewaren' en 'stop de taak helemaal'.",
    "Lees het AI-beleid van je eigen organisatie; het examen gaat ervan uit dat je zulk beleid volgt."
  ]
},

/* ===================================================== D7 */
d7: {
  intro: "Het kleinste domein (10%), maar het combineert alles: als output tegenvalt, moet je de oorzaak vinden en gericht verbeteren. Dit domein toetst systematisch diagnosticeren, bijsturen op basis van feedback en resultaten, en workflows efficiënter en effectiever maken.",
  sections: [
    { sub: "d7.1", title: "Slechte output diagnosticeren en oplossen", body: `
<p>Werk systematisch. Koppel het symptoom aan de waarschijnlijke oorzaak:</p>
<div class="tbl"><table>
<thead><tr><th>Symptoom</th><th>Waarschijnlijke oorzaak</th><th>Oplossing</th></tr></thead>
<tbody>
<tr><td>Generiek, oppervlakkig antwoord</td><td>Te weinig context of doel</td><td>Doel, doelgroep, bron en voorbeelden toevoegen</td></tr>
<tr><td>Verkeerd formaat of lengte</td><td>Formaat niet gespecificeerd</td><td>Expliciet formaat en lengte, eventueel een voorbeeld</td></tr>
<tr><td>Verzonnen feiten</td><td>Geen bron, of vraag buiten beschikbare kennis</td><td>Bron aanleveren, citaten vragen, toestemming om 'weet ik niet' te zeggen, zoekfunctie gebruiken</td></tr>
<tr><td>Instructies worden genegeerd</td><td>Tegenstrijdige of begraven instructies, lang rommelig gesprek</td><td>Instructies opschonen en prominent plaatsen, nieuw gesprek</td></tr>
<tr><td>Inconsistent tussen gesprekken</td><td>Instructies alleen in losse chats</td><td>Vastleggen in projectinstructies en voorbeelden</td></tr>
<tr><td>Verkeerde informatie in een Project</td><td>Verouderde of tegenstrijdige kennisbronnen</td><td>Bronnen opschonen en actualiseren</td></tr>
<tr><td>Oppervlakkig bij complexe taak</td><td>Te veel in één keer, of te licht model</td><td>Opknippen; capabeler model overwegen</td></tr>
<tr><td>Traag of duur bij simpele taak</td><td>Te zwaar model</td><td>Sneller model kiezen</td></tr>
</tbody></table></div>
<p>Verander <b>één ding tegelijk</b> en test met dezelfde voorbeelden, zodat je weet wat het verschil maakte. Begin bij de goedkoopste oplossing (prompt, context, bronnen) voordat je naar model of procesherontwerp gaat.</p>` },
    { sub: "d7.2", title: "Aanpak bijstellen op basis van feedback en resultaten", body: `
<ul>
<li><b>Verzamel feedback gestructureerd</b>: van gebruikers en lezers, met concrete voorbeelden van goede en slechte output.</li>
<li><b>Zoek patronen</b>: één slecht antwoord kan toeval zijn; terugkerende fouten wijzen op een structurele oorzaak.</li>
<li><b>Vertaal feedback naar aanpassingen</b>: in de prompt, de projectinstructies, de kennisbronnen of de werkverdeling.</li>
<li><b>Meet opnieuw</b>: gebruik een vaste testset van representatieve vragen of taken om te zien of het beter wordt.</li>
<li><b>Weet wanneer te stoppen of escaleren</b>: als een taak na redelijke iteratie onbetrouwbaar blijft, is Claude misschien niet de juiste oplossing voor die stap, of is een technische aanpak nodig (Developer/Architect).</li>
</ul>` },
    { sub: "d7.3", title: "Workflows optimaliseren", body: `
<p>Optimaliseren gaat om <b>efficiëntie</b> (minder tijd, kosten, handelingen) en <b>effectiviteit</b> (betere uitkomst).</p>
<ul>
<li><b>Herbruikbaarheid</b>: zet terugkerende prompts in projectinstructies, sjablonen of skills in plaats van ze steeds opnieuw te typen.</li>
<li><b>Bundelen</b>: verwerk vergelijkbare items samen (tien e-mails in één opdracht met een vast formaat) in plaats van elk apart.</li>
<li><b>Juiste model voor de stap</b>: lichter model voor eenvoudige stappen, zwaarder model waar het telt.</li>
<li><b>Context slank houden</b>: alleen relevante bronnen; samenvatten en opnieuw beginnen bij lange gesprekken.</li>
<li><b>Controle slim plaatsen</b>: review waar het risico zit, niet bij elke tussenstap.</li>
<li><b>Meten</b>: tijd per taak, aantal correctierondes, foutpercentage in steekproeven.</li>
</ul>
<p>Pas op met optimaliseren ten koste van kwaliteit: review schrappen om tijd te winnen is geen optimalisatie als het risico daarmee stijgt.</p>` }
  ],
  terms: [
    ["Troubleshooting", "Problemen systematisch opsporen en oplossen."],
    ["Root cause", "De onderliggende oorzaak van een probleem."],
    ["Test set", "Vaste set voorbeelden om verbeteringen te meten."],
    ["Feedback loop", "Cyclus van feedback verzamelen en verwerken."],
    ["Batching", "Vergelijkbare taken samen verwerken."],
    ["Efficiency / effectiveness", "Doelmatigheid / doeltreffendheid."],
    ["Templates", "Herbruikbare sjablonen voor prompts of output."]
  ],
  examples: [
    { title: "Inconsistente toon in klantmails",
      bad: "Elke medewerker schrijft een eigen prompt; de toon verschilt per mail. Oplossing: 'iedereen moet beter prompten'.",
      good: "Een gedeeld Project met tooninstructies en drie goedgekeurde voorbeeldmails; na twee weken een steekproef om te zien of de toon consistent is.",
      why: "De oorzaak is structureel (geen gedeelde instructies). De oplossing legt de standaard vast en meet het effect." }
  ],
  pitfalls: [
    "Meerdere dingen tegelijk veranderen, waardoor je niet weet wat hielp.",
    "Meteen het model de schuld geven terwijl context of bronnen het probleem zijn.",
    "Optimaliseren door review weg te halen bij risicovolle stappen.",
    "Eén slecht antwoord als patroon zien, of een terugkerend patroon als toeval.",
    "Blijven itereren zonder te meten of het beter wordt."
  ],
  scenarios: [
    { title: "De samenvattingen missen steeds de risico's",
      situation: "Het team gebruikt Claude om projectrapporten samen te vatten. Feedback: de samenvattingen zijn netjes, maar de risicoparagraaf ontbreekt regelmatig. Wat is de beste eerste stap?",
      options: [
        { t: "De instructie expliciet maken: 'neem altijd een sectie Risico's op met de risico's uit hoofdstuk 5', vastleggen in het Project en testen op vijf eerdere rapporten.", ok: true, fb: "Gerichte aanpassing van de instructie, structureel vastgelegd en gemeten op een testset." },
        { t: "Overstappen naar het duurste model.", ok: false, fb: "Het symptoom wijst op een ontbrekende instructie, niet op te weinig capaciteit. Eerst de goedkoopste, meest waarschijnlijke oplossing." },
        { t: "Teamleden vragen de risico's zelf toe te voegen.", ok: false, fb: "Verplaatst werk terug naar mensen zonder de oorzaak op te lossen." }
      ] }
  ],
  advice: [
    "Leer de symptoom-oorzaak-tabel. Bijna elke troubleshootingvraag is een variant daarvan.",
    "Bij 'wat is de eerste stap': kies de gerichte, goedkoopste aanpassing die de waarschijnlijke oorzaak raakt.",
    "Herken optimalisaties die stiekem kwaliteit of controle opofferen; dat zijn afleiders."
  ]
}

});
