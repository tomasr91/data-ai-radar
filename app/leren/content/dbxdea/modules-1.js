/* Databricks Data Engineer Associate: uitleg per subonderwerp.
   Gebaseerd op de officiële examengids (augustus 2026) en docs.databricks.com, gecontroleerd op 25 november 2026. */
Academy.addModules("dbxdea", {

d1: { sections: [
  { sub: "d1.1", title: "Onderdelen van het platform", body: `
<ul>
<li><b>Lakehouse</b>: je data staat als open bestanden in je eigen cloudopslag; Databricks rekent erop.</li>
<li><b>Delta Lake</b>: tabelformaat bovenop Parquet met een transactielog: ACID, time travel (<code>VERSION AS OF</code>), <code>MERGE</code>, schema-afdwinging.</li>
<li><b>Unity Catalog</b>: één plek voor rechten, lineage en vindbaarheid. Namen in drie delen: <code>catalog.schema.tabel</code>. Ook volumes (bestanden), functies en modellen.</li>
<li>Control plane (beheer, door Databricks) en compute plane (waar je data verwerkt wordt).</li>
</ul>` },
  { sub: "d1.2", title: "Compute kiezen", body: `
<ul>
<li><b>Serverless</b> (notebooks, jobs, pipelines): start in seconden, geen clusterbeheer; je betaalt per gebruik.</li>
<li><b>Jobs compute</b>: een cluster dat alleen voor één job-run draait en daarna stopt. Goedkoper dan all-purpose.</li>
<li><b>All-purpose compute</b>: voor interactief werken in notebooks; duurder per DBU.</li>
<li><b>SQL warehouse</b>: voor SQL, dashboards en BI-tools zoals Power BI. Serverless start het snelst.</li>
</ul>
<p>Vuistregel: geplande productie → jobs compute of serverless; ontwikkelen → all-purpose; SQL en BI → SQL warehouse.</p>` }
] },

d2: { sections: [
  { sub: "d2.1", title: "Batch, streaming, incrementeel", body: `
<ul>
<li><b>Batch</b>: alles in één keer lezen en schrijven.</li>
<li><b>Streaming</b> (<code>readStream</code>/<code>writeStream</code>): verwerkt nieuwe data doorlopend; een <b>checkpoint</b> onthoudt wat al verwerkt is.</li>
<li><b>Incrementeel als batch</b>: een stream met <code>trigger(availableNow=True)</code> verwerkt alles wat nieuw is en stopt dan. Ideaal in een geplande job.</li>
</ul>` },
  { sub: "d2.2", title: "COPY INTO", body: `
<pre><code>COPY INTO main.bronze.opnames
FROM '/Volumes/main/landing/opnames'
FILEFORMAT = JSON
COPY_OPTIONS ('mergeSchema' = 'true')</code></pre>
<ul>
<li><b>Idempotent</b>: bestanden die al geladen zijn, slaat hij over. Je kunt hem dus veilig opnieuw draaien.</li>
<li>Geschikt voor duizenden bestanden; bij miljoenen bestanden of doorlopend binnenkomende data is Auto Loader beter.</li>
</ul>` },
  { sub: "d2.3", title: "Auto Loader", body: `
<p>Auto Loader (<code>format("cloudFiles")</code>) leest nieuwe bestanden uit cloudopslag incrementeel. Met <code>cloudFiles.schemaLocation</code> bewaart hij het afgeleide schema.</p>
<ul>
<li>JSON en CSV: alle kolommen worden standaard als string afgeleid (met <code>inferColumnTypes</code> echte types).</li>
<li><code>cloudFiles.schemaEvolutionMode</code>:
<ul><li><b>addNewColumns</b> (standaard zonder opgegeven schema): de stream stopt bij een nieuwe kolom en voegt hem toe bij de herstart. Laat een job hem automatisch herstarten.</li>
<li><b>rescue</b>: schema verandert nooit, stream stopt niet; nieuwe kolommen gaan in <code>_rescued_data</code>.</li>
<li><b>failOnNewColumns</b>: stream faalt tot je het schema aanpast.</li>
<li><b>none</b>: niets aanpassen, nieuwe kolommen negeren (standaard als je zelf een schema opgeeft).</li></ul></li>
</ul>` },
  { sub: "d2.4", title: "Lakeflow Connect", body: `
<ul>
<li><b>Managed connectors</b> halen data uit SaaS-apps (bijv. Salesforce, Workday) en databases (bijv. SQL Server) naar Delta-tabellen, incrementeel en zonder eigen code.</li>
<li>Voor databases loopt dat via een <b>ingestion gateway</b> (leest de wijzigingen) en een <b>ingestion pipeline</b> (schrijft naar streaming tables).</li>
<li>Beheer, rechten en lineage gaan via Unity Catalog.</li>
</ul>` },
  { sub: "d2.5", title: "JDBC, ODBC en REST", body: `
<ul>
<li>Is er geen connector? Lees met <code>spark.read.format("jdbc")</code> uit een database, of haal data op uit een REST-API met een notebook of script.</li>
<li>Bewaar wachtwoorden en tokens in <b>secrets</b> (<code>dbutils.secrets.get</code>), nooit in de code.</li>
<li>Plan het als taak in een <b>Lakeflow Job</b>, met retries voor tijdelijke fouten.</li>
</ul>` },
  { sub: "d2.6", title: "De juiste manier kiezen", body: `
<ul>
<li>Bestanden in cloudopslag, veel of doorlopend → <b>Auto Loader</b>.</li>
<li>Bestanden, beperkt aantal, SQL-gebruikers → <b>COPY INTO</b>.</li>
<li>SaaS-app of database met een managed connector → <b>Lakeflow Connect</b>.</li>
<li>Bron die Databricks niet zelf kent → <b>partnerconnector</b> of eigen JDBC/REST-code in een job.</li>
</ul>` },
  { sub: "d2.7", title: "JSON en geneste data", body: `
<ul>
<li>Geneste velden lees je met een punt: <code>adres.plaats</code>. Op een kolom met een JSON-string: <code>kolom:veld</code> of <code>from_json</code>.</li>
<li>Een array maak je plat met <code>explode</code>: één rij per element.</li>
<li>Het type <b>VARIANT</b> slaat semi-gestructureerde data flexibel en snel op (<code>parse_json</code>).</li>
<li>Bestanden zonder vaste structuur (pdf, afbeeldingen) zet je in een <b>volume</b>; met <code>binaryFile</code> lees je ze als bytes.</li>
</ul>` }
] },

d3: { sections: [
  { sub: "d3.1", title: "Bronze naar silver", body: `
<ul>
<li>In silver: types goedzetten (<code>cast</code>), lege waarden afhandelen (<code>coalesce</code>, <code>fillna</code>, <code>dropna</code>), namen gelijk trekken, ontdubbelen.</li>
<li>Schrijf naar een Delta-tabel in Unity Catalog; incrementeel met <code>MERGE INTO</code> op een sleutel.</li>
</ul>` },
  { sub: "d3.2", title: "Joins en set-operaties", body: `
<ul>
<li><b>inner</b>: alleen rijen die aan beide kanten bestaan; <b>left</b>: alle rijen links, rechts NULL als er niets is; <b>cross</b>: elke rij met elke rij.</li>
<li><b>Broadcast join</b>: de kleine tabel gaat naar elke worker, zodat de grote niet geshuffeld hoeft te worden (<code>broadcast(df)</code> of hint <code>/*+ BROADCAST(t) */</code>).</li>
<li><b>UNION</b> haalt dubbele rijen weg, <b>UNION ALL</b> niet (en is daardoor sneller). In PySpark: <code>union</code> houdt dubbelen; <code>unionByName</code> koppelt op kolomnaam.</li>
</ul>` },
  { sub: "d3.3", title: "Kolommen en rijen", body: `
<ul>
<li><code>withColumn</code> (toevoegen/wijzigen), <code>drop</code>, <code>withColumnRenamed</code>, <code>filter</code>/<code>where</code>.</li>
<li><code>split(kolom, ',')</code> maakt een array; <code>explode</code> maakt er rijen van.</li>
</ul>` },
  { sub: "d3.4", title: "Ontdubbelen en aggregeren", body: `
<ul>
<li><code>dropDuplicates(["id"])</code> houdt één rij per id, maar je kiest niet welke. Wil je de nieuwste: <code>row_number()</code> over een window per id, gesorteerd op datum, en houd rij 1.</li>
<li><code>approx_count_distinct</code>: snelle schatting van het aantal unieke waarden bij grote tabellen.</li>
<li><code>describe()</code> / <code>summary()</code>: snelle statistiek (aantal, gemiddelde, min, max).</li>
</ul>` },
  { sub: "d3.5", title: "Spark-instellingen", body: `
<ul>
<li><code>spark.sql.shuffle.partitions</code>: aantal partities na een shuffle (standaard 200). Met <b>Adaptive Query Execution</b> (AQE, standaard aan) past Spark dit tijdens het draaien aan.</li>
<li><code>spark.sql.autoBroadcastJoinThreshold</code>: tot welke grootte Spark zelf een broadcast join kiest.</li>
<li>Verander één ding tegelijk en <b>meet opnieuw</b> (looptijd, Spark UI).</li>
</ul>` },
  { sub: "d3.6", title: "Objecten in de gold-laag", body: `
<ul>
<li><b>View</b>: alleen een opgeslagen query; altijd actueel, rekent bij elke vraag.</li>
<li><b>Materialized view</b>: uitkomst wordt opgeslagen en ververst (waar het kan incrementeel). Goed voor zware aggregaties die vaak gelezen worden.</li>
<li><b>Streaming table</b>: voor data die alleen wordt toegevoegd; verwerkt elke nieuwe rij één keer.</li>
<li><b>Table</b>: gewone Delta-tabel die je zelf vult.</li>
</ul>` },
  { sub: "d3.7", title: "Datakwaliteit", body: `
<p>In Lakeflow Declarative Pipelines leg je regels vast als <b>expectations</b>:</p>
<pre><code>CONSTRAINT geldige_datum EXPECT (opname_dt IS NOT NULL)
  ON VIOLATION DROP ROW</code></pre>
<ul>
<li>Zonder ON VIOLATION: rij blijft staan, de schending wordt geteld. <b>DROP ROW</b>: rij weg. <b>FAIL UPDATE</b>: de update stopt.</li>
<li>In Python: <code>@dp.expect</code>, <code>@dp.expect_or_drop</code>, <code>@dp.expect_or_fail</code>.</li>
<li>Buiten pipelines: Delta <code>CHECK</code>-constraints en <code>NOT NULL</code> houden foute data tegen bij het schrijven.</li>
</ul>` }
] },

d4: { sections: [
  { sub: "d4.1", title: "Retries, voorwaarden en lussen", body: `
<ul>
<li><b>Retries</b> per taak: bij een (tijdelijke) fout probeert de job het opnieuw, met een wachttijd ertussen.</li>
<li><b>Run if</b>: wanneer een taak draait, bijv. alleen als alles ervoor gelukt is, of juist als er iets mislukte (voor een melding of opruimtaak).</li>
<li><b>If/else-taak</b>: vertakken op een waarde (bijv. een taakwaarde of parameter).</li>
<li><b>For each-taak</b>: dezelfde taak draaien voor elk item in een lijst (bijv. per bron of per tabel).</li>
<li><b>Repair run</b>: alleen de mislukte taken en wat ervan afhangt opnieuw draaien.</li>
</ul>` },
  { sub: "d4.2", title: "Taken en afhankelijkheden", body: `
<ul>
<li>Taaksoorten: notebook, SQL, Python-script, pipeline, dashboard, dbt, een andere job.</li>
<li>Met <b>depends on</b> bouw je een DAG; taken zonder onderlinge afhankelijkheid draaien tegelijk.</li>
<li>Waarden doorgeven tussen taken: <b>task values</b> (<code>dbutils.jobs.taskValues.set/get</code>).</li>
</ul>` },
  { sub: "d4.3", title: "Schema's en triggers", body: `
<ul>
<li><b>Scheduled</b>: op tijd (cron).</li>
<li><b>File arrival</b>: zodra er nieuwe bestanden in een Unity Catalog-locatie (volume of external location) komen.</li>
<li><b>Table update</b>: zodra een of meer tabellen in Unity Catalog nieuwe data hebben (bij meerdere: als één of als alle bijgewerkt zijn).</li>
<li><b>Continuous</b>: de job draait steeds opnieuw zodra de vorige klaar is.</li>
</ul>` },
  { sub: "d4.4", title: "Op tijd of op data", body: `
<ul>
<li>Tijd: als afnemers een vast moment verwachten, of als de bron geen signaal geeft.</li>
<li>Data: als de bron onregelmatig levert. Je rekent dan alleen als er echt iets nieuws is, en de data is sneller klaar.</li>
</ul>` }
] },

d5: { sections: [
  { sub: "d5.1", title: "Git in de workspace", body: `
<ul>
<li><b>Git folders</b> koppelen een map in de workspace aan een repository (bijv. Azure DevOps).</li>
<li>In de UI: branch maken, wijzigingen committen en pushen, pullen. De pull request maak en review je bij de Git-provider.</li>
</ul>` },
  { sub: "d5.2", title: "Variabelen en targets", body: `
<pre><code>variables:
  catalog:
    default: dev
targets:
  dev:
    mode: development
  prod:
    variables:
      catalog: prod</code></pre>
<ul>
<li>Gebruik met <code>\${var.catalog}</code>. Per target kun je variabelen en instellingen <b>overschrijven</b>.</li>
<li><code>mode: development</code> zet een prefix met je naam voor resources en pauzeert schema's, zodat je dev-jobs niet botsen met die van anderen.</li>
</ul>` },
  { sub: "d5.3", title: "Uitrollen", body: `
<ul>
<li>Eén bundle (<code>databricks.yml</code>) beschrijft jobs, pipelines en andere resources als code.</li>
<li>Uitrollen naar een omgeving: <code>databricks bundle deploy -t prod</code>. Zelfde code, andere instellingen per target.</li>
</ul>` },
  { sub: "d5.4", title: "De CLI", body: `
<ul>
<li><code>databricks bundle validate</code>: klopt de configuratie?</li>
<li><code>databricks bundle deploy -t &lt;target&gt;</code>: uitrollen. <code>databricks bundle run &lt;job&gt;</code>: een job starten.</li>
<li>In een CI-pipeline (bijv. Azure Pipelines) logt de CLI in met een service principal.</li>
</ul>` }
] },

d6: { sections: [
  { sub: "d6.1", title: "Looptijden en trends", body: `
<ul>
<li>De run-geschiedenis van een job laat de looptijd per run zien. Wordt een run steeds langer, kijk dan naar groeiende data, skew of kleine bestanden.</li>
<li>Systeemtabellen (<code>system.lakeflow</code>) geven run-gegevens voor eigen analyses en meldingen.</li>
</ul>` },
  { sub: "d6.2", title: "Gezondheid bewaken", body: `
<ul>
<li>Bij een job: de status per run en per taak in de matrix- en grafiekweergave. Je ziet meteen welke taak faalde.</li>
<li>Bij een pipeline: de event log met de status per tabel en de expectations.</li>
<li>Meldingen (e-mail, webhook) bij mislukken of te lange looptijd.</li>
</ul>` },
  { sub: "d6.3", title: "Skew, shuffle en spill", body: `
<ul>
<li><b>Skew</b>: één taak in een stage duurt veel langer of verwerkt veel meer data dan de rest. Oplossing: AQE skew join, of de sleutel beter verdelen.</li>
<li><b>Shuffle</b>: data gaat over het netwerk tussen workers (bij joins, groupBy). Veel shuffle-lees/schrijf in de stage-metrics.</li>
<li><b>Spill</b>: er past te weinig in het geheugen, dus Spark schrijft naar schijf ("spill (disk)"). Oplossing: meer geheugen per taak of meer partities.</li>
</ul>` },
  { sub: "d6.4", title: "Liquid Clustering en predictive optimization", body: `
<ul>
<li><b>Liquid Clustering</b> (<code>CLUSTER BY (kolom)</code>) ordent data op kolommen waarop je vaak filtert. Vervangt partitioneren en ZORDER; sleutels kun je later wijzigen met <code>ALTER TABLE ... CLUSTER BY</code>. Met <code>CLUSTER BY AUTO</code> kiest Databricks ze zelf.</li>
<li><b>Predictive optimization</b> voert onderhoud als <code>OPTIMIZE</code>, <code>VACUUM</code> en statistieken automatisch uit, voor managed tables in Unity Catalog.</li>
</ul>` },
  { sub: "d6.5", title: "Startfouten, libraries, geheugen", body: `
<ul>
<li><b>Cluster start niet</b>: kijk in de event log; vaak quota of capaciteit bij de cloud, of een mislukt init-script.</li>
<li><b>Library-conflict</b>: twee versies van hetzelfde package; pin versies, kijk wat de runtime al meebrengt.</li>
<li><b>Out of memory op de driver</b>: vaak <code>collect()</code> of <code>toPandas()</code> op veel data. Op executors: te grote partities of skew.</li>
</ul>` }
] },

d7: { sections: [
  { sub: "d7.1", title: "Managed en external", body: `
<ul>
<li><b>Managed</b>: Unity Catalog beheert opslag en levenscyclus. <code>DROP TABLE</code> verwijdert ook de data (met <code>UNDROP</code> kun je een tijdje terug). Predictive optimization werkt alleen hier.</li>
<li><b>External</b>: data staat op een eigen locatie (<code>LOCATION</code>, via een external location). <code>DROP TABLE</code> verwijdert alleen de definitie; de bestanden blijven.</li>
</ul>` },
  { sub: "d7.2", title: "GRANT en REVOKE", body: `
<pre><code>GRANT USE CATALOG ON CATALOG main TO \`bi\`;
GRANT USE SCHEMA, SELECT ON SCHEMA main.gold TO \`bi\`;</code></pre>
<ul>
<li>Om een tabel te lezen heb je nodig: <code>USE CATALOG</code> op de catalog, <code>USE SCHEMA</code> op het schema en <code>SELECT</code> op de tabel (of hoger).</li>
<li>Rechten op een catalog of schema gelden ook voor alles eronder, ook voor tabellen die er later bij komen.</li>
<li>Geef rechten aan groepen, niet aan losse gebruikers. <code>REVOKE</code> haalt ze weer weg.</li>
</ul>` },
  { sub: "d7.3", title: "Kolommaskers en rijfilters", body: `
<pre><code>CREATE FUNCTION afdeling_filter(afd STRING)
  RETURN is_account_group_member('admin') OR afd = 'cardiologie';
ALTER TABLE opnames SET ROW FILTER afdeling_filter ON (afdeling);</code></pre>
<ul>
<li>Een <b>rijfilter</b> is een functie die per rij true of false geeft. Een <b>kolommasker</b> geeft per gebruiker de echte of een afgeschermde waarde (<code>ALTER COLUMN ... SET MASK</code>).</li>
<li>Met <code>is_account_group_member()</code> kijk je in welke groep iemand zit.</li>
</ul>` },
  { sub: "d7.4", title: "ABAC", body: `
<ul>
<li>Bij <b>ABAC</b> zet je <b>governed tags</b> op objecten (bijv. <code>gevoelig = ja</code> op kolommen) en maak je één policy op een catalog of schema.</li>
<li>De policy past een rijfilter of kolommasker toe op <b>alle</b> tabellen en kolommen met die tag, ook nieuwe. Je hoeft niet per tabel een filter te zetten.</li>
<li>Governed tags worden op accountniveau beheerd: niet iedereen mag ze maken of toekennen.</li>
</ul>` }
] }
});
