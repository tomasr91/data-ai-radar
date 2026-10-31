/* Academy content registry.
   Elke certificering is een los object; inhoudsbestanden registreren modules en vragen per certificering.
   Een nieuwe certificering toevoegen = één meta-blok hieronder + eigen modules/vragen-bestanden. */
(function () {
  const certs = {};
  const order = [];
  window.Academy = {
    certs, order,
    defineCert(def) {
      certs[def.id] = Object.assign({ modules: {}, questions: [] }, def);
      order.push(def.id);
    },
    addModules(certId, modules) { Object.assign(certs[certId].modules, modules); },
    addQuestions(certId, qs) { certs[certId].questions.push(...qs); }
  };

  const GUIDE_BASE = "https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2F6nizmqk8tpzpfjvt6qmmav7rh%2Fpublic%2F";

  /* ---------- Actieve certificering ---------- */
  Academy.defineCert({
    id: "ccaof",
    status: "active",
    code: "CCAO-F",
    name: "Claude Certified Associate – Foundations",
    short: "Associate – Foundations",
    audience: "Professionals die Claude als productiviteitstool gebruiken en Claude Projects bouwen (operations, marketing, projectmanagement, onderwijs, communicatie, HR, consultancy). Geen API- of ontwikkelaarservaring vereist.",
    exam: {
      items: 60, minutes: 120, scaleMin: 100, scaleMax: 1000, cut: 720, fee: "$99 USD",
      format: "Multiple-choice en multiple-response; elke vraag vermeldt hoeveel antwoorden je moet kiezen",
      delivery: "Geproctord via Pearson VUE (online of testcentrum)",
      validity: "12 maanden",
      report: "Geslaagd/gezakt met schaalscore (100–1.000), plus percentage correct per domein. De domeinpercentages bepalen de uitslag niet."
    },
    sources: [
      { label: "Officiële examengids (PDF, v1.0, juli 2026)", url: GUIDE_BASE + "1783542847%2FClaude+Certified+Associate+%E2%80%93+Foundations+Exam+Guide.pdf" },
      { label: "Certificeringspagina, Anthropic Partner Academy", url: "https://anthropic-partners.skilljar.com/claude-certified-associate-foundations-certification" },
      { label: "Overzicht alle certificeringen", url: "https://anthropic-partners.skilljar.com/page/partner-certifications" },
      { label: "Claude Help Center (productfunctionaliteit)", url: "https://support.claude.com" },
      { label: "Claude-modellen, platformdocumentatie", url: "https://platform.claude.com/docs/en/models/overview" }
    ],
    verifiedOn: "21 oktober 2026",
    guideVersion: "1.0 (juli 2026)",
    domains: [
      { id: "d1", n: 1, name: "Prompting and Task Execution", nl: "Prompten en taakuitvoering", weight: 14,
        subs: [
          { id: "d1.1", en: "Create effective prompts for business and technical tasks", nl: "Effectieve prompts maken" },
          { id: "d1.2", en: "Apply task decomposition techniques to structure complex requests", nl: "Taken opknippen (task decomposition)" },
          { id: "d1.3", en: "Iterate prompts to improve output quality", nl: "Prompts itereren" },
          { id: "d1.4", en: "Adapt prompting strategies based on task type", nl: "Promptstrategie per taaktype" }
        ] },
      { id: "d2", n: 2, name: "Output Evaluation and Validation", nl: "Output beoordelen en valideren", weight: 21,
        subs: [
          { id: "d2.1", en: "Evaluate Claude-generated outputs for accuracy and completeness", nl: "Juistheid en volledigheid beoordelen" },
          { id: "d2.2", en: "Identify hallucinations, inconsistencies, and biases in responses", nl: "Hallucinaties, inconsistenties en bias herkennen" },
          { id: "d2.3", en: "Apply fact-checking and validation techniques", nl: "Factchecken en valideren" },
          { id: "d2.4", en: "Determine when human review or additional verification is required", nl: "Wanneer menselijke review nodig is" },
          { id: "d2.5", en: "Edit, adapt, refine, and compare outputs for the intended audience", nl: "Output aanpassen voor de doelgroep" },
          { id: "d2.6", en: "Organize and curate information and select appropriate output formats", nl: "Informatie ordenen en outputformaat kiezen" }
        ] },
      { id: "d3", n: 3, name: "Product and Model Selection", nl: "Product- en modelkeuze", weight: 12,
        subs: [
          { id: "d3.1", en: "Select appropriate Claude product features (Projects, research mode, chat, artifacts)", nl: "Juiste productfunctie kiezen" },
          { id: "d3.2", en: "Differentiate between Claude model types (Haiku, Sonnet, Opus)", nl: "Modeltypen onderscheiden" },
          { id: "d3.3", en: "Align model selection with task requirements (cost, speed, quality)", nl: "Model afstemmen op taakeisen" },
          { id: "d3.4", en: "Understand and manage context limitations and memory considerations", nl: "Contextlimieten en geheugen beheren" }
        ] },
      { id: "d4", n: 4, name: "Workflow Integration and Solution Design", nl: "Workflowintegratie en oplossingsontwerp", weight: 16,
        subs: [
          { id: "d4.1", en: "Apply Claude to analyze requirements and use cases", nl: "Eisen en use cases analyseren" },
          { id: "d4.2", en: "Leverage Claude for research, planning, and process optimization", nl: "Onderzoek, planning en procesoptimalisatie" },
          { id: "d4.3", en: "Use Claude to support solution design, development, and iteration", nl: "Oplossingsontwerp en iteratie" },
          { id: "d4.4", en: "Integrate Claude into existing workflows to augment or redesign them", nl: "Integreren in bestaande workflows" },
          { id: "d4.5", en: "Communicate Claude's value and limitations to stakeholders", nl: "Waarde en grenzen communiceren" }
        ] },
      { id: "d5", n: 5, name: "Configuration and Knowledge Management", nl: "Configuratie en kennisbeheer", weight: 12,
        subs: [
          { id: "d5.1", en: "Configure Claude Projects with instructions and knowledge sources", nl: "Projects configureren" },
          { id: "d5.2", en: "Manage uploaded knowledge and connectors (e.g., Google Drive, Gmail)", nl: "Kennis en connectors beheren" },
          { id: "d5.3", en: "Create effective system-level instructions", nl: "Effectieve instructies schrijven" },
          { id: "d5.4", en: "Inform, maintain, and update Claude configurations, knowledge sources, and instructions", nl: "Configuraties onderhouden" }
        ] },
      { id: "d6", n: 6, name: "Governance, Risk, and Responsible Use", nl: "Governance, risico en verantwoord gebruik", weight: 15,
        subs: [
          { id: "d6.1", en: "Identify appropriate and inappropriate use cases", nl: "Geschikte en ongeschikte use cases" },
          { id: "d6.2", en: "Apply data sensitivity, regulatory, and privacy considerations", nl: "Gevoelige data, regelgeving en privacy" },
          { id: "d6.3", en: "Follow organizational AI policies and governance standards", nl: "AI-beleid en governance volgen" },
          { id: "d6.4", en: "Understand the ethical implications of AI usage", nl: "Ethische implicaties" }
        ] },
      { id: "d7", n: 7, name: "Troubleshooting and Optimization", nl: "Probleemoplossing en optimalisatie", weight: 10,
        subs: [
          { id: "d7.1", en: "Identify, diagnose, and resolve issues with underperforming prompts or poor outputs", nl: "Slechte output diagnosticeren" },
          { id: "d7.2", en: "Adjust approach based on feedback and results", nl: "Aanpak bijstellen op feedback" },
          { id: "d7.3", en: "Optimize workflows for efficiency and effectiveness", nl: "Workflows optimaliseren" }
        ] }
    ]
  });

  /* ---------- Overige certificeringen: onderwerpen uit de officiële examengidsen (v1.0, juli 2026), vragenbank volgt ---------- */
  const sub = (id, en) => ({ id, en, nl: en });
  const sb = (id, en, nl) => ({ id, en, nl });
  Academy.defineCert({
    id: "ccdvf", status: "active", code: "CCDV-F", name: "Claude Certified Developer – Foundations", short: "Developer – Foundations",
    audience: "Engineers die bouwen met de Claude API, Claude Code en het Model Context Protocol.",
    exam: { items: 53, minutes: 120, cut: 720, scaleMin: 100, scaleMax: 1000, fee: "$125 USD" }, guideVersion: "1.0 (juli 2026)",
    verifiedOn: "21 oktober 2026",
    sources: [
      { label: "Officiële examengids (PDF)", url: GUIDE_BASE + "1783542875%2FClaude+Certified+Developer+%E2%80%93+Foundations+Exam+Guide.pdf" },
      { label: "Claude Platform-documentatie (API)", url: "https://platform.claude.com/docs" },
      { label: "Claude Code-documentatie", url: "https://code.claude.com/docs" },
      { label: "Model Context Protocol", url: "https://modelcontextprotocol.io" },
      { label: "Building effective agents (Anthropic)", url: "https://www.anthropic.com/engineering/building-effective-agents" }
    ],
    domains: [
      { id: "d1", n: 1, name: "Agents and Workflows", nl: "Agents en workflows", weight: 14.7, subs: [
        sb("d1.1", "Agent Architecture", "Agent-architectuur: workflow of agent, hiërarchieën"),
        sb("d1.2", "Agent Construction with Claude", "Agents bouwen: Agent SDK, loops, hooks, hosting"),
        sb("d1.3", "Agent Patterns and Frameworks", "Agentpatronen en frameworks")] },
      { id: "d2", n: 2, name: "Applications and Integration", nl: "Applicaties en integratie", weight: 33.1, subs: [
        sb("d2.1", "Understanding Requirements", "Eisen vertalen naar functionele en infra-eisen"),
        sb("d2.2", "Systems Life Cycle", "Levenscyclus: bouwen, uitrollen, beheren"),
        sb("d2.3", "Claude API Mechanics", "Werking van de Claude API"),
        sb("d2.4", "Software Engineering Foundations", "Software-engineeringbasis"),
        sb("d2.5", "Claude Application Design", "Ontwerp van Claude-applicaties"),
        sb("d2.6", "Configuration Management", "Configuratiebeheer: CLAUDE.md, settings, versies")] },
      { id: "d3", n: 3, name: "Claude Code", nl: "Claude Code", weight: 3.1, subs: [
        sb("d3.1", "Claude Code Operation", "Claude Code gebruiken en configureren")] },
      { id: "d4", n: 4, name: "Eval, Testing, and Debugging", nl: "Evaluatie, testen en debuggen", weight: 2.6, subs: [
        sb("d4.1", "Debugging and Error Handling", "Debuggen en foutafhandeling")] },
      { id: "d5", n: 5, name: "Model Selection and Optimization", nl: "Modelkeuze en optimalisatie", weight: 16.8, subs: [
        sb("d5.1", "LLM Fundamentals", "LLM-basis: tokens, context, sampling"),
        sb("d5.2", "Technical Fundamentals", "Technische basis: thinking, effort, fast mode, streaming"),
        sb("d5.3", "Model Selection and Tradeoffs", "Modelkeuze en afwegingen"),
        sb("d5.4", "Cost and Token Management", "Kosten- en tokenbeheer, caching")] },
      { id: "d6", n: 6, name: "Prompt and Context Engineering", nl: "Prompt- en contextengineering", weight: 11.0, subs: [
        sb("d6.1", "Context Engineering", "Contextbeheer: groei, drift, compaction"),
        sb("d6.2", "Prompt Engineering", "Prompt engineering"),
        sb("d6.3", "Output Handling", "Output verwerken en valideren")] },
      { id: "d7", n: 7, name: "Security and Safety", nl: "Beveiliging en veiligheid", weight: 8.1, subs: [
        sb("d7.1", "AI Application Security", "Beveiliging: prompt injection, datalekken"),
        sb("d7.2", "Guardrails and Safe Deployment", "Guardrails en veilig uitrollen"),
        sb("d7.3", "Claude Hooks", "Hooks als harde controle"),
        sb("d7.4", "Identity, Secrets, and Key Management", "Identiteit, secrets en sleutelbeheer")] },
      { id: "d8", n: 8, name: "Tools and MCPs", nl: "Tools en MCP", weight: 10.6, subs: [
        sb("d8.1", "Tool Implementation", "Tools implementeren"),
        sb("d8.2", "MCP Server Development", "MCP-servers bouwen"),
        sb("d8.3", "Agentic Customization", "Kiezen: built-in tools, custom tools, Skills, MCP")] }
    ]
  });
  Academy.defineCert({
    id: "ccarf", status: "planned", code: "CCAR-F", name: "Claude Certified Architect – Foundations", short: "Architect – Foundations",
    audience: "Partners die Claude-oplossingen end-to-end ontwerpen: agent-architecturen, tools en MCP, Claude Code, evaluatie en betrouwbaarheid.",
    exam: { items: 60, minutes: 120, cut: 720, scaleMin: 100, scaleMax: 1000, fee: "$125 USD" }, guideVersion: "1.0 (juli 2026)",
    sources: [{ label: "Officiële examengids (PDF)", url: GUIDE_BASE + "1783542750%2FClaude+Certified+Architect+%E2%80%93+Foundations+Exam+Guide.pdf" }],
    domains: [
      { id: "d1", n: 1, name: "Agentic Architecture & Orchestration", weight: 27, subs: [sub("d1.1","Design and implement agentic loops for autonomous task execution"), sub("d1.2","Orchestrate multi-agent systems with coordinator-subagent patterns"), sub("d1.3","Configure subagent invocation, context passing, and spawning"), sub("d1.4","Implement multi-step workflows with enforcement and handoff patterns"), sub("d1.5","Apply Agent SDK hooks for tool call interception and data normalization"), sub("d1.6","Design task decomposition strategies for complex workflows"), sub("d1.7","Manage session state, resumption, and forking")] },
      { id: "d2", n: 2, name: "Tool Design & MCP Integration", weight: 18, subs: [sub("d2.1","Design effective tool interfaces with clear descriptions and boundaries"), sub("d2.2","Implement structured error responses for MCP tools"), sub("d2.3","Distribute tools appropriately across agents and configure tool choice"), sub("d2.4","Integrate MCP servers into Claude Code and agent workflows"), sub("d2.5","Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively")] },
      { id: "d3", n: 3, name: "Claude Code Configuration & Workflows", weight: 20, subs: [sub("d3.1","Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization"), sub("d3.2","Create and configure custom slash commands and skills"), sub("d3.3","Apply path-specific rules for conditional convention loading"), sub("d3.4","Determine when to use plan mode vs direct execution"), sub("d3.5","Apply iterative refinement techniques for progressive improvement"), sub("d3.6","Integrate Claude Code into CI/CD pipelines")] },
      { id: "d4", n: 4, name: "Prompt Engineering & Structured Output", weight: 20, subs: [sub("d4.1","Design prompts with explicit criteria to improve precision and reduce false positives"), sub("d4.2","Apply few-shot prompting to improve output consistency and quality"), sub("d4.3","Enforce structured output using tool use and JSON schemas"), sub("d4.4","Implement validation, retry, and feedback loops for extraction quality"), sub("d4.5","Design efficient batch processing strategies"), sub("d4.6","Design multi-instance and multi-pass review architectures")] },
      { id: "d5", n: 5, name: "Context Management & Reliability", weight: 15, subs: [sub("d5.1","Manage conversation context to preserve critical information across long interactions"), sub("d5.2","Design effective escalation and ambiguity resolution patterns"), sub("d5.3","Implement error propagation strategies across multi-agent systems"), sub("d5.4","Manage context effectively in large codebase exploration"), sub("d5.5","Design human review workflows and confidence calibration"), sub("d5.6","Preserve information provenance and handle uncertainty in multi-source synthesis")] }
    ]
  });
  Academy.defineCert({
    id: "ccarp", status: "planned", code: "CCAR-P", name: "Claude Certified Architect – Professional", short: "Architect – Professional",
    audience: "Vervolg op Architect – Foundations: oplossingsontwerp, integratie, evaluatie, governance en stakeholdermanagement op professioneel niveau.",
    exam: { items: 63, minutes: 120, cut: 720, scaleMin: 100, scaleMax: 1000, fee: "$175 USD" }, guideVersion: "1.0 (juli 2026)",
    sources: [{ label: "Officiële examengids (PDF)", url: GUIDE_BASE + "1783542810%2FClaude+Certified+Architect+%E2%80%93+Professional+Exam+Guide.pdf" }],
    domains: [
      { id: "d1", n: 1, name: "Solution Design & Architecture", weight: 17, subs: [sub("d1.1","Translate business problems into Claude-based AI solutions"), sub("d1.2","Design end-to-end architectures (input → processing → output → feedback loops)"), sub("d1.3","Select appropriate architectural patterns (workflow, agentic, augmented LLM)"), sub("d1.4","Design multi-agent systems and orchestration strategies"), sub("d1.5","Apply decomposition techniques for complex problem solving"), sub("d1.6","Align solutions to business value pillars")] },
      { id: "d2", n: 2, name: "Claude Models, Prompting & Context Engineering", weight: 13, subs: [sub("d2.1","Select appropriate Claude models based on trade-offs"), sub("d2.2","Design system prompts, templates, and guardrails"), sub("d2.3","Apply prompt engineering techniques (zero-shot, few-shot, chain-of-thought)"), sub("d2.4","Optimize context windows and manage token usage"), sub("d2.5","Implement prompt reuse strategies (caching, modular prompts, Skills)")] },
      { id: "d3", n: 3, name: "Integration", weight: 19, subs: [sub("d3.1","Evaluate tool/agent configuration for capability bloat"), sub("d3.2","Analyze authentication and authorization requirements to identify security gaps"), sub("d3.3","Evaluate accuracy-latency trade-offs and justify configuration decisions"), sub("d3.4","Analyze observability challenges and select monitoring strategies at scale"), sub("d3.5","Design a RAG pipeline with appropriate chunking and indexing strategies"), sub("d3.6","Apply retrieval strategies matched to data shape and query pattern"), sub("d3.7","Evaluate connection protocols and select the integration mechanism (MCP, API/CLI, agent-to-agent)"), sub("d3.8","Evaluate progressive discovery vs. monolithic context strategy")] },
      { id: "d4", n: 4, name: "Evaluation, Testing & Optimization", weight: 16, subs: [sub("d4.1","Define evaluation metrics (accuracy, latency, cost, safety, security)"), sub("d4.2","Design evaluation datasets and test frameworks using mixed methodologies"), sub("d4.3","Conduct A/B testing and iterative improvements"), sub("d4.4","Diagnose system issues (prompt failure, hallucinations, model mismatch)"), sub("d4.5","Optimize token usage, latency, and cost-performance trade-offs"), sub("d4.6","Monitor system performance using logging and observability tools")] },
      { id: "d5", n: 5, name: "Governance, Safety & Risk Management", weight: 14, subs: [sub("d5.1","Implement guardrails and safety controls"), sub("d5.2","Identify risks, limitations, and failure modes of LLM systems"), sub("d5.3","Apply human-in-the-loop validation strategies"), sub("d5.4","Ensure compliance with regulations (e.g., GDPR, HIPAA, FedRAMP)"), sub("d5.5","Address ethical AI considerations (bias, fairness, transparency)")] },
      { id: "d6", n: 6, name: "Stakeholder Communication & Lifecycle Management", weight: 14, subs: [sub("d6.1","Conduct structured discovery and requirement gathering"), sub("d6.2","Communicate architectural decisions and trade-offs"), sub("d6.3","Manage stakeholder feedback loops and expectation alignment (including SLAs)"), sub("d6.4","Document architectures and provide implementation guidance"), sub("d6.5","Support lifecycle phases (discovery, design, handoff, monitoring, iteration)")] },
      { id: "d7", n: 7, name: "Developer Productivity & Operational Enablement", weight: 7, subs: [sub("d7.1","Configure Claude tools and environments for teams (e.g., Claude Code)"), sub("d7.2","Improve developer workflows using AI-assisted tooling"), sub("d7.3","Support debugging and operational issue resolution")] }
    ]
  });
})();
