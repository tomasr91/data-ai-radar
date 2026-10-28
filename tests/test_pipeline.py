"""Tests voor de pipeline. Draaien: python -m unittest discover -s tests -v"""
import json
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from pipeline import build as build_mod
from pipeline import config as cfg
from pipeline import enrich
from pipeline.dedupe import dedupe
from pipeline.normalize import canonical_url, normalize, parse_date
from pipeline.providers import ProviderResult, feeds
from pipeline.score import score_article

NOW = datetime(2026, 10, 28, 20, 0, tzinfo=timezone.utc)
F = "2026-10-28T19:00:00Z"

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Unity Catalog lineage and data quality checks</title><link>https://example.org/a?utm_source=x</link>
<pubDate>Tue, 27 Oct 2026 18:00:00 GMT</pubDate><description>&lt;p&gt;dbt tests and data lineage&lt;/p&gt;</description></item>
<item><title>No link item</title></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>t</title>
<entry><title>RAG evaluation for AI agents</title><link rel="alternate" href="https://example.org/b"/>
<published>2026-10-20T10:00:00+02:00</published><summary>retrieval augmented generation</summary></entry></feed>"""


def conf_with(sources):
    c = cfg.load()
    c.sources = {"sources": sources}
    return c


def src(id_, method="rss", **kw):
    base = {"id": id_, "name": id_, "url": f"https://example.org/{id_}", "feed_url": f"https://example.org/{id_}.xml",
            "type": "vendor_blog", "topics": [], "priority": 5, "enabled": True, "trust_level": "high",
            "language": "en", "fetch_method": method, "verification": {"status": "verified"}}
    base.update(kw)
    return base


def raw(source_id, title, url, pub="Tue, 27 Oct 2026 18:00:00 GMT", excerpt=""):
    return {"source_id": source_id, "title": title, "url": url, "published_raw": pub, "fetched_at": F, "excerpt": excerpt}


class TestFetching(unittest.TestCase):
    def test_parse_rss_and_atom(self):
        items = feeds.parse_feed(RSS, "s", F)
        self.assertEqual(len(items), 1, "item zonder link wordt overgeslagen")
        self.assertEqual(items[0]["published_raw"], "Tue, 27 Oct 2026 18:00:00 GMT")
        atom = feeds.parse_feed(ATOM, "s", F)
        self.assertEqual(atom[0]["url"], "https://example.org/b")

    def test_invalid_xml_raises_value_error(self):
        with self.assertRaises(ValueError):
            feeds.parse_feed(b"<html><body>not a feed", "s", F)

    def test_failing_source_does_not_block_others(self):
        def getter(url):
            if "down" in url:
                raise urllib.error.URLError("connection refused")
            if "broken" in url:
                return b"<oops"
            return RSS
        c = conf_with([src("down"), src("broken"), src("good"), src("page", method="html"),
                       src("man", method="manual"), src("off", enabled=False)])
        res = feeds.collect(c, getter=getter)
        status = {r["source_id"]: r["status"] for r in res.source_results}
        self.assertEqual(status, {"down": "failed", "broken": "failed", "good": "ok",
                                  "page": "not_supported", "man": "skipped"})
        self.assertEqual(res.mode, "partial")
        self.assertEqual({i["source_id"] for i in res.items}, {"good"})

    def test_all_failed_mode(self):
        def getter(url):
            raise urllib.error.URLError("offline")
        res = feeds.collect(conf_with([src("a"), src("b")]), getter=getter)
        self.assertEqual(res.mode, "failed")

    def test_github_releases_url(self):
        self.assertEqual(feeds.feed_url_for(src("g", "github_releases", url="https://github.com/dbt-labs/dbt-core/releases")),
                         "https://github.com/dbt-labs/dbt-core/releases.atom")


class TestNormalize(unittest.TestCase):
    def test_dates(self):
        self.assertEqual(parse_date("Tue, 27 Oct 2026 18:00:00 GMT"), "2026-10-27T18:00:00Z")
        self.assertEqual(parse_date("2026-10-20T10:00:00+02:00"), "2026-10-20T08:00:00Z")
        self.assertEqual(parse_date("2026-10-15"), "2026-10-15T00:00:00Z")
        self.assertIsNone(parse_date("6 days ago"))
        self.assertIsNone(parse_date(None))

    def test_no_fallback_to_fetch_date(self):
        a = normalize(raw("s", "t", "https://example.org/x", pub=None))
        self.assertIsNone(a["published_at"])
        self.assertEqual(a["fetched_at"], F)

    def test_canonical_url(self):
        self.assertEqual(canonical_url("http://WWW.Example.org/a/?utm_source=x&id=1"), "https://example.org/a?id=1")
        self.assertEqual(canonical_url("https://learn.microsoft.com/en-us/azure/x"),
                         canonical_url("https://learn.microsoft.com/nl-nl/azure/x"))
        self.assertNotEqual(canonical_url("https://e.org/p#a"), canonical_url("https://e.org/p#b"))


class TestDedupe(unittest.TestCase):
    sources = {"official": {"trust_level": "high", "priority": 5}, "news": {"trust_level": "medium", "priority": 3}}

    def test_same_url_and_similar_title_and_development(self):
        arts = [normalize(x) for x in [
            raw("news", "Databricks adds governed tag propagation", "https://example.org/a?utm_source=feed"),
            raw("official", "Governed tag propagation in Beta", "https://example.org/a"),
            raw("official", "Lakeflow connector for Asana now available", "https://example.org/c"),
            raw("news", "Lakeflow connector for Asana now available!", "https://other.org/c"),
            raw("official", "Data Classification API GA", "https://example.org/d"),
            raw("official", "Data Classification adds 50 classes", "https://example.org/e"),
            raw("official", "Something unrelated", "https://example.org/f"),
        ]]
        arts[4]["development_key"] = arts[5]["development_key"] = "dc"
        kept, merged = dedupe(arts, self.sources)
        self.assertEqual(merged, 3)
        self.assertEqual(len(kept), 4)
        primary = next(a for a in kept if a["canonical_url"] == "https://example.org/a")
        self.assertEqual(primary["source_id"], "official", "bron met hoogste trust blijft hoofdartikel")
        self.assertEqual(primary["also_reported_by"][0]["source_id"], "news")


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.conf = conf_with([src("official")])

    def _scored(self, title, excerpt="", **extra):
        a = normalize(raw("official", title, "https://example.org/" + str(abs(hash(title))), excerpt=excerpt))
        a["processing_status"] = "raw"
        a.update(extra)
        return score_article(a, self.conf, NOW)

    def test_excluded_topic_always_out(self):
        a = self._scored("dbt startup raises Series B funding round", exceptional=True)
        self.assertEqual(a["decision"], "excluded")

    def test_no_topic(self):
        self.assertEqual(self._scored("Game Boy Color on my badge")["decision"], "no_topic")

    def test_single_generic_keyword_is_weak(self):
        weak = self._scored("How to teach with Databricks Free Edition")
        strong = self._scored("Unity Catalog lineage with dbt tests", "data lineage and data quality in dbt")
        self.assertEqual(weak["decision"], "below_threshold")
        self.assertEqual(strong["decision"], "included")
        self.assertGreater(strong["relevance_score"], weak["relevance_score"])

    def test_high_priority_does_not_guarantee_inclusion(self):
        a = self._scored("dbt", published_raw=None)
        self.assertEqual(a["topics"][0], "dbt_analytics_engineering")
        self.assertNotEqual(a["decision"], "included")

    def test_spelling_variants_match(self):
        a = self._scored("dbt_context_engineering: modeling the context your AI agents read",
                         "dbt-context-engineering is a new package that helps you create AI ready data")
        self.assertIn("ai_context_engineering", a["topics"])
        self.assertEqual(a["decision"], "included")

    def test_exceptional_override_only_for_low_priority(self):
        low = self._scored("AI industry news", exceptional=True)
        self.assertEqual(low["decision"], "included_exceptional")
        high = self._scored("dbt", exceptional=True)
        self.assertEqual(high["decision"], "below_threshold")


class TestEnrichment(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._cache = enrich.CACHE
        enrich.CACHE = Path(self.tmp.name)
        self.topics = set(cfg.load().topics)

    def tearDown(self):
        enrich.CACHE = self._cache
        self.tmp.cleanup()

    def _art(self, i):
        a = normalize(raw("official", f"Article {i}", f"https://example.org/{i}"))
        a["processing_status"] = "raw"
        return a

    def test_without_api_key_nothing_breaks(self):
        arts = [self._art(1), self._art(2)]
        rep = enrich.enrich_new(arts, self.topics, 5, api_key="")
        self.assertFalse(rep["api_key_present"])
        self.assertEqual(rep["skipped_no_key"], 2)
        self.assertTrue(all(a["processing_status"] == "raw" for a in arts))

    def test_invalid_output_is_reported_and_run_continues(self):
        good = {"summary": "s", "what_is_new": "n", "personal_relevance": "r", "availability_status": "preview",
                "limitations": [], "topics": ["dbt_analytics_engineering"],
                "quality": {"depth": 0.5, "practicality": 0.5, "novelty": 0.5}}

        def caller(article, topic_ids, key):
            if article["title"].endswith("1"):
                return {"summary": "only a summary"}
            if article["title"].endswith("2"):
                raise TimeoutError("api timeout")
            return dict(good)
        arts = [self._art(1), self._art(2), self._art(3)]
        rep = enrich.enrich_new(arts, self.topics, 5, api_key="test", caller=caller)
        self.assertEqual(rep["processed"], 1)
        self.assertEqual(len(rep["failed"]), 2)
        self.assertEqual(arts[2]["processing_status"], "enriched")
        self.assertTrue((enrich.CACHE / f"{arts[2]['id']}.json").exists(), "verrijking wordt gecachet")

    def test_cache_is_reused(self):
        calls = []

        def caller(article, topic_ids, key):
            calls.append(1)
            return {"summary": "s", "what_is_new": "n", "personal_relevance": "r", "availability_status": "onbekend",
                    "limitations": [], "topics": [], "quality": {"depth": 0, "practicality": 0, "novelty": 0}}
        a = self._art(9)
        enrich.enrich_new([a], self.topics, 5, api_key="k", caller=caller)
        b = self._art(9)
        cached = enrich.load_cached(b["id"])
        enrich.attach(b, cached)
        enrich.enrich_new([b], self.topics, 5, api_key="k", caller=caller)
        self.assertEqual(len(calls), 1)


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._data, self._cache = cfg.DATA, enrich.CACHE
        cfg.DATA = Path(self.tmp.name)
        enrich.CACHE = Path(self.tmp.name) / "enrichment"
        self.out = Path(self.tmp.name) / "feed.json"

    def tearDown(self):
        cfg.DATA, enrich.CACHE = self._data, self._cache
        self.tmp.cleanup()

    def _provider(self, items, mode="partial"):
        return lambda c: ProviderResult(items=items, source_results=[{"source_id": "dbt_labs_blog", "status": "ok", "items": len(items), "message": "", "checked_at": F}], mode=mode)

    def test_end_to_end_without_key(self):
        items = [raw("dbt_labs_blog", "dbt tests for data quality and lineage", "https://example.org/1",
                     excerpt="dbt tests, data lineage, semantic layer"),
                 raw("databricks_blog", "dbt tests for data quality and lineage!", "https://example.org/1?utm_source=rss",
                     excerpt="dbt tests, data lineage, semantic layer")]
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider(items), now=NOW)
        self.assertEqual(len(feed["articles"]), 1, "dubbel artikel één keer getoond")
        self.assertEqual(feed["quality_report"]["merged_duplicates"], 1)
        self.assertEqual(feed["articles"][0]["processing_status"], "raw")
        self.assertTrue(list((cfg.DATA / "raw").glob("*.json")), "ruwe laag wordt bewaard")

    def test_archive_keeps_articles_that_left_the_feed(self):
        item = raw("dbt_labs_blog", "dbt tests for data quality and lineage", "https://example.org/1",
                   excerpt="dbt tests, data lineage, semantic layer")
        build_mod.build("feeds", self.out, provider_fn=self._provider([item]), now=NOW)
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider([]), now=NOW)
        self.assertEqual(len(feed["articles"]), 1, "artikel blijft staan als de bronfeed het niet meer toont")

    def test_invalid_cache_ignored_and_skipped_not_queued(self):
        item = raw("dbt_labs_blog", "dbt tests for data quality and lineage", "https://example.org/1",
                   excerpt="dbt tests, data lineage, semantic layer")
        aid = normalize(item)["id"]
        enrich.CACHE.mkdir(parents=True)
        (enrich.CACHE / f"{aid}.json").write_text(json.dumps({"summary": "half bestand"}))
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider([item]), now=NOW)
        self.assertEqual(feed["articles"][0]["processing_status"], "raw")
        self.assertEqual(feed["quality_report"]["invalid_enrichment"][0]["id"], aid)
        queue = json.loads((cfg.DATA / "to_enrich.json").read_text())
        self.assertEqual([i["id"] for i in queue["items"]], [aid], "onverwerkt artikel staat op de werklijst")
        (enrich.CACHE / f"{aid}.json").unlink()
        (enrich.CACHE / "skipped").mkdir()
        (enrich.CACHE / "skipped" / f"{aid}.json").write_text(json.dumps({"reason": "pagina onleesbaar"}))
        build_mod.build("feeds", self.out, provider_fn=self._provider([item]), now=NOW)
        queue = json.loads((cfg.DATA / "to_enrich.json").read_text())
        self.assertEqual(queue["items"], [], "overgeslagen artikel komt niet terug")

    def test_removed_source_disappears_from_feed(self):
        items = [raw("dbt_labs_blog", "dbt tests for data quality and lineage", "https://example.org/1",
                     excerpt="dbt tests, data lineage, semantic layer"),
                 raw("verwijderde_bron", "dbt tests and data lineage elsewhere", "https://example.org/2",
                     excerpt="dbt tests, data lineage, semantic layer")]
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider(items), now=NOW)
        self.assertEqual({a["source_id"] for a in feed["articles"]}, {"dbt_labs_blog"})

    def test_failed_fetch_keeps_previous_feed(self):
        self.out.write_text(json.dumps({"mode": "live", "articles": [{"id": "x"}], "sources": []}))
        failing = lambda c: ProviderResult(items=[], source_results=[], mode="failed", note="offline")
        feed = build_mod.build("feeds", self.out, provider_fn=failing, now=NOW)
        self.assertEqual(feed["mode"], "stale")
        self.assertEqual(feed["articles"], [{"id": "x"}])


class TestPublishedFeed(unittest.TestCase):
    """Controleert het feed.json dat de app leest."""

    def test_feed_contract(self):
        path = cfg.ROOT / "data" / "feed.json"
        if not path.exists():
            self.skipTest("nog geen feed gebouwd")
        f = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(f["mode"], {"live", "partial", "snapshot", "demo", "stale"})
        ids = [a["id"] for a in f["articles"]]
        self.assertEqual(len(ids), len(set(ids)), "geen dubbele artikelen")
        group_ids = {g["id"] for g in f["groups"]}
        source_ids = {s["id"] for s in f["sources"]}
        for a in f["articles"]:
            self.assertTrue(a["url"].startswith("https://"), a["url"])
            self.assertIn(a["source_id"], source_ids)
            self.assertTrue(set(a["groups"]) <= group_ids)
            self.assertIn("fetched_at", a)
            if a["processing_status"] == "enriched":
                needed = (["headline", "summary", "story", "key_facts", "availability_status"] if a.get("format_version") == 2
                          else ["summary", "what_is_new", "personal_relevance", "availability_status"])
                for k in needed:
                    self.assertIn(k, a, f"{a['title']}: {k}")
        self.assertTrue(set(f["daily_top"]) <= set(ids))
        self.assertLessEqual(len(f["daily_top"]), 5)


if __name__ == "__main__":
    unittest.main()
