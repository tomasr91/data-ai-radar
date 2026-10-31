/* CCDV-F samenvattingen per subonderwerp (één scherm per leerdoel).
   Gebaseerd op de officiële documentatie (platform.claude.com, code.claude.com, modelcontextprotocol.io,
   anthropic.com/engineering/building-effective-agents); gecontroleerd op 21 oktober 2026.
   Structuur: per domein { sections: [{ sub, title, body (HTML) }] }. */
Academy.addModules("ccdvf", {

/* ================================================= D1 Agents and Workflows */
d1: { sections: [
  { sub: "d1.1", title: "Workflow of agent?", body: `
<p><b>Workflow</b>: jij legt het pad vast in code; het model voert stappen uit. <b>Agent</b>: het model bepaalt zelf welke stappen en tools het gebruikt, in een loop met feedback uit de omgeving.</p>
<ul>
<li><b>Begin eenvoudig.</b> Eén goede aanroep met retrieval en voorbeelden is vaak genoeg. Voeg pas complexiteit toe als evaluaties laten zien dat het beter werkt.</li>
<li><b>Vaste, voorspelbare stappen</b> → workflow. <b>Open taken waarvan je de stappen niet vooraf kent</b> → agent.</li>
<li>Patronen: <b>prompt chaining</b> (vaste stappen na elkaar), <b>routing</b> (classificeren en doorsturen), <b>parallelization</b> (sectioning of voting), <b>orchestrator-workers</b> (subtaken bepaald door het model), <b>evaluator-optimizer</b> (genereren, beoordelen, verbeteren bij heldere criteria).</li>
<li><b>Subagents</b> geven contextisolatie: ze werken in een eigen context en sturen alleen een samenvatting terug.</li>
<li>Agents hebben <b>stopcondities</b> (maximum aantal stappen), echte feedback uit de omgeving (testresultaten, toolresultaten) en <b>menselijke checkpoints</b> nodig.</li>
</ul>` },
  { sub: "d1.2", title: "Agents bouwen", body: `
<p>De <b>agent loop</b>: stuur een request met tools → is <code>stop_reason</code> <code>tool_use</code>, voer de tools uit en stuur de <code>tool_result</code>s terug → herhaal. Bij <code>pause_turn</code> (server-tool-loop gepauzeerd) stuur je de assistant-inhoud terug om door te gaan. Stop bij <code>end_turn</code> of bij je eigen maximum aantal iteraties.</p>
<ul>
<li><b>Claude Agent SDK</b>: de harness van Claude Code als library in je eigen app (tools, hooks, subagents, MCP, permissies, sessies, skills). Jij host het. Authenticatie met API-sleutels, niet met een claude.ai-login.</li>
<li><b>Managed Agents</b>: Anthropic host de harness en sandbox voor je.</li>
<li><b>Instructies zijn verzoeken, hooks zijn regels.</b> Wat altijd moet gebeuren (formatteren na elke bewerking) → <code>PostToolUse</code>-hook. Wat nooit mag → <code>PreToolUse</code>-hook of een deny-permissie.</li>
<li><b>Tools zijn ook prompts</b>: investeer in naam, beschrijving en schema; daarop kiest het model.</li>
</ul>` },
  { sub: "d1.3", title: "Patronen en frameworks", body: `
<ul>
<li><b>Sectioning</b>: onafhankelijke delen tegelijk laten verwerken en daarna samenvoegen. <b>Voting</b>: dezelfde taak meerdere keren voor meer zekerheid.</li>
<li><b>Contextgroei</b> beheers je door te isoleren (subagents) en op te ruimen (tool result clearing, compaction).</li>
<li><b>Memory</b>: kennis buiten de context bewaren (bijv. bestanden via de memory tool) en gericht teruglezen.</li>
<li>Protocolregel: elk <code>tool_use</code>-block krijgt in het volgende user-bericht een <code>tool_result</code> met hetzelfde id, en die results staan vóór eventuele tekst.</li>
<li><b>Frameworks</b> versnellen de start, maar verbergen prompts en responses. Begrijp wat eronder gebeurt en kies op basis van je eisen en een kleine evaluatie.</li>
<li>Autonome acties test je eerst in een <b>sandbox</b>.</li>
</ul>` }
]},

/* ================================================= D2 Applications and Integration */
d2: { sections: [
  { sub: "d2.1", title: "Eisen vertalen", body: `
<p><b>Functionele eisen</b> beschrijven wat de toepassing doet (taken, kwaliteit, bronvermelding). <b>Infra-eisen</b> beschrijven hoe en waar het draait (latency, volume, opslag, locatie, kosten).</p>
<ul>
<li><b>Geen real-time nodig en veel volume</b> → Message Batches API.</li>
<li>"Snel" maak je meetbaar: een latency-eis, en streaming voor ervaren snelheid.</li>
<li><b>Gevoelige data</b>: bepaal eerst eisen voor opslag, retentie en datalocatie.</li>
<li><b>Bron moet aantoonbaar zijn</b> → citations of letterlijke citaten uit de documenten.</li>
<li><b>Haalbaarheid</b> toets je met een kleine set representatieve voorbeelden met verwachte uitkomsten en een prototype.</li>
</ul>` },
  { sub: "d2.2", title: "Levenscyclus", body: `
<ul>
<li><b>Evaluatieset</b> = vaste voorbeelden met verwachte uitkomsten. Daarmee zie je regressies bij elke prompt- of modelwijziging.</li>
<li><b>Modelupgrade</b>: eerst je eigen evals draaien, dan geleidelijk uitrollen (klein deel van het verkeer, metrics vergelijken, opschalen).</li>
<li><b>Vastgezet model-ID</b>: de gewichten veranderen niet; de infrastructuur kan kleine verschillen geven. Volg deprecations en plan migraties op tijd.</li>
<li><b>Monitoren</b>: foutpercentages per type, latency, tokens, kosten én kwaliteit (steekproeven of automatische evaluaties).</li>
<li><b>Prompts</b> horen in versiebeheer: traceerbaar, reviewbaar en terug te draaien.</li>
</ul>` },
  { sub: "d2.3", title: "Werking van de Claude API", body: `
<p><b>Messages API</b>: stateless; je stuurt de hele gespreksgeschiedenis mee. Belangrijke <code>stop_reason</code>s:</p>
<ul>
<li><code>end_turn</code> klaar · <code>max_tokens</code> afgekapt · <code>stop_sequence</code> · <code>tool_use</code> voer tools uit · <code>pause_turn</code> server-tool-loop gepauzeerd, terugsturen · <code>refusal</code> geweigerd (gewoon HTTP 200) · <code>model_context_window_exceeded</code>.</li>
<li><b>Tool use</b>: client tools voer jij uit (je stuurt <code>tool_result</code> terug); server tools (zoals web search) voert Anthropic uit. In het user-bericht staan de tool_results eerst.</li>
<li><b>tool_choice</b>: <code>auto</code> (vrij), <code>any</code> (verplicht een tool), <code>tool</code> (verplicht deze tool), <code>none</code>. Let op: Opus 5.5, Sonnet 5.5, Fable 5.1 en Mythos 5.1 geven op <code>any</code>/<code>tool</code> een 400; gebruik daar <code>auto</code> met <code>strict</code> of structured outputs. Eén tool per beurt: <code>disable_parallel_tool_use</code>.</li>
<li><b>Streaming</b>: tool-input komt als <code>input_json_delta</code> (samenvoegen, dan parsen); stop_reason en cumulatieve usage staan in <code>message_delta</code>.</li>
<li><b>Batches</b>: 50% korting, verwerkt binnen 24 uur, resultaten in willekeurige volgorde (koppel via <code>custom_id</code>), 29 dagen beschikbaar, geen streaming.</li>
<li><b>Files API</b>: upload één keer, hergebruik via <code>file_id</code>.</li>
</ul>` },
  { sub: "d2.4", title: "Software-engineeringbasis", body: `
<ul>
<li><b>Lange antwoorden</b> → streaming (betere ervaring, minder HTTP-time-outs).</li>
<li><b>Veel aanvragen</b> → async met begrensde concurrency, binnen je rate limits.</li>
<li><b>Herhaalbare acties</b> (retries!) → idempotent maken, zodat een tweede poging geen dubbele boeking geeft.</li>
<li><b>Testen</b>: mock de API voor je eigen logica; gebruik evals voor modelkwaliteit.</li>
<li><b>Modeloutput</b>: defensief parsen (try/catch, schema-validatie, fallback).</li>
<li>Centraliseer API-aanroepen in een <b>servicelaag</b> (één plek voor retries, logging, modelkeuze).</li>
<li><b>WebSocket</b> past bij langdurige, tweerichtings realtime-verbindingen; voor losse aanvragen volstaat REST.</li>
<li>AI-gegenereerde code: branches, tests en review zoals bij elke wijziging.</li>
</ul>` },
  { sub: "d2.5", title: "Applicatieontwerp", body: `
<ul>
<li><b>System prompt</b> = vaste rol en regels. <b>User-bericht</b> = taak en data.</li>
<li><b>Stateless</b>: jouw app beheert de gespreksgeschiedenis.</li>
<li><b>Grote kennisbank</b> → retrieval (RAG): alleen relevante stukken in de context.</li>
<li><b>Onvertrouwde inhoud</b> (webpagina's, e-mails, documenten van derden) hoort nooit in de system prompt; zet het in een <code>tool_result</code> of duidelijk gemarkeerde data.</li>
<li><b>Uniforme structuur</b> → vast schema plus validatie. Handel elke stop_reason af.</li>
<li>Elke omgeving (claude.ai, Claude Code, API, cloudplatforms) voegt eigen instructies en context toe; controleer ook of functies er beschikbaar zijn.</li>
<li>Een Claude Code-<b>plugin</b> bundelt skills, subagents, hooks en MCP-servers om een setup te delen.</li>
</ul>` },
  { sub: "d2.6", title: "Configuratiebeheer", body: `
<ul>
<li><b>Productie</b>: pin een volledig model-ID (vaste snapshot), geen alias die kan verschuiven.</li>
<li><b>Claude Code settings</b>: <code>~/.claude/settings.json</code> (gebruiker), <code>.claude/settings.json</code> (project, gedeeld via git), <code>.claude/settings.local.json</code> (persoonlijk), plus managed settings van de organisatie.</li>
<li><b>Afdwingen</b> doe je met <code>permissions.deny</code>, bijv. <code>Read(**/.env)</code>. Deny gaat vóór ask en allow.</li>
<li><b>Gedeelde MCP-servers</b>: <code>.mcp.json</code> in het project; geheimen via <code>\${VAR}</code>.</li>
<li><b>CLAUDE.md</b> kan andere bestanden importeren met <code>@pad</code>.</li>
<li>Configuratie expliciet en geversioneerd; <b>secrets buiten de code</b>.</li>
</ul>` }
]},

/* ================================================= D3 Claude Code */
d3: { sections: [
  { sub: "d3.1", title: "Claude Code gebruiken en configureren", body: `
<ul>
<li><b>CLAUDE.md</b>: projectinstructies voor het team (in git). <b>CLAUDE.local.md</b>: persoonlijk per project. Bestanden van de root tot je werkmap worden allemaal geladen: <b>additief</b>, niet overschrijvend.</li>
<li><b>CLAUDE.md = altijd in context. Skill = op aanvraag</b> geladen als de taak erom vraagt. Skills met bijwerkingen (deployen) krijgen <code>disable-model-invocation: true</code>, zodat alleen jij ze start.</li>
<li><b>Subagents</b> werken in een eigen context en worden gekozen op hun <code>description</code>.</li>
<li><b>Permissies</b>: volgorde deny → ask → allow.</li>
<li><b>Headless</b>: <code>claude -p "…"</code> met <code>--output-format json</code> of <code>stream-json</code>. <code>--bare</code> slaat lokale configuratie over voor reproduceerbare, geïsoleerde runs in scripts en CI.</li>
</ul>` }
]},

/* ================================================= D4 Eval, Testing, Debugging */
d4: { sections: [
  { sub: "d4.1", title: "Debuggen en foutafhandeling", body: `
<ul>
<li><b>Retry met exponentiële backoff</b>: 429 (rate limit; respecteer <code>retry-after</code>), 500, 529 (overloaded), 504. De SDK's retryen standaard twee keer.</li>
<li><b>Niet retryen, maar repareren</b>: 400 (ongeldige request), 401/403 (sleutel of rechten), 404, 413, en een 429 door een bereikte spend cap.</li>
<li><b>Streaming</b>: een fout na de 200 komt als <code>error</code>-event in de stream.</li>
<li><code>stop_reason: max_tokens</code> = afgekapt; verhoog de limiet (of ga verder).</li>
<li><b>Debuggen</b>: bekijk wat het model werkelijk kreeg (prompt, context, toolresultaten) en wat het teruggaf. Een tool_use zonder direct volgend tool_result geeft een 400.</li>
<li><b>Loggen</b>: de <code>request-id</code> wel, de API-sleutel nooit.</li>
</ul>` }
]},

/* ================================================= D5 Model Selection and Optimization */
d5: { sections: [
  { sub: "d5.1", title: "LLM-basis", body: `
<ul>
<li><b>Tokens</b> zijn stukjes tekst: de eenheid voor contextlengte, limieten en kosten. Tel vooraf met het <code>count_tokens</code>-endpoint.</li>
<li><b>Contextvenster</b> = alles wat in één aanvraag meeweegt: systeemprompt, berichten, tool-definities én de output.</li>
<li><code>max_tokens</code> is een harde grens op de output.</li>
<li><b>Sampling maakt output niet-deterministisch.</b> Test op eigenschappen (bevat de juiste velden, klopt het schema) in plaats van exacte tekst, en valideer gestructureerde output.</li>
<li><b>Vloeiend is niet hetzelfde als juist</b>: controleer feiten tegen bronnen.</li>
</ul>` },
  { sub: "d5.2", title: "Thinking, effort, fast mode, streaming", body: `
<ul>
<li><b>Effort</b> (<code>output_config.effort</code>: low, medium, high, xhigh, max) stuurt hoeveel werk het model doet over alle output; het is een gedragssignaal, geen strikt budget. Opus 5.5 en Haiku 5.5 staan standaard op medium. Eenvoudig werk in volume → low.</li>
<li><b>Adaptive thinking</b> (<code>thinking: {type: "adaptive"}</code>): het model bepaalt zelf of en hoeveel het nadenkt; effort stuurt dat. <code>budget_tokens</code> is de oudere manier.</li>
<li>Thinking-blocks stuur je <b>ongewijzigd</b> terug, zeker bij tool use. Thinking-tokens zie je in <code>usage.output_tokens_details.thinking_tokens</code>.</li>
<li><b>Fast mode</b> (<code>speed: "fast"</code>): tot ~2,5× meer outputtokens per seconde (niet een snellere eerste token), tegen premiumprijs, niet in batch.</li>
<li>Een andere effort halverwege een gecachet gesprek maakt de cache ongeldig: houd hem constant.</li>
</ul>` },
  { sub: "d5.3", title: "Modelkeuze", body: `
<ul>
<li><b>Opus 5.5</b>: aanbevolen standaard. <b>Fable 5.1</b>: zwaarste redeneertaken. <b>Sonnet 5.5</b>: balans snelheid/intelligentie. <b>Haiku 5.5</b>: snel en goedkoop voor volume.</li>
<li>Kies op basis van <b>eigen evals</b> op kwaliteit, latency en kosten. Een duurder model alleen bij aantoonbare meerwaarde.</li>
<li>Kies model en effort <b>per rol</b>: bijv. Haiku als router of screener, Opus voor de planner.</li>
<li>Een nieuwe modelgeneratie kan zich anders gedragen (letterlijker instructies volgen, andere lengte): opnieuw testen.</li>
<li>Hoge outputsnelheid nodig en budget aanwezig → fast mode.</li>
</ul>` },
  { sub: "d5.4", title: "Kosten en prompt caching", body: `
<ul>
<li><b>Cacheprefix</b>: tools → system → messages. Zet het breakpoint (<code>cache_control</code>) op het laatste stabiele block; maximaal 4 breakpoints.</li>
<li>Iets wijzigen vroeg in de prefix (bijv. tool-definities) maakt alles daarna ongeldig.</li>
<li><b>TTL</b>: standaard 5 minuten; 1 uur als je later hergebruikt. Schrijven kost 1,25× (5 min) of 2× (1 uur); lezen ~0,1×.</li>
<li>Controleer in <code>usage</code>: <code>cache_creation_input_tokens</code> en <code>cache_read_input_tokens</code>. Cache-reads tellen bij de meeste modellen niet mee voor ITPM.</li>
<li><b>Kosten omlaag</b>: caching voor stabiele context, Batch API (50%) voor werk zonder haast, context opruimen of compacteren. Meet tokens op representatieve aanvragen.</li>
</ul>` }
]},

/* ================================================= D6 Prompt and Context Engineering */
d6: { sections: [
  { sub: "d6.1", title: "Contextbeheer", body: `
<ul>
<li><b>Context editing / tool result clearing</b>: oude toolresultaten weghalen, recente laten staan. Gericht weghalen.</li>
<li><b>Compaction</b>: oudere geschiedenis samenvatten zodat het gesprek door kan.</li>
<li><b>Isoleren</b>: zoekwerk met veel ruis in een subagent; alleen de samenvatting komt terug.</li>
<li><b>Drift</b>: in lange sessies raken doelen ondergesneeuwd. Ruim op en vat samen.</li>
<li>Geef tools alleen terug wat nodig is (pruning).</li>
<li>Opruimen breekt de cache: ruim in grotere stappen op. Wat je later nog nodig hebt, bewaar je eerst (memory), dan pas opruimen.</li>
</ul>` },
  { sub: "d6.2", title: "Prompt engineering", body: `
<ul>
<li><b>System</b> = rol en regels; <b>user</b> = taak en data.</li>
<li>Instructies: <b>concreet, positief</b> (zeg wat wél moet) en <b>met reden</b>.</li>
<li><b>Structuur</b> met XML-tags of kopjes scheidt instructies, context, voorbeelden en data.</li>
<li><b>Few-shot</b>: een paar gevarieerde voorbeelden voor consistent formaat.</li>
<li>Complexe analyse: criteria en formaat meegeven, en ruimte om eerst te redeneren.</li>
<li><b>Saneer invoer</b> zodat gebruikerstekst je promptstructuur niet breekt (afsluitende tags, instructie-achtige tekst).</li>
<li>Verbeteren: testset, meten, één wijziging tegelijk. Slecht gevolgd? Maak concreet en haal tegenstrijdigheden weg.</li>
</ul>` },
  { sub: "d6.3", title: "Output verwerken", body: `
<ul>
<li><b>Structured outputs</b>: <code>output_config.format</code> met <code>json_schema</code> dwingt het eindantwoord in een schema. <code>strict: true</code> op een tool doet dat voor de tool-input.</li>
<li>Check eerst <code>stop_reason</code>: bij <code>refusal</code> of <code>max_tokens</code> voldoet de output mogelijk niet aan het schema.</li>
<li>Niet ondersteund in het schema: o.a. <code>minimum</code>/<code>maximum</code> en <code>minLength</code>/<code>maxLength</code> (een ruw schema geeft een 400). SDK-helpers zetten ze in de beschrijving en valideren achteraf; anders valideer je zelf.</li>
<li><b>Defensief parsen</b>: try/catch, validatie tegen je volledige schema, fallback.</li>
<li>Accepteer geen output op zelfvertrouwen: verifieer cijfers tegen bron of data.</li>
</ul>` }
]},

/* ================================================= D7 Security and Safety */
d7: { sections: [
  { sub: "d7.1", title: "Prompt injection en datalekken", body: `
<ul>
<li><b>Indirecte prompt injection</b>: instructies verstopt in inhoud van derden (webpagina, e-mail, document) die je agent leest.</li>
<li>Onvertrouwde inhoud: in een <code>tool_result</code>, gelabeld met bron, eventueel JSON-geëncodeerd; leg in de systeemprompt vast dat data geen instructie is.</li>
<li>Screen input of tooloutput met een licht model (Haiku).</li>
<li><b>Least privilege</b>: beperk wat de agent kan, zodat een geslaagde injectie weinig schade doet.</li>
<li><b>Autorisatie in de backend</b>, nooit alleen in de prompt.</li>
<li>Log geen onnodige persoonsgegevens; maskeer gevoelige data.</li>
</ul>` },
  { sub: "d7.2", title: "Guardrails en veilig uitrollen", body: `
<ul>
<li><b>Defense in depth</b>: meerdere onafhankelijke lagen (screening, grenzen in de systeemprompt, permissies, outputvalidatie, monitoring).</li>
<li><b>Onomkeerbare externe acties</b> (betalen, mailen, verwijderen): menselijke goedkeuring of een harde beperking.</li>
<li>Geeft je screeningsmodel een <code>refusal</code>, behandel de inhoud dan als schadelijk.</li>
<li>Vóór livegang <b>red-teamen</b> (ook met injectiepogingen), na livegang <b>monitoren</b>.</li>
</ul>` },
  { sub: "d7.3", title: "Hooks als harde controle", body: `
<ul>
<li><b>Exit 2</b> = blokkeren (stderr gaat naar Claude) en wint van JSON-output. Ook mogelijk: <code>permissionDecision: "deny"</code>.</li>
<li><b>Exit 1</b> = niet-blokkerende fout; de actie gaat door, tenzij de hook <code>onFailure: "block"</code> heeft (command- en http-hooks, v2.1.295+).</li>
<li><b>Exit 0 zonder output</b> = geen beslissing, geen goedkeuring.</li>
<li>Vooraf blokkeren kan alleen in <code>PreToolUse</code>; bij <code>PostToolUse</code> is de tool al uitgevoerd.</li>
<li>Matcher voor MCP-tools: <code>mcp__&lt;server&gt;__&lt;tool&gt;</code>.</li>
<li>Hooks draaien als shellcommando's in jouw omgeving: lees ze voordat je een project vertrouwt. Gebruikers kunnen managed hooks niet uitzetten met <code>disableAllHooks</code>.</li>
</ul>` },
  { sub: "d7.4", title: "Identiteit, secrets en sleutels", body: `
<ul>
<li><b>API-sleutels nooit in de client</b> (browser of app); laat de backend de API aanroepen.</li>
<li>Secrets in een <b>secret manager</b> of beveiligde omgevingsvariabelen; nooit in code, repository of prompts.</li>
<li>Per omgeving een eigen sleutel; regelmatig roteren; ongebruikte intrekken. Gelekt? Direct intrekken en vervangen.</li>
<li><b>Files API</b>: bestanden zijn workspace-breed zichtbaar. Accepteer nooit een <code>file_id</code> van een eindgebruiker; bewaar zelf welke file bij welke gebruiker hoort.</li>
<li>Toegang tot externe systemen: server-side een token per gebruiker met minimale scopes; het model ziet het token niet.</li>
</ul>` }
]},

/* ================================================= D8 Tools and MCPs */
d8: { sections: [
  { sub: "d8.1", title: "Tools implementeren", body: `
<ul>
<li>Een tool-definitie: <code>name</code>, <code>description</code> (wat, wanneer, betekenis van de invoer) en <code>input_schema</code> (types, required).</li>
<li><code>strict: true</code> garandeert dat de tool-input aan het schema voldoet.</li>
<li><b>Fouten</b>: <code>tool_result</code> met <code>is_error: true</code> en een instructieve melding, zodat het model kan bijsturen.</li>
<li>Ontwerp tegen fouten (<b>poka-yoke</b>): bijv. absolute paden eisen, enums in plaats van vrije tekst. Verwarring tussen tools los je op met scherpere beschrijvingen en grenzen.</li>
<li>Destructieve tools: <b>approval-patroon</b>.</li>
<li>Tool-definities tellen als <b>input-tokens</b>, en tool use voegt een kleine systeemprompt toe.</li>
<li><b>Anthropic-schema client tools</b> (bash, text editor): Anthropic levert het schema, jouw app voert uit.</li>
</ul>` },
  { sub: "d8.2", title: "MCP-servers bouwen", body: `
<ul>
<li><b>Rollen</b>: de <b>host</b> is de AI-app; die maakt per server een <b>client</b>; de <b>server</b> levert context en mogelijkheden. Berichten via <b>JSON-RPC 2.0</b>.</li>
<li><b>Primitives</b>: <b>tools</b> (acties), <b>resources</b> (contextdata), <b>prompts</b> (sjablonen).</li>
<li><b>Transport</b>: lokaal → <b>stdio</b>; remote → <b>Streamable HTTP</b>, met OAuth voor autorisatie.</li>
<li>Goede server: duidelijke namen, beschrijvingen en schema's; invoer valideren; heldere foutmeldingen; output gericht houden (context en kosten). Claude Code waarschuwt bij grote MCP-output.</li>
<li>In <code>.mcp.json</code> geheimen via <code>\${VAR}</code> of <code>\${VAR:-default}</code>.</li>
<li>De MCP-specificatie verandert (versie 2026-07-28); het examen toetst vooral de stabiele concepten hierboven.</li>
</ul>` },
  { sub: "d8.3", title: "Kiezen: built-in, custom, skill, MCP", body: `
<ul>
<li><b>Externe dienst koppelen</b> → MCP-server. <b>Herbruikbare werkwijze of kennis, op aanvraag</b> → skill. MCP is de verbinding; een skill vertelt hoe je hem goed gebruikt.</li>
<li><b>Built-in waar het kan, custom waar het moet</b>: eigen tool alleen voor bedrijfsspecifieke acties of data.</li>
<li><b>Altijd na elke bewerking</b> → hook. <b>Contextisolatie</b> → subagent. <b>Altijd geldende conventies</b> → CLAUDE.md.</li>
<li><b>Te veel tools</b> verwart het model en kost tokens: beperk de set of laat tools pas laden als ze nodig zijn.</li>
</ul>` }
]}

});
