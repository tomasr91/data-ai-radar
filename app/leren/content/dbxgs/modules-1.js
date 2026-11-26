/* Get Started with Databricks for Data Engineering: uitleg per onderwerp (beginnersniveau).
   Onderwerpen volgens de cursuspagina van Databricks Academy; feiten uit docs.databricks.com (26 november 2026). */
Academy.addModules("dbxgs", {

d1: { sections: [
  { sub: "d1.1", title: "Workspace, notebooks en compute", body: `
<ul>
<li>De <b>workspace</b> is waar je werkt: notebooks, SQL-editor, jobs, pipelines en de Catalog Explorer staan in het menu links.</li>
<li>Een <b>notebook</b> bestaat uit cellen. Per cel kies je de taal met een magic: <code>%sql</code>, <code>%python</code>, <code>%md</code> (tekst).</li>
<li>Om iets te draaien heb je <b>compute</b> nodig: serverless (start direct), een cluster, of een SQL warehouse voor SQL.</li>
</ul>` },
  { sub: "d1.2", title: "Unity Catalog", body: `
<ul>
<li>Unity Catalog ordent data in drie niveaus: <b>catalog → schema → tabel</b>. Een tabel heet voluit <code>catalog.schema.tabel</code>.</li>
<li>Met <code>USE CATALOG</code> en <code>USE SCHEMA</code> stel je in waar je standaard werkt.</li>
<li>Bestanden (CSV, JSON) horen in een <b>volume</b>: <code>/Volumes/catalog/schema/volume/bestand.csv</code>.</li>
<li>In <b>Catalog Explorer</b> zie je tabellen, kolommen, voorbeelddata, rechten en lineage.</li>
</ul>` }
] },

d2: { sections: [
  { sub: "d2.1", title: "Tabellen maken", body: `
<pre><code>CREATE TABLE IF NOT EXISTS opnames (
  opname_id BIGINT,
  afdeling STRING,
  opname_dt DATE
);</code></pre>
<ul>
<li>Op Databricks is elke tabel standaard een <b>Delta</b>-tabel en <b>managed</b>: Unity Catalog bewaart de bestanden.</li>
<li><code>IF NOT EXISTS</code>: geen fout als de tabel er al is. <code>CREATE OR REPLACE</code>: tabel vervangen.</li>
</ul>` },
  { sub: "d2.2", title: "Tabellen bekijken", body: `
<ul>
<li><code>DESCRIBE TABLE t</code>: kolommen en types. <code>DESCRIBE TABLE EXTENDED t</code>: ook eigenaar, type (managed/external) en locatie.</li>
<li><code>DESCRIBE DETAIL t</code>: aantal bestanden, grootte, formaat.</li>
<li><code>SHOW TABLES IN catalog.schema</code>: welke tabellen er zijn.</li>
</ul>` }
] },

d3: { sections: [
  { sub: "d3.1", title: "INSERT, UPDATE en DELETE", body: `
<ul>
<li><code>INSERT INTO t VALUES (...)</code> of <code>INSERT INTO t SELECT ...</code>: rijen toevoegen.</li>
<li><code>INSERT OVERWRITE t SELECT ...</code>: de hele inhoud vervangen.</li>
<li><code>UPDATE t SET kolom = ... WHERE ...</code> en <code>DELETE FROM t WHERE ...</code>: dit kan op Delta-tabellen, anders dan bij losse Parquet-bestanden.</li>
<li>Elke wijziging maakt een nieuwe <b>versie</b> van de tabel.</li>
</ul>` },
  { sub: "d3.2", title: "MERGE", body: `
<pre><code>MERGE INTO patienten AS d
USING updates AS u ON d.id = u.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;</code></pre>
<p>Met <code>MERGE</code> werk je bestaande rijen bij en voeg je nieuwe toe in één stap (een "upsert"). Met <code>WHEN MATCHED ... THEN DELETE</code> kun je ook verwijderen.</p>` }
] },

d4: { sections: [
  { sub: "d4.1", title: "Geschiedenis en time travel", body: `
<ul>
<li><code>DESCRIBE HISTORY t</code>: elke versie met tijdstip, gebruiker en bewerking.</li>
<li>Oude versie lezen: <code>SELECT * FROM t VERSION AS OF 3</code> of <code>TIMESTAMP AS OF '2026-11-01'</code>.</li>
</ul>` },
  { sub: "d4.2", title: "Terugzetten en opruimen", body: `
<ul>
<li><code>RESTORE TABLE t TO VERSION AS OF 3</code>: de tabel terugzetten. Ook dat wordt weer een nieuwe versie.</li>
<li><code>VACUUM t</code>: oude bestanden opruimen (standaard ouder dan 7 dagen). Daarna kun je niet meer naar die oude versies terug.</li>
</ul>` }
] },

d5: { sections: [
  { sub: "d5.1", title: "CTAS en uploaden", body: `
<ul>
<li><b>CTAS</b>: <code>CREATE TABLE t AS SELECT * FROM read_files('/Volumes/.../opnames.csv', format =&gt; 'csv', header =&gt; true)</code>. Tabel maken en vullen in één stap; het schema komt uit de query.</li>
<li>Met de <b>upload-knop</b> (Add data) zet je een klein bestand direct in een tabel of een volume, zonder code.</li>
</ul>` },
  { sub: "d5.2", title: "COPY INTO", body: `
<pre><code>COPY INTO bronze_opnames
FROM '/Volumes/main/landing/opnames'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');</code></pre>
<p>COPY INTO laadt bestanden in een bestaande tabel en onthoudt welke al geladen zijn. Draai je hem opnieuw, dan komen alleen de nieuwe bestanden erbij.</p>` }
] },

d6: { sections: [
  { sub: "d6.1", title: "De drie lagen", body: `
<ul>
<li><b>Bronze</b>: ruwe data zoals die binnenkomt, vaak met extra kolommen zoals laadtijd en bestandsnaam.</li>
<li><b>Silver</b>: opgeschoond: juiste types, geen dubbele rijen, ongeldige rijen eruit.</li>
<li><b>Gold</b>: klaar voor gebruik: samengevat per onderwerp, voor rapporten en analyses.</li>
</ul>` },
  { sub: "d6.2", title: "Van laag naar laag", body: `
<ul>
<li>Bronze → silver: <code>cast</code>, <code>to_date</code>, <code>trim</code>, filteren op geldige waarden, ontdubbelen.</li>
<li>Silver → gold: <code>GROUP BY</code> met <code>count</code>, <code>sum</code>, <code>avg</code>; joins met dimensies.</li>
<li>Extra kolommen in bronze: <code>current_timestamp()</code> als laadtijd, <code>_metadata.file_name</code> voor het bronbestand.</li>
</ul>` }
] },

d7: { sections: [
  { sub: "d7.1", title: "Taken en afhankelijkheden", body: `
<ul>
<li>Een <b>job</b> bestaat uit <b>taken</b>, bijv. één notebook per laag: bronze, silver, gold.</li>
<li>Met <b>depends on</b> zet je de volgorde: silver start pas als bronze gelukt is.</li>
<li>Faalt een taak, dan draaien de taken die ervan afhangen niet. Met <b>repair run</b> draai je alleen de mislukte delen opnieuw.</li>
</ul>` },
  { sub: "d7.2", title: "Plannen en bewaken", body: `
<ul>
<li>Een <b>schedule</b> start de job op vaste tijden. Andere triggers: bij nieuwe bestanden, bij een tabelwijziging, of doorlopend.</li>
<li>In de lijst met <b>runs</b> zie je per run en per taak of het lukte en hoe lang het duurde.</li>
<li>Met <b>notificaties</b> krijg je een mail als een run mislukt.</li>
</ul>` }
] },

d8: { sections: [
  { sub: "d8.1", title: "Streaming tables en materialized views", body: `
<p>In een <b>declarative pipeline</b> (Lakeflow Spark Declarative Pipelines) beschrijf je <i>wat</i> er moet ontstaan; Databricks regelt de volgorde en het verversen.</p>
<pre><code>CREATE OR REFRESH STREAMING TABLE bronze_opnames
AS SELECT * FROM STREAM read_files('/Volumes/main/landing/opnames', format =&gt; 'csv');

CREATE OR REFRESH MATERIALIZED VIEW gold_per_afdeling
AS SELECT afdeling, count(*) AS aantal FROM silver_opnames GROUP BY afdeling;</code></pre>
<ul><li><b>Streaming table</b>: verwerkt alleen nieuwe data. <b>Materialized view</b>: opgeslagen uitkomst van een query, die bij elke update wordt bijgewerkt.</li></ul>` },
  { sub: "d8.2", title: "Expectations", body: `
<pre><code>CONSTRAINT geldig_id EXPECT (opname_id IS NOT NULL) ON VIOLATION DROP ROW</code></pre>
<ul><li>Zonder ON VIOLATION worden schendingen alleen geteld; <b>DROP ROW</b> gooit de rij weg; <b>FAIL UPDATE</b> stopt de pipeline.</li></ul>` }
] }
});
