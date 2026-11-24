/* dbt Analytics Engineering: uitleg per subonderwerp (één scherm per leerdoel).
   Gebaseerd op de officiële studiegids (dbt Core 1.11) en docs.getdbt.com, gecontroleerd op 24 november 2026.
   "In v2" = wat er anders is in dbt v2 (bron: docs.getdbt.com, Upgrading to v2). Het examen gaat over 1.11. */
Academy.addModules("dbtae", {

/* ================================================= D1 Modellen bouwen */
d1: { sections: [
  { sub: "d1.1", title: "Bronnen vastleggen", body: `
<p>Ruwe tabellen leg je vast als <b>source</b> in YAML (<code>sources:</code> → <code>tables:</code>) en je verwijst ernaar met <code>{{ source('bron', 'tabel') }}</code>. Nooit een tabelnaam hard in de SQL zetten.</p>
<ul>
<li>Met <code>source()</code> ziet dbt de afhankelijkheid: de bron staat in de DAG en in de lineage, en je kunt erop selecteren (<code>dbt build -s source:hix+</code>).</li>
<li>Op sources kun je tests zetten (bijv. <code>not_null</code>, <code>unique</code>) en <b>freshness</b> controleren.</li>
<li><code>dbt ls -s source:hix+</code> laat zien welke modellen van een bron afhangen; zo controleer je de afhankelijkheden.</li>
<li>Bronnaam en schema kunnen verschillen: <code>name</code> is hoe je ernaar verwijst, <code>schema</code> (en <code>database</code>) waar de tabel echt staat; met <code>identifier</code> wijk je af van de tabelnaam.</li>
</ul>
<p class="small"><b>In v2:</b> je mag projectmacro's gebruiken in <code>sources.yml</code> (bijv. <code>database: "{{ get_environment() }}"</code>); in v1 werkt dat niet.</p>` },
  { sub: "d1.2", title: "Materializations", body: `
<ul>
<li><b>view</b> (standaard): alleen een view; altijd actueel, maar de query draait bij elke vraag.</li>
<li><b>table</b>: de hele tabel wordt bij elke run opnieuw gebouwd. Snel om te lezen, trager om te bouwen.</li>
<li><b>incremental</b>: alleen nieuwe of gewijzigde rijen toevoegen of bijwerken. Voor grote tabellen.</li>
<li><b>ephemeral</b>: komt niet in het datawarehouse; dbt plakt de SQL als CTE in de modellen die hem gebruiken.</li>
<li><b>materialized_view</b>: het platform houdt de tabel zelf bij (waar het platform dat ondersteunt).</li>
</ul>
<p>Vuistregel: begin met views, kies <b>table</b> als lezen te traag wordt, en <b>incremental</b> als bouwen te traag wordt.</p>` },
  { sub: "d1.3", title: "Modulair en DRY", body: `
<ul>
<li><b>Lagen</b>: staging (één model per brontabel: hernoemen, types, geen joins), intermediate (logica opknippen), marts (feiten en dimensies voor gebruikers).</li>
<li>Elk model verwijst met <code>ref()</code> naar het vorige; zo bouwt dbt de DAG en de juiste volgorde.</li>
<li><b>DRY</b> (don't repeat yourself): herhaalde SQL wordt een <b>macro</b> of een eigen model; herhaalde config zet je in <code>dbt_project.yml</code>.</li>
<li>Een bron gebruik je alleen in staging; daarna alleen nog <code>ref()</code> naar staging.</li>
</ul>` },
  { sub: "d1.4", title: "Commando's", body: `
<ul>
<li><code>dbt run</code>: bouwt modellen. <code>dbt test</code>: draait tests. <code>dbt seed</code>: laadt CSV-bestanden uit <code>seeds/</code>. <code>dbt snapshot</code>: draait snapshots.</li>
<li><code>dbt build</code>: alles in DAG-volgorde (modellen, tests, seeds, snapshots). Tests van een model draaien direct na dat model; faalt een test, dan worden de modellen erna overgeslagen.</li>
<li><code>dbt docs generate</code>: maakt de documentatie (<code>catalog.json</code>); <code>dbt docs serve</code> toont hem lokaal.</li>
<li><code>dbt show</code>: toont een voorbeeld van de uitkomst zonder iets te bouwen (<code>-s model</code> of <code>--inline "select ..."</code>; standaard 5 rijen, <code>--limit</code> voor meer).</li>
</ul>
<p class="small"><b>In v2:</b> <code>dbt build</code> draait eerst alle unit tests en daarna de rest van de DAG. Nieuw zijn ook <code>dbt check</code>, <code>dbt lint</code> en <code>dbt freshness</code>.</p>` },
  { sub: "d1.5", title: "Een schone DAG", body: `
<ul>
<li>De DAG volgt uit <code>ref()</code> en <code>source()</code>. Een kring (A → B → A) is niet toegestaan.</li>
<li>Vermijd dat marts direct sources lezen of dat een laag "terugspringt" (een mart die een staging-model opnieuw joint terwijl een intermediate model dat al doet).</li>
<li><b>Selectie</b>: <code>-s model+</code> (model en alles erna), <code>+model</code> (alles ervoor), <code>2+model</code> (twee stappen terug), <code>@model</code> (model, alles erna én alles wat die nodig hebben), <code>tag:</code>, <code>path:</code>, <code>--exclude</code>.</li>
</ul>
<p class="small"><b>In v2:</b> <code>--models</code> en <code>-m</code> geven een fout; gebruik <code>--select</code> / <code>-s</code>.</p>` },
  { sub: "d1.6", title: "dbt_project.yml", body: `
<ul>
<li>Config per map: <code>models: mijn_project: staging: +materialized: view</code>. De <code>+</code> geeft aan dat het om een config gaat en niet om een submap.</li>
<li><b>Voorrang</b>: <code>config()</code> in het model wint van het properties-bestand (YAML), en dat wint van <code>dbt_project.yml</code>. Specifieker wint van algemener.</li>
<li>Ook hier: <code>vars:</code> (op te vragen met <code>var()</code>), <code>flags:</code> (gedrag van dbt), paden zoals <code>model-paths</code>.</li>
</ul>
<p class="small"><b>In v2:</b> een config-pad dat nergens op past, een verkeerd gespelde config of een dubbele sleutel geeft een fout bij het parsen (in v1 vaak alleen een waarschuwing).</p>` },
  { sub: "d1.7", title: "Packages", body: `
<ul>
<li>Packages zet je in <code>packages.yml</code> (of <code>dependencies.yml</code>) met een versie of versiebereik, bijv. <code>dbt-labs/dbt_utils</code>.</li>
<li><code>dbt deps</code> installeert ze in <code>dbt_packages/</code> en schrijft <code>package-lock.yml</code> met de exacte versies, zodat iedereen dezelfde krijgt.</li>
<li>Macro's uit een package roep je aan met de naam ervoor: <code>{{ dbt_utils.generate_surrogate_key([...]) }}</code>.</li>
</ul>
<p class="small"><b>In v2:</b> een package werkt als zijn <code>require-dbt-version</code> 2.0.0 toelaat (bijv. <code>&gt;=1.10.0,&lt;3.0.0</code>). Vragen een lokaal package en je project om verschillende versies van hetzelfde hub-package, dan geeft dat een fout.</p>` },
  { sub: "d1.8", title: "Python-modellen", body: `
<p>Een Python-model is een <code>.py</code>-bestand in <code>models/</code> met een functie <code>def model(dbt, session):</code> die een DataFrame teruggeeft.</p>
<ul>
<li><code>dbt.ref("x")</code> en <code>dbt.source("a", "b")</code> geven DataFrames; <code>dbt.config(materialized="table")</code> zet de config.</li>
<li>Alleen <b>table</b> en <b>incremental</b>. Bij incremental: <code>dbt.is_incremental</code> en <code>dbt.this</code>.</li>
<li>Gebruik Python voor wat in SQL lastig is (bijv. een library of model); voor gewone transformaties blijft SQL beter.</li>
<li><code>--sample</code> werkt (nog) niet voor Python-modellen.</li>
</ul>` },
  { sub: "d1.9", title: "Grants", body: `
<p>Met de config <code>grants</code> geeft dbt na het bouwen rechten op het object.</p>
<ul>
<li><code>grants: {select: ['rapportage']}</code> in een model, YAML of <code>dbt_project.yml</code> (<code>+grants</code>).</li>
<li>Standaard <b>vervangt</b> een specifiekere grants-config de algemene. Zet je een <code>+</code> voor het recht (<code>'+select': [...]</code>), dan <b>voegt</b> dbt het toe aan wat er al geërfd is.</li>
<li>dbt trekt rechten in die niet meer in de config staan, voor het object dat hij bouwt.</li>
</ul>` },
  { sub: "d1.10", title: "Snapshots in YAML", body: `
<p>Snapshots leggen veranderingen vast (type 2 SCD). Sinds 1.9 schrijf je ze in YAML:</p>
<pre><code>snapshots:
  - name: patienten_snapshot
    relation: source('hix', 'patienten')
    config:
      unique_key: id
      strategy: timestamp
      updated_at: gewijzigd_op</code></pre>
<ul>
<li><b>timestamp</b>: verandering zie je aan <code>updated_at</code>. <b>check</b>: dbt vergelijkt <code>check_cols</code> (of <code>all</code>), voor bronnen zonder betrouwbare wijzigingsdatum.</li>
<li>Extra kolommen: <code>dbt_valid_from</code>, <code>dbt_valid_to</code>, <code>dbt_scd_id</code>, <code>dbt_updated_at</code>.</li>
<li><code>dbt_valid_to_current</code>: een waarde (bijv. 9999-12-31) in plaats van NULL voor de huidige rij.</li>
<li><code>hard_deletes</code>: <code>ignore</code> (standaard), <code>invalidate</code> (rij afsluiten) of <code>new_record</code> (een nieuwe rij met <code>dbt_is_deleted</code>).</li>
</ul>` },
  { sub: "d1.11", title: "Incremental strategy kiezen", body: `
<ul>
<li><b>append</b>: alleen toevoegen, geen dubbelen herkennen. Voor logs of events die nooit veranderen.</li>
<li><b>merge</b>: bijwerken op <code>unique_key</code>, nieuwe rijen toevoegen. Standaard op Databricks.</li>
<li><b>delete+insert</b>: rijen met dezelfde sleutel eerst weg, dan opnieuw erin.</li>
<li><b>insert_overwrite</b>: hele partities vervangen (bijv. per dag).</li>
<li><b>microbatch</b>: in tijdvakken op <code>event_time</code> (zie microbatch).</li>
</ul>
<p>In de SQL filter je met <code>{% if is_incremental() %} where ... &gt; (select max(...) from {{ this }}) {% endif %}</code>. <code>--full-refresh</code> bouwt de tabel helemaal opnieuw. <code>on_schema_change</code> (<code>ignore</code>, <code>fail</code>, <code>append_new_columns</code>, <code>sync_all_columns</code>) bepaalt wat er gebeurt bij nieuwe kolommen.</p>` },
  { sub: "d1.12", title: "--empty", body: `
<p><code>dbt run --empty</code> of <code>dbt build --empty</code> bouwt je modellen met <b>nul rijen</b>: refs en sources krijgen een limit 0. Zo controleer je snel en goedkoop of de SQL klopt en de kolommen en types goed zijn, zonder data te verwerken.</p>
<ul><li>Handig in CI of na een grote wijziging. Tests op data zeggen dan weinig: er zijn geen rijen.</li></ul>` },
  { sub: "d1.13", title: "--sample", body: `
<p><code>--sample</code> (bij <code>run</code> en <code>build</code>) bouwt je modellen met een <b>stukje echte data</b>, gefilterd op tijd. Een stap verder dan <code>--empty</code>.</p>
<ul>
<li>Alleen <b>op tijd</b>: relatief (<code>--sample="3 days"</code>) of vast (een start en een eind).</li>
<li>dbt filtert refs en sources op hun <code>event_time</code>-config. Heeft een upstream model geen <code>event_time</code>, dan wordt het niet gefilterd.</li>
<li>Werkt niet voor Python-modellen. Seeds worden normaal gebouwd, maar gefilterd als je ernaar verwijst.</li>
</ul>` },
  { sub: "d1.14", title: "Microbatch", body: `
<p>Microbatch is een incremental strategy die het werk opknipt in <b>tijdvakken</b>. Verplicht: <code>event_time</code>, <code>begin</code> en <code>batch_size</code> (<code>hour</code>, <code>day</code>, <code>month</code>, <code>year</code>).</p>
<ul>
<li>Geen <code>is_incremental()</code>-filter nodig: dbt zet per batch zelf het tijdfilter, ook op upstream modellen met een <code>event_time</code>.</li>
<li><code>lookback</code>: zoveel eerdere batches opnieuw verwerken voor late data (standaard 1).</li>
<li>Herladen: <code>dbt run --event-time-start "2026-01-01" --event-time-end "2026-02-01"</code>. Alleen <code>--full-refresh</code> zonder die grenzen laadt niets opnieuw.</li>
<li>Batches lopen parallel als dbt dat veilig vindt; met <code>concurrent_batches</code> dwing je het af of zet je het uit.</li>
<li><code>dbt retry</code> draait alleen de mislukte batches opnieuw.</li>
</ul>` }
] },

/* ================================================= D2 Governance */
d2: { sections: [
  { sub: "d2.1", title: "Model contracts", body: `
<p>Een contract legt de <b>vorm</b> van een model vast: welke kolommen, met welk datatype.</p>
<pre><code>models:
  - name: dim_patient
    config:
      contract: {enforced: true}
    columns:
      - name: patient_id
        data_type: bigint</code></pre>
<ul>
<li>Elke kolom moet in de YAML staan met <code>name</code> en <code>data_type</code>. Klopt de SQL er niet mee (kolom erbij, weg of ander type), dan faalt de build vóórdat er iets wordt gebouwd.</li>
<li>Voor modellen waar anderen op bouwen: een wijziging in de vorm wordt dan een bewuste keuze (en vaak een nieuwe versie).</li>
<li>Werkt niet voor ephemeral modellen.</li>
</ul>` },
  { sub: "d2.2", title: "Versies en uitfaseren", body: `
<pre><code>models:
  - name: dim_patient
    latest_version: 2
    versions:
      - v: 1
        deprecation_date: 2026-12-31
      - v: 2</code></pre>
<ul>
<li><code>ref('dim_patient')</code> zonder versie geeft de <code>latest_version</code>. Met <code>ref('dim_patient', v=1)</code> pin je een oude versie.</li>
<li>Standaard heet de tabel <code>dim_patient_v1</code>, <code>dim_patient_v2</code>. Met <code>defined_in</code> wijs je per versie een ander SQL-bestand aan.</li>
<li><code>deprecation_date</code>: dbt waarschuwt wie de oude versie nog gebruikt. Zo geef je afnemers tijd om over te stappen.</li>
</ul>` },
  { sub: "d2.3", title: "Constraints", body: `
<p>Constraints laten het <b>platform</b> regels afdwingen: <code>not_null</code>, <code>unique</code>, <code>primary_key</code>, <code>foreign_key</code>, <code>check</code>.</p>
<ul>
<li>Je zet ze per kolom (of op modelniveau) in YAML. Ze worden alleen toegepast als het <b>contract</b> afgedwongen wordt.</li>
<li>Of een platform een constraint echt afdwingt, verschilt. Databricks dwingt <code>not_null</code> en <code>check</code> af; primary en foreign keys zijn daar alleen informatief.</li>
<li>Een constraint is geen vervanging van een test: een test controleert achteraf, een afgedwongen constraint houdt foute data tegen.</li>
</ul>` }
] },

/* ================================================= D3 Debuggen */
d3: { sections: [
  { sub: "d3.1", title: "Foutmeldingen lezen", body: `
<ul>
<li><b>Compilation Error</b>: Jinja of YAML klopt niet (bijv. onbekende macro, verkeerde ref).</li>
<li><b>Database Error</b>: de SQL is gecompileerd, maar het platform weigert hem (bijv. kolom bestaat niet).</li>
<li><b>Dependency Error</b>: iets met packages of de DAG (bijv. een kring).</li>
<li>De melding noemt het model en vaak het pad naar het gecompileerde bestand. Meer detail staat in <code>logs/dbt.log</code>; de uitkomst per model in <code>target/run_results.json</code>.</li>
</ul>
<p class="small"><b>In v2:</b> veel fouten komen eerder, al bij het parsen: onbekende macro's, ongedefinieerde variabelen en onbekende tests.</p>` },
  { sub: "d3.2", title: "Gecompileerde SQL", body: `
<ul>
<li><code>dbt compile</code> zet de Jinja om naar gewone SQL in <code>target/compiled/</code>: de select-query zoals hij echt draait.</li>
<li>In <code>target/run/</code> staat wat dbt werkelijk uitvoerde, met de create- of merge-statement eromheen.</li>
<li>Debuggen: open het gecompileerde bestand, draai het los in het platform, en zoek de fout in de echte SQL in plaats van in de Jinja.</li>
<li><code>dbt show -s model</code> toont de uitkomst zonder te bouwen.</li>
</ul>
<p class="small"><b>In v2:</b> <code>compile</code> stopt niet bij de eerste fout maar slaat alleen de modellen erna over.</p>` },
  { sub: "d3.3", title: "YAML-fouten", body: `
<ul>
<li>Meest voorkomend: verkeerde inspringing, een lijst waar een object hoort (of andersom), een sleutel op de verkeerde plek of een dubbele sleutel.</li>
<li><code>dbt parse</code> controleert het hele project zonder iets te draaien.</li>
<li>Sinds 1.8 heten tests in YAML <code>data_tests:</code> (voorheen <code>tests:</code>). Argumenten van generieke tests horen onder <code>arguments:</code>.</li>
<li>Eigen eigenschappen horen in <code>meta:</code>, niet als losse sleutel.</li>
</ul>
<p class="small"><b>In v2:</b> onbekende of verkeerd gespelde sleutels zijn een fout, geen waarschuwing meer. Losse YAML-ankers horen onder een sleutel <code>anchors:</code>.</p>` },
  { sub: "d3.4", title: "Fix maken vóór de merge", body: `
<ol>
<li>Werk op een eigen branch en een eigen dev-schema (target <code>dev</code>), nooit direct in productie.</li>
<li>Reproduceer de fout, pas de code aan, en draai het model en alles erna: <code>dbt build -s model+</code>.</li>
<li>Voeg een test toe die de fout had gevangen, zodat hij niet terugkomt.</li>
<li>Open een pull request. In CI draait alleen wat veranderd is: <code>dbt build -s state:modified+ --defer --state prod-artifacts</code>. Merge pas als alles groen is.</li>
</ol>` },
  { sub: "d3.5", title: "Flags", body: `
<ul>
<li>Op de commandoregel: <code>--fail-fast</code> (stop bij de eerste fout), <code>--full-refresh</code>, <code>--warn-error</code> (waarschuwingen worden fouten), <code>--warn-error-options</code> (alleen bepaalde waarschuwingen), <code>--debug</code>, <code>--log-level</code>.</li>
<li>Voorrang: commandoregel &gt; omgevingsvariabele (<code>DBT_...</code>) &gt; <code>flags:</code> in <code>dbt_project.yml</code>.</li>
<li><b>Behavior change flags</b> in <code>flags:</code> laten je een nieuw gedrag van dbt eerder aanzetten, of tijdelijk uitzetten tijdens een migratie.</li>
</ul>
<p class="small"><b>In v2:</b> flags gemarkeerd met "2.0" zijn weg: het nieuwe gedrag staat altijd aan en je kunt het niet meer uitzetten.</p>` }
] },

/* ================================================= D4 Pipelines */
d4: { sections: [
  { sub: "d4.1", title: "Faalpunten in de DAG", body: `
<ul>
<li>Faalt een model of een test met severity <code>error</code> in <code>dbt build</code>, dan krijgen de modellen erna <b>SKIP</b>. De rest van de DAG gaat door.</li>
<li><code>--fail-fast</code>: stop de hele run bij de eerste fout.</li>
<li>Test die niet moet blokkeren? Zet <code>severity: warn</code>, of gebruik <code>warn_if</code> / <code>error_if</code> met een drempel.</li>
<li>Na een fout: <code>dbt retry</code> draait alleen wat mislukte of werd overgeslagen.</li>
</ul>` },
  { sub: "d4.2", title: "dbt clone", body: `
<p><code>dbt clone --state pad/naar/prod-artifacts -s ...</code> maakt kopieën van productieobjecten in je eigen schema.</p>
<ul>
<li>Waar het platform het kan (Databricks, Snowflake, BigQuery) is dat een <b>zero-copy clone</b>; anders maakt dbt een view naar productie.</li>
<li>Handig in CI om incremental modellen te testen tegen een echte stand, of om een dev-omgeving snel te vullen.</li>
<li>Verschil met <code>--defer</code>: defer laat ontbrekende upstream refs <b>bij het compileren</b> naar productie wijzen zonder iets te maken; clone <b>maakt echte objecten</b> in jouw schema.</li>
<li>Bestaande objecten slaat clone over, tenzij je <code>--full-refresh</code> gebruikt.</li>
</ul>` }
] },

/* ================================================= D5 Tests */
d5: { sections: [
  { sub: "d5.1", title: "Soorten tests", body: `
<ul>
<li><b>Generieke tests</b> (in YAML): <code>unique</code>, <code>not_null</code>, <code>accepted_values</code>, <code>relationships</code>.</li>
<li><b>Singular test</b>: een SQL-bestand in <code>tests/</code> dat de <b>foute rijen</b> selecteert. Nul rijen = geslaagd.</li>
<li><b>Custom generic test</b>: een herbruikbare test als <code>{% test naam(model, column_name) %} ... {% endtest %}</code>, daarna te gebruiken in YAML zoals een ingebouwde test.</li>
<li><b>Unit test</b> (sinds 1.8, onder <code>unit_tests:</code>): test de <b>logica</b> van een SQL-model met vaste invoer (<code>given</code>) en verwachte uitkomst (<code>expect</code>), vóórdat je het model bouwt. Draai ze in dev en CI, niet in productie.</li>
</ul>
<p class="small"><b>Let op:</b> argumenten van generieke tests horen onder <code>arguments:</code> (bijv. <code>accepted_values: {arguments: {values: [...]}}</code>). <b>In v2</b> is dat verplicht.</p>` },
  { sub: "d5.2", title: "Aannames testen", body: `
<ul>
<li>Test ook <b>sources</b>: daar komen de fouten vandaan. Zet de tests in de sources-YAML.</li>
<li><code>severity: warn</code> of <code>error</code>; met <code>warn_if: "&gt;10"</code> en <code>error_if: "&gt;100"</code> stel je drempels in.</li>
<li><code>where:</code> beperkt de test tot een deel van de rijen (bijv. alleen actieve rijen); <code>limit:</code> beperkt de foute rijen die hij teruggeeft.</li>
<li><code>store_failures: true</code> bewaart de foute rijen in een tabel, zodat je ze kunt bekijken.</li>
</ul>` },
  { sub: "d5.3", title: "Tests in de workflow", body: `
<ul>
<li><b>Tijdens ontwikkelen</b>: unit tests voor lastige logica, <code>dbt build -s model+</code>.</li>
<li><b>In CI</b>: alleen wat veranderd is, plus alles erna (<code>state:modified+</code>), met <code>--defer</code> naar productie.</li>
<li><b>In productie</b>: <code>dbt build</code>, zodat tests direct na elk model draaien en foute data niet verder loopt. Source freshness vóór de run.</li>
<li>Alleen tests van één soort selecteren: <code>dbt test -s test_type:unit</code> of <code>test_type:data</code>.</li>
</ul>` }
] },

/* ================================================= D6 Externe afhankelijkheden */
d6: { sections: [
  { sub: "d6.1", title: "Exposures", body: `
<p>Een exposure beschrijft wie je modellen gebruikt buiten dbt, bijvoorbeeld een Power BI-rapport.</p>
<pre><code>exposures:
  - name: wachttijden_dashboard
    type: dashboard
    owner: {name: BI-team, email: bi@voorbeeld.nl}
    depends_on: [ref('fct_wachttijden')]</code></pre>
<ul>
<li><code>type</code>: dashboard, notebook, analysis, ml of application. <code>owner</code> is verplicht.</li>
<li>Exposures worden niet gebouwd. Ze staan in de DAG en de docs, en je kunt selecteren: <code>dbt build -s +exposure:wachttijden_dashboard</code> bouwt alles wat het dashboard nodig heeft.</li>
</ul>` },
  { sub: "d6.2", title: "Source freshness", body: `
<pre><code>sources:
  - name: hix
    config:
      loaded_at_field: _geladen_op
      freshness:
        warn_after: {count: 12, period: hour}
        error_after: {count: 24, period: hour}</code></pre>
<ul>
<li><code>dbt source freshness</code> vergelijkt de nieuwste <code>loaded_at_field</code> met nu, en schrijft de uitkomst naar <code>target/sources.json</code>.</li>
<li>Met de vorige uitkomst als <code>--state</code> selecteer je <code>source_status:fresher+</code>: alleen bouwen wat nieuwe brondata heeft.</li>
</ul>
<p class="small"><b>In v2:</b> freshness kan ook op modellen, met het commando <code>dbt freshness</code> (schrijft <code>target/freshness.json</code>). <code>dbt source freshness</code> blijft voor sources.</p>` }
] },

/* ================================================= D7 State */
d7: { sections: [
  { sub: "d7.1", title: "State en defer", body: `
<p><b>State</b> = de artefacten (vooral <code>manifest.json</code>) van een eerdere run, meestal productie. Met <code>--state pad</code> vergelijkt dbt je project daarmee.</p>
<ul>
<li><code>state:modified</code> (gewijzigd), <code>state:new</code> (nieuw), en fijner: <code>state:modified.body</code>, <code>.configs</code>, <code>.contract</code>.</li>
<li><code>--defer</code>: een upstream model dat je niet bouwt, leest dbt uit productie in plaats van uit je eigen schema. Zo hoef je in CI niet alles te bouwen.</li>
<li><code>result:error</code> of <code>result:fail</code> (met <code>run_results.json</code> als state): selecteer wat de vorige keer misging.</li>
</ul>
<p class="small"><b>In v2:</b> het manifest is versie 12 en werkt samen met v1, dus <code>state:modified</code> en <code>--defer</code> werken ook als productie nog op v1 draait.</p>` },
  { sub: "d7.2", title: "dbt retry", body: `
<p><code>dbt retry</code> draait de vorige opdracht opnieuw <b>vanaf het punt waar het misging</b>. Hij leest <code>target/run_results.json</code> en draait alleen wat mislukte of werd overgeslagen, met dezelfde flags.</p>
<ul>
<li>Ging de vorige run goed, dan doet retry niets.</li>
<li>Bij microbatch: alleen de mislukte batches.</li>
<li>Run je tussendoor een ander commando, dan overschrijft dat <code>run_results.json</code> en weet retry niet meer wat er misging.</li>
</ul>` }
] },

/* ================================================= D8 dbt v2 */
d8: { sections: [
  { sub: "d8.1", title: "Upgraden naar v2", body: `
<p>dbt v2 is de Rust-engine (voorheen Fusion), algemeen beschikbaar sinds september 2026. Het is <b>strenger, niet anders</b>: wat in v1 een waarschuwing was, is nu vaak een fout.</p>
<ul>
<li>Los <b>alle deprecation-waarschuwingen</b> op in v1 vóór je overstapt. <code>dbt-autofix</code> doet veel automatisch. In v1.12 test je de nieuwe parser met <code>--use-v2-parser</code>.</li>
<li><code>--models</code> / <code>-m</code> geven een fout; <code>--partial-parse</code> werkt niet in v2-jobs.</li>
<li>Verkeerd gespelde configs, onbekende YAML-sleutels, onbekende macro's en ongedefinieerde <code>var()</code>'s falen al bij het parsen.</li>
<li>Installeren: <code>pip install dbt</code>. Verbinding met het platform gaat via <b>ADBC-drivers</b>, niet meer via Python-adapters.</li>
</ul>` },
  { sub: "d8.2", title: "Nieuw en anders in v2", body: `
<ul>
<li><code>dbt build</code> draait eerst alle unit tests. Bij Databricks regelt dbt het aantal threads zelf (<code>threads</code> is dan een maximum).</li>
<li><code>meta</code> uitlezen in macro's: <code>config.meta_get('owner')</code> en <code>config.meta_require('pii')</code>.</li>
<li>Nieuw: <code>dbt lint</code> (compatibel met SQLFluff), <code>dbt check</code> (SQL-regels in <code>checks/</code>, draaien mee in build), freshness op modellen met <code>dbt freshness</code>, kolom-lineage met <code>--static-analysis strict</code>.</li>
<li><code>dbt clean</code> verwijdert nooit meer bestanden in je eigen resource-paden of buiten het project.</li>
<li>State-aware orchestration heet nu <b>dbt State</b>.</li>
</ul>` }
] }
});
