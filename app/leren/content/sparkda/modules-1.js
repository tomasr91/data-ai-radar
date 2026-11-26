/* Associate Developer for Apache Spark: uitleg per onderwerp.
   Onderwerpen volgens de examengids (8 oktober 2026); feiten uit spark.apache.org/docs (26 november 2026). */
Academy.addModules("sparkda", {

d1: { sections: [
  { sub: "d1.1", title: "Driver, executors en cluster", body: `
<ul>
<li>De <b>driver</b> draait je programma, houdt de <code>SparkSession</code> vast, maakt het plan en verdeelt taken.</li>
<li><b>Executors</b> voeren de taken uit en bewaren gecachte data. Elke core draait één taak tegelijk.</li>
<li>De <b>cluster manager</b> (standalone, YARN, Kubernetes) geeft de resources.</li>
<li>Eén taak verwerkt één <b>partitie</b>. Meer partities dan cores = werk in rondes; minder = cores die niets doen.</li>
<li><code>collect()</code> haalt alles naar de driver. Bij grote data: out-of-memory op de driver.</li>
</ul>` },
  { sub: "d1.2", title: "Lazy evaluation, jobs en stages", body: `
<ul>
<li><b>Transformaties</b> (<code>select</code>, <code>filter</code>, <code>groupBy</code>, <code>join</code>) zijn lazy: ze bouwen alleen een plan.</li>
<li><b>Acties</b> (<code>count</code>, <code>show</code>, <code>collect</code>, <code>write</code>) starten het werk.</li>
<li>Hiërarchie: actie → <b>job</b> → <b>stages</b> → <b>tasks</b>. Een nieuwe stage begint bij een <b>shuffle</b>.</li>
<li><b>Narrow</b> (filter, select): geen data tussen executors. <b>Wide</b> (groupBy, join, distinct): shuffle.</li>
<li>De optimizer (<b>Catalyst</b>) herschrijft het plan; <code>df.explain()</code> laat het zien.</li>
</ul>` },
  { sub: "d1.3", title: "Partities, caching en modules", body: `
<ul>
<li>Na een shuffle krijg je <code>spark.sql.shuffle.partitions</code> partities (standaard 200; AQE kan ze samenvoegen).</li>
<li><code>cache()</code> / <code>persist(level)</code> bewaren een DataFrame voor hergebruik. Ook lazy: pas bij de eerste actie gevuld. <code>unpersist()</code> haalt het weg.</li>
<li>Storage levels o.a. <code>MEMORY_ONLY</code>, <code>MEMORY_AND_DISK</code>, <code>DISK_ONLY</code>.</li>
<li>Veel <b>GC time</b> in de Spark UI = geheugendruk op de executors.</li>
<li>Modules: Spark SQL/DataFrames, Pandas API on Spark, Structured Streaming, MLlib (machine learning). Datasets (getypeerd) bestaan in Scala/Java, niet in Python.</li>
</ul>` }
] },

d2: { sections: [
  { sub: "d2.1", title: "Lezen en schrijven", body: `
<pre><code>df = (spark.read.format("csv")
      .option("header", True)
      .schema("id INT, afdeling STRING")
      .load("/data/opnames/"))
df.write.mode("overwrite").partitionBy("jaar").parquet("/out/opnames")</code></pre>
<ul>
<li>Save modes: <code>append</code>, <code>overwrite</code>, <code>ignore</code>, <code>error</code>/<code>errorifexists</code> (standaard).</li>
<li><code>partitionBy("kol")</code> maakt een map per waarde.</li>
<li>JDBC: <code>format("jdbc")</code> met opties <code>url</code> en <code>dbtable</code>.</li>
<li>SQL direct op bestanden: <code>SELECT * FROM json.\`/pad/\`</code> (ook <code>csv</code>, <code>parquet</code>, <code>orc</code>, <code>text</code>, <code>delta</code>).</li>
<li>JSON verwacht standaard één object per regel; anders <code>option("multiLine", True)</code>.</li>
</ul>` },
  { sub: "d2.2", title: "Tabellen en temp views", body: `
<ul>
<li><code>df.createOrReplaceTempView("v")</code> + <code>spark.sql("SELECT ... FROM v")</code>. Een temp view leeft zolang de SparkSession.</li>
<li>Global temp view: <code>createGlobalTempView</code>, lees je via <code>global_temp.v</code>.</li>
<li><code>df.write.saveAsTable("t")</code> maakt een blijvende tabel; <code>spark.table("t")</code> leest hem.</li>
<li><code>bucketBy</code> en <code>sortBy</code> werken alleen samen met <code>saveAsTable</code>.</li>
<li><code>insertInto</code> koppelt op <b>positie</b>, niet op kolomnaam.</li>
</ul>` }
] },

d3: { sections: [
  { sub: "d3.1", title: "Kolommen en rijen", body: `
<pre><code>from pyspark.sql import functions as F
df = (df.withColumn("jaar", F.year("opname_dt"))
        .withColumnRenamed("afd", "afdeling")
        .drop("tmp")
        .filter(F.col("leeftijd") &gt;= 18)
        .withColumn("codes", F.split("codes_txt", ","))
        .withColumn("code", F.explode("codes")))</code></pre>
<ul>
<li><code>explode</code> laat rijen met een lege of NULL-array weg; <code>explode_outer</code> houdt ze.</li>
<li>Ontdubbelen: <code>distinct()</code> (hele rij) of <code>dropDuplicates(["id"])</code> (op kolommen).</li>
<li>NULLs: <code>dropna()</code> / <code>fillna()</code> (ook <code>df.na.drop()</code>, <code>df.na.fill()</code>).</li>
</ul>` },
  { sub: "d3.2", title: "Aggregaties en datums", body: `
<ul>
<li><code>df.groupBy("afdeling").agg(F.count("*").alias("n"), F.avg("ligduur"))</code></li>
<li><code>countDistinct</code> is exact; <code>approx_count_distinct</code> is sneller en bij benadering.</li>
<li><code>describe()</code>: count, mean, stddev, min, max. <code>summary()</code> voegt percentielen toe.</li>
<li>Epoch naar tijd: <code>F.from_unixtime("epoch")</code> of <code>F.timestamp_seconds("epoch")</code>. Delen: <code>year</code>, <code>month</code>, <code>dayofweek</code>.</li>
<li>Tekst naar datum: <code>F.to_date("dt", "dd-MM-yyyy")</code>.</li>
</ul>` },
  { sub: "d3.3", title: "Joins en unions", body: `
<ul>
<li><code>a.join(b, "id", "left")</code>; standaard is <code>inner</code>. Meerdere sleutels: <code>["id", "datum"]</code>.</li>
<li><code>left_anti</code>: rijen uit links zonder match. <code>crossJoin</code>: elke combinatie.</li>
<li><code>F.broadcast(klein)</code>: kleine tabel naar elke executor, geen shuffle van de grote.</li>
<li><code>union</code> koppelt op positie en ontdubbelt niet (zoals UNION ALL). <code>unionByName</code> koppelt op naam.</li>
</ul>` },
  { sub: "d3.4", title: "UDF's en broadcast", body: `
<ul>
<li>Python-UDF: <code>F.udf(func, "string")</code>. Traag(er): rijen gaan naar Python en Catalyst kan er niet in kijken. Kies eerst ingebouwde functies.</li>
<li>Voor SQL: <code>spark.udf.register("naam", func, "string")</code>.</li>
<li><b>Broadcast variable</b>: alleen-lezen kopie per executor (<code>spark.sparkContext.broadcast(dict)</code>).</li>
<li><b>Accumulator</b>: executors tellen op, de driver leest de waarde.</li>
<li>Streaming-aggregaties bewaren hun tussenstand in een <b>state store</b>.</li>
</ul>` }
] },

d4: { sections: [
  { sub: "d4.1", title: "Partitioneren, skew en shuffles", body: `
<ul>
<li><code>repartition(n)</code>: volledige shuffle, kan meer of minder. <code>coalesce(n)</code>: alleen minder, zonder volledige shuffle.</li>
<li><b>Skew</b>: één sleutel heeft veel meer rijen; één taak duurt veel langer dan de rest.</li>
<li>Minder shuffle: vroeg filteren, alleen nodige kolommen, kleine tabel broadcasten.</li>
<li>Veel kleine bestanden bij schrijven: vooraf <code>coalesce</code>.</li>
</ul>` },
  { sub: "d4.2", title: "AQE en logs", body: `
<ul>
<li><b>Adaptive Query Execution</b> past het plan tijdens het draaien aan op basis van echte statistieken (standaard aan sinds Spark 3.2).</li>
<li>AQE kan: shuffle-partities samenvoegen, naar een broadcast join wisselen, skew joins opsplitsen.</li>
<li>Logs: Spark UI → tab <b>Executors</b> → stdout/stderr per executor. Ook driverlogs.</li>
<li>Driver OOM: vaak <code>collect()</code>/<code>toPandas()</code> op grote data. Executor OOM: te grote partities of skew.</li>
</ul>` }
] },

d5: { sections: [
  { sub: "d5.1", title: "Model en garanties", body: `
<ul>
<li>Een stream is een <b>tabel die steeds groeit</b>; je schrijft gewone DataFrame-code.</li>
<li>Standaard <b>micro-batches</b>: de volgende batch start zodra de vorige klaar is. <code>trigger(availableNow=True)</code> verwerkt wat er is en stopt.</li>
<li><b>Checkpoint</b> (<code>checkpointLocation</code>) bewaart offsets en state. Met een herspeelbare bron en idempotente sink: <b>exactly-once</b>.</li>
</ul>` },
  { sub: "d5.2", title: "Output, windows en watermarks", body: `
<pre><code>(spark.readStream.format("json").schema(s).load("/in")
   .withWatermark("tijd", "10 minutes")
   .groupBy(F.window("tijd", "5 minutes")).count()
   .writeStream.outputMode("append")
   .option("checkpointLocation", "/chk").start("/out"))</code></pre>
<ul>
<li>Output modes: <code>append</code> (alleen nieuwe rijen), <code>complete</code> (hele resultaat), <code>update</code> (alleen gewijzigde rijen).</li>
<li><b>Watermark</b>: hoe lang je op late data wacht; oudere state mag weg.</li>
<li><code>dropDuplicates</code> zonder watermark houdt alle sleutels bij: state blijft groeien.</li>
</ul>` }
] },

d6: { sections: [
  { sub: "d6.1", title: "Spark Connect en deploy-modi", body: `
<ul>
<li><b>Spark Connect</b>: dunne client stuurt (onopgeloste) plannen via gRPC naar een Spark-server. <code>SparkSession.builder.remote("sc://host:15002")</code>.</li>
<li>Voordelen: client los te upgraden, client-crash raakt de server niet, werken vanuit je IDE. Geen RDD's of <code>sparkContext</code> via Connect.</li>
<li><b>Client mode</b>: driver op de machine die het werk indient. <b>Cluster mode</b>: driver binnen het cluster. <b>Local mode</b>: alles in één proces op één machine (<code>local[*]</code>).</li>
</ul>` }
] },

d7: { sections: [
  { sub: "d7.1", title: "Pandas API en Pandas UDF's", body: `
<ul>
<li><code>import pyspark.pandas as ps</code>: pandas-syntax, maar verdeeld over het cluster.</li>
<li>Wisselen: <code>sdf.pandas_api()</code> en <code>psdf.to_spark()</code>.</li>
<li><code>toPandas()</code> haalt alles naar de driver: alleen voor kleine data.</li>
<li><b>Pandas UDF</b> (<code>@F.pandas_udf("double")</code>, <code>pd.Series → pd.Series</code>): werkt per batch via Arrow, sneller dan een gewone Python-UDF.</li>
</ul>` }
] }

});
