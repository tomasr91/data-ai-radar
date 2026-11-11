"""Tests voor de pipeline. Draaien: python -m unittest discover -s tests -v"""
import json
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import build as build_mod
from pipeline import config as cfg
from pipeline import enrich
from pipeline.dedupe import dedupe
from pipeline.normalize import canonical_url, normalize, parse_date
from pipeline.providers import ProviderResult, feeds
from pipeline.score import excluded_by, score_article

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

    def test_opinion_needs_author(self):
        base = {"format_version": 2, "headline": "Kop", "summary": "s", "personal_relevance": "r",
                "experiment": "e", "story": ["a", "b", "c"], "key_facts": ["Auteur stelt X."],
                "availability_status": "onbekend", "limitations": [], "topics": ["dbt_analytics_engineering"],
                "quality": {"depth": 0.5, "practicality": 0.5, "novelty": 0.5}}
        self.assertEqual(enrich.validate(base, self.topics), [])
        self.assertTrue(enrich.validate({**base, "article_type": "opinie"}, self.topics))
        self.assertEqual(enrich.validate({**base, "article_type": "opinie", "author": "Benn Stancil, oprichter van Mode"}, self.topics), [])
        self.assertTrue(enrich.validate({**base, "article_type": "column"}, self.topics))

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


class TestExclusions(unittest.TestCase):
    """Regels uit interests.yml: geen connectoren, geen patches/dev-builds, geen maandoverzichten."""

    def test_title_patterns(self):
        conf = cfg.load()
        cases = {
            "QuickBooks connector is available in Beta": True,
            "Box Audit Logs managed ingestion connector (Beta)": True,
            "Databricks ADBC connector for Power BI and Microsoft Fabric (Generally Available)": False,
            "dbt v1.12.6": True, "v2.0.3": True, "v2.0.0-dev.41-test-pypi": True,
            "dbt v1.13.0b1": False, "dbt v2.0 is GA": False, "dbt v1.13.0": False,
            "Power BI October 2026 Feature Summary": True,
            "Genie agentic capabilities are now processed in South Korea": True,
        }
        for title, expected in cases.items():
            self.assertEqual(bool(excluded_by(title, title, conf.excluded_topics)), expected, title)

    def test_technical_words_are_not_funding_news(self):
        conf = cfg.load()
        text = "dbt v1.13.0b1 raises an error on duplicate keys; data acquisition pipelines"
        self.assertEqual(excluded_by("dbt v1.13.0b1", text, conf.excluded_topics), [])


class TestWeeklyDigest(unittest.TestCase):
    """Claude Code: losse patchreleases eruit, één overzicht per afgeronde week erin."""

    def test_one_digest_per_completed_week(self):
        from pipeline.digest import weekly_digests
        conf = cfg.load()
        rel = lambda v, d: {"source_id": "claude_code_releases", "title": v, "fetched_at": F,
                            "url": f"https://github.com/anthropics/claude-code/releases/tag/{v}",
                            "published_raw": d, "excerpt": "<ul><li>Added something</li></ul>"}
        items = [rel("v2.1.310", "2026-10-23T23:39:00Z"), rel("v2.1.304", "2026-10-19T21:34:39Z"),
                 rel("v2.1.311", "2026-10-26T21:51:23Z")]  # week 44 loopt nog: geen overzicht
        now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        out = weekly_digests(items, conf, now)
        self.assertEqual(len(out), 1)
        d = out[0]
        self.assertIn("week 43", d["title"])
        self.assertIn("v2.1.304 t/m v2.1.310", d["title"])
        self.assertEqual(excluded_by(d["title"], d["title"], conf.excluded_topics), [])
        self.assertTrue(all(excluded_by(i["title"], i["title"], conf.excluded_topics) for i in items))
        a = score_article(normalize(d) | {"processing_status": "raw"}, conf, now)
        self.assertIn("claude_ai_development", a["topics"])
        self.assertGreaterEqual(a["relevance_score"], build_mod.QUEUE_MIN_SCORE)


class TestAzureDigestAndSourceCap(unittest.TestCase):
    """Azure release notes: losse notes eruit, één weekoverzicht erin; maximum per bron."""

    def test_azure_notes_become_weekly_digest(self):
        from pipeline.digest import weekly_digests
        conf = cfg.load()
        note = lambda t, d, u: {"source_id": "azure_databricks_release_notes", "title": t, "fetched_at": F,
                                "url": f"https://learn.microsoft.com/en-us/azure/databricks/release-notes/{u}",
                                "published_raw": d, "excerpt": "Lakeflow Spark Declarative Pipelines Unity Catalog"}
        items = [note("Multiple flows per pipeline are in beta", "Wed, 21 Oct 2026 00:00:00 GMT", "product#a"),
                 note("Multiple flows per pipeline are in beta", "Wed, 21 Oct 2026 00:00:00 GMT", "platform#a"),
                 note("Unity Catalog API change", "Thu, 22 Oct 2026 00:00:00 GMT", "product#b")]
        now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        out = weekly_digests(items, conf, now)
        self.assertEqual(len(out), 1)
        d = out[0]
        self.assertEqual(d["title"], "Azure Databricks: wat is er nieuw in week 43")
        self.assertIn("2 release notes", d["excerpt"])      # dubbele note telt één keer
        dig = score_article(normalize(d) | {"processing_status": "raw"}, conf, now)
        self.assertNotIn("weekoverzicht", dig["excluded_by"])
        loose = score_article(normalize(items[2]) | {"processing_status": "raw"}, conf, now)
        self.assertEqual(loose["decision"], "excluded")
        self.assertIn("weekoverzicht", loose["excluded_by"])

    def test_cap_is_configured(self):
        self.assertGreaterEqual(cfg.load().scoring.get("max_articles_per_source", 0), 5)
        self.assertGreaterEqual(cfg.load().scoring.get("max_articles_per_source_per_day", 0), 2)


class TestWeeklyAndReads(unittest.TestCase):
    """Jouw week (zondag) en gelezen artikelen als licht signaal."""

    def test_weekly_validates_and_drops_missing_links(self):
        import tempfile
        from pathlib import Path
        from pipeline import weekly
        good = {"week": "2026-W44", "generated_at": "2026-11-01T04:40:00Z", "intro": "Rustige week.",
                "highlights": [{"title": "Metric views", "why": "Twee zinnen.", "article_ids": ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]}]}
        self.assertEqual(weekly.validate(good), [])
        self.assertTrue(weekly.validate({**good, "week": "week 44"}))
        self.assertTrue(weekly.validate({**good, "highlights": []}))
        self.assertTrue(weekly.validate({**good, "highlights": good["highlights"] * 4}))
        p = Path(tempfile.mkdtemp()) / "weekly.json"
        p.write_text(json.dumps(good), encoding="utf-8")
        out, problems = weekly.load([{"id": "aaaaaaaaaaaa"}], p)
        self.assertEqual(problems, [])
        self.assertEqual(out["highlights"][0]["article_ids"], ["aaaaaaaaaaaa"])

    def test_reads_count_lightly_and_votes_win(self):
        from pipeline import feedback
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        at = "2026-10-31T10:00:00Z"
        data = {"votes": {}, "reads": {"aaaaaaaaaaaa": {"at": at, "topics": ["dbt_analytics_engineering"], "source_id": "dbt_labs_blog"}}}
        light = feedback.preferences(data, now)["topics"]["dbt_analytics_engineering"]
        data["votes"]["bbbbbbbbbbbb"] = {"v": 1, "at": at, "topics": ["dbt_analytics_engineering"], "source_id": "dbt_labs_blog"}
        full = feedback.preferences({"votes": data["votes"], "reads": {}}, now)["topics"]["dbt_analytics_engineering"]
        self.assertTrue(0 < light < full)
        # duim omhoog telt dubbel zo zwaar als duim omlaag
        down = feedback.preferences({"votes": {"cccccccccccc": {"v": -1, "r": "geen_interesse", "at": at, "topics": ["dbt_analytics_engineering"]}}, "reads": {}}, now)["topics"]["dbt_analytics_engineering"]
        self.assertGreater(full, -down)
        # gelezen én duim omlaag: alleen de duim telt
        data2 = {"votes": {"aaaaaaaaaaaa": {"v": -1, "r": "niet_mijn_stack", "at": at, "topics": ["dbt_analytics_engineering"]}}, "reads": data["reads"]}
        self.assertLess(feedback.preferences(data2, now)["topics"]["dbt_analytics_engineering"], 0)

    def test_parse_reads_from_issue(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import collect_feedback as cf
        body = 'x\n```json\n{"votes": [], "reads": ["aaaaaaaaaaaa", "kapot", "aaaaaaaaaaaa"]}\n```'
        self.assertEqual(cf.parse_reads(body), ["aaaaaaaaaaaa"])


class TestTerms(unittest.TestCase):
    """Begrippen: moeten letterlijk in de tekst staan; woordenlijst voegt samen."""

    def test_validate_terms(self):
        from pipeline.terms import validate_terms
        text = "Auto Loader leest nieuwe bestanden. Met CDC zie je wijzigingen."
        ok = [{"term": "Auto Loader", "explanation": "Leest nieuwe bestanden in."}, {"term": "cdc", "explanation": "Wijzigingen."}]
        self.assertEqual(validate_terms(ok, text), [])
        self.assertTrue(validate_terms([{"term": "Loader leest x", "explanation": "x"}], text))   # staat er niet
        self.assertTrue(validate_terms([{"term": "Load", "explanation": "x"}], text))            # alleen als los woord
        self.assertTrue(validate_terms(ok + ok, text))                                          # dubbel
        self.assertTrue(validate_terms([{"term": "CDC", "explanation": "x" * 300}], text))       # te lang
        self.assertEqual(validate_terms(None, text), [])

    def test_glossary_merges_newest_first(self):
        from pipeline.terms import glossary
        arts = [{"id": "a1", "headline": "Oud", "processed_at": "2026-10-01T00:00:00Z", "terms": [{"term": "CDC", "explanation": "oud"}]},
                {"id": "a2", "headline": "Nieuw", "processed_at": "2026-10-30T00:00:00Z", "terms": [{"term": "cdc", "explanation": "nieuw"}]}]
        dds = [{"id": "d1", "headline": "Verdieping", "written_at": "2026-10-15T00:00:00Z", "terms": [{"term": "ADBC", "explanation": "driver"}]}]
        g = glossary(arts, dds)
        self.assertEqual([t["term"] for t in g], ["ADBC", "cdc"])
        self.assertEqual(g[1]["explanation"], "nieuw")
        self.assertEqual([r["id"] for r in g[1]["refs"]], ["a2", "a1"])


class TestFeedbackRelative(unittest.TestCase):
    """Feedback telt relatief: boven gemiddeld omhoog, de rest omlaag; hooguit 15 punten."""

    def test_offset_centres_effect(self):
        from pipeline import feedback
        conf = cfg.load()
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        prefs = {"topics": {"dbt_analytics_engineering": 1.0}, "sources": {}}
        base = {"title": "x", "url": "https://x", "source_id": "dbt_labs_blog", "published_at": "2026-10-31T00:00:00Z",
                "processing_status": "enriched", "quality": {"depth": .7, "practicality": .7, "novelty": .7}}
        prefs["topics"]["ai_agents_rag"] = 0.0
        arts = [dict(base, id="a", topics=["dbt_analytics_engineering"]), dict(base, id="b", topics=["ai_agents_rag"]),
                dict(base, id="c", topics=["sql_spark_sql"], source_id="sqlbi")]
        prefs["offset"] = feedback.mean_factor(arts, prefs)
        self.assertAlmostEqual(prefs["offset"], 0.5)          # c telt niet mee: daar gaf je geen feedback over
        a = score_article(dict(arts[0]), conf, now, prefs)
        b = score_article(dict(arts[1]), conf, now, prefs)
        c = score_article(dict(arts[2]), conf, now, prefs)
        self.assertGreater(a["score_parts"]["feedback"], 0)
        self.assertLess(b["score_parts"]["feedback"], 0)
        self.assertNotIn("feedback", c["score_parts"])        # geen feedback = geen duw omlaag
        self.assertEqual(feedback.WEIGHT, 0.15)
        self.assertTrue({"praktisch", "goed_uitgelegd", "nieuw_voor_mij", "mijn_stack", "meer_hiervan"} <= feedback.REASONS)


class TestInterests(unittest.TestCase):
    """Mijn interesses: weergave, voorstellen en verzoeken uit issues."""

    def test_view_and_suggestions(self):
        from pipeline import interests
        conf = cfg.load()
        v = interests.view(conf)
        self.assertEqual({a["id"] for a in v["areas"]}, {"data_engineering", "context_agents", "claude", "new_tech"})
        self.assertTrue(all(t["area"] != "overig" for t in v["topics"]))
        self.assertTrue(any(t.get("learning") for t in v["topics"]))
        ok = {"generated_at": "2026-11-08T04:40:00Z", "suggestions": [
            {"id": "data-contracts", "kind": "nieuw", "name": "Data contracts", "description": "x", "why": "y"},
            {"id": "pbi", "kind": "belangrijker", "topic": "powerbi_semantic_models", "why": "y"}]}
        self.assertEqual(interests.validate_suggestions(ok, set(conf.topics)), [])
        bad = {"generated_at": "2026-11-08T04:40:00Z", "suggestions": [{"id": "x", "kind": "weg", "topic": "bestaat_niet", "why": "y"}] * 4}
        self.assertTrue(interests.validate_suggestions(bad, set(conf.topics)))

    def test_interests_in_feedback_issue(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import collect_feedback as cf
        body = 'x\n```json\n{"votes": [], "reads": [], "interests": {"answers": [{"id": "data-contracts", "a": "ja"}], "changes": [{"topic": "sql_spark_sql", "c": "leren"}], "note": ""}}\n```'
        self.assertEqual(cf.parse_interests(body), {"answers": [{"id": "data-contracts", "a": "ja"}], "changes": [{"topic": "sql_spark_sql", "c": "leren"}], "note": ""})
        self.assertIsNone(cf.parse_interests('x\n```json\n{"votes": []}\n```'))

    def test_requests_only_owner(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import interest_requests as ir
        body = 'x\n```json\n{"answers": [{"id": "data-contracts", "a": "ja"}, {"id": "x", "a": "misschien"}], "changes": [{"topic": "open_source_tools", "c": "minder"}, {"topic": "a", "c": "wissen"}], "note": "meer Fabric"}\n```'
        issues = [{"number": 3, "title": "Interesses: 2 wijzigingen", "user": {"login": "tomasr91"}, "body": body},
                  {"number": 4, "title": "Interesses: spam", "user": {"login": "iemand"}, "body": body}]
        out = ir.requests(issues, "tomasr91")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0][1], {"answers": [{"id": "data-contracts", "a": "ja"}],
                                     "changes": [{"topic": "open_source_tools", "c": "minder"}], "note": "meer Fabric"})


class TestAreaMinimum(unittest.TestCase):
    """Ondergrens per gebied: aanvullen met recente uitgelegde artikelen net onder de drempel."""

    def test_fills_area_up_to_minimum(self):
        conf = cfg.load()
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        need = next(a for a in conf.interests["interest_areas"] if a["id"] == "claude")["min_articles"]
        mk = lambda i, d, score, when="2026-10-30T04:00:00Z": {"id": f"{i:012x}", "main_topics": ["claude_ai_development"], "topics": ["claude_ai_development"],
                                                              "processing_status": "enriched", "decision": d, "relevance_score": score, "processed_at": when}
        arts = [mk(i, "below_threshold", 50 + i) for i in range(need + 2)] + [mk(99, "below_threshold", 99, "2026-09-01T04:00:00Z"), mk(98, "excluded", 98)]
        extra = build_mod.area_minimum(arts, [], conf, now)
        self.assertEqual(len(extra), need)
        self.assertTrue(all(a["decision"] == "area_minimum" for a in extra))
        self.assertNotIn(f"{99:012x}", [a["id"] for a in extra])   # te oud
        self.assertNotIn(f"{98:012x}", [a["id"] for a in extra])   # uitgesloten blijft uitgesloten
        self.assertEqual(extra[0]["relevance_score"], 50 + need + 1)   # beste eerst


class TestNightRuns(unittest.TestCase):
    """Taakverslagen en wat de inhaalrun nog moet doen."""

    def test_night_status(self):
        import tempfile
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import night_status as ns
        d = Path(tempfile.mkdtemp())
        (d / "runs").mkdir()
        rep = lambda t, st="ok": json.dumps({"task": t, "status": st, "started_at": "2026-11-02T03:00:00Z", "finished_at": "2026-11-02T03:30:00Z", "summary": "x", "problems": []})
        now = datetime(2026, 11, 2, 6, 30, tzinfo=timezone.utc)   # maandag 07:30 Amsterdam
        self.assertEqual([t for t, _ in ns.missing(now, d)], ["uitleggen", "verdiepen", "overzicht"])
        for t in ["uitleggen", "verdiepen", "overzicht"]:
            (d / "runs" / f"2026-11-02-{t}.json").write_text(rep(t), encoding="utf-8")
        (d / "deepdive_options.json").write_text(json.dumps({"generated_at": "2026-11-02T04:20:00Z"}), encoding="utf-8")
        self.assertEqual(ns.missing(now, d), [])
        self.assertEqual([t for t, _ in ns.missing(now, d, pending_deepdive=True)], ["verdiepen"])
        (d / "runs" / "2026-11-02-overzicht.json").write_text(rep("overzicht", "deels"), encoding="utf-8")
        self.assertEqual([t for t, _ in ns.missing(now, d)], ["overzicht"])
        from pipeline import runs
        self.assertEqual(runs.latest(d / "runs")["date"], "2026-11-02")
        self.assertTrue(runs.validate({"task": "x"}))


class TestOwnTopic(unittest.TestCase):
    """Jouw lijst: eigen onderwerp als verdieping (issue 'Verdieping: eigen-...')."""

    def test_own_topic_from_issue(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import next_deepdive as nd
        body = "Eigen onderwerp\n\nOnderwerp: dbt project evaluator\nNotitie: past dit bij silver?\nGezien in: Ecolab (https://x)\n"
        o = nd.own_topic("eigen-dbt-project-evaluator", body)
        self.assertEqual((o["title"], o["question"], o["own"]), ("dbt project evaluator", "past dit bij silver?", True))
        self.assertEqual(nd.own_topic("eigen-iets-anders", "")["title"], "iets anders")
        issues = [{"number": 4, "title": "Verdieping: eigen-dbt-project-evaluator", "user": {"login": "tomasr91"}},
                  {"number": 5, "title": "Verdieping: eigen-spam", "user": {"login": "vreemde"}}]
        self.assertEqual(nd.choices(issues, "tomasr91"), [(4, "eigen-dbt-project-evaluator")])

    def test_plan_only_at_night_and_regular_plus_own(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import next_deepdive as nd
        issues = [{"number": 12, "title": "Verdieping: eigen-a", "user": {"login": "tomasr91"}, "body": "Onderwerp: A"},
                  {"number": 13, "title": "Verdieping: keuze-x", "user": {"login": "tomasr91"}},
                  {"number": 14, "title": "Verdieping: eigen-b", "user": {"login": "tomasr91"}},
                  {"number": 15, "title": "Verdieping: eigen-c", "user": {"login": "tomasr91"}},
                  {"number": 16, "title": "Verdieping: keuze-y", "user": {"login": "tomasr91"}}]
        known = {"keuze-x": {"id": "keuze-x"}, "keuze-y": {"id": "keuze-y"}}
        night = datetime(2026, 11, 2, 3, 15, tzinfo=timezone.utc)      # 04:15 Amsterdam
        day = datetime(2026, 11, 1, 14, 0, tzinfo=timezone.utc)        # 15:00 Amsterdam
        out = "\n".join(nd.plan(issues, "tomasr91", known, set(), night))
        self.assertIn("SCHRIJVEN: keuze-x (issue #13)", out)
        self.assertIn("SCHRIJVEN: eigen-a (issue #12)", out)
        self.assertIn("SCHRIJVEN: eigen-b (issue #14)", out)
        self.assertNotIn("SCHRIJVEN: eigen-c", out)          # hooguit 2 eigen per nacht
        self.assertNotIn("SCHRIJVEN: keuze-y", out)          # één gewone per nacht
        self.assertIn("LATER: eigen voorstel 'eigen-c'", out)
        self.assertTrue(nd.plan(issues, "tomasr91", known, set(), day)[0].startswith("NIET NU"))
        done = "\n".join(nd.plan(issues, "tomasr91", known, {"keuze-x"}, night))
        self.assertIn("AL GESCHREVEN: 'keuze-x'", done)
        self.assertIn("SCHRIJVEN: keuze-y (issue #16)", done)

    def test_own_plan_id_is_valid(self):
        from pipeline import deepdives
        probs = deepdives.validate({"plan_id": "eigen-dbt-project-evaluator"}, set(), set())
        self.assertFalse(any("plan_id" in p for p in probs))
        probs = deepdives.validate({"plan_id": "verzonnen"}, set(), set())
        self.assertTrue(any("plan_id" in p for p in probs))


class TestLearningLamp(unittest.TestCase):
    """Lampje: alleen als een leeronderwerp bij de eerste twee onderwerpen (Claudes volgorde) hoort."""

    def test_learning_from_main_topics(self):
        conf = cfg.load()
        learn = [t for t, v in conf.topics.items() if v.get("learning")]
        self.assertIn("data_ingestion", learn)
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        base = {"id": "aaaaaaaaaaaa", "title": "x", "url": "https://x", "source_id": "dbt_labs_blog", "published_at": "2026-10-31T00:00:00Z",
                "processing_status": "enriched", "quality": {"depth": .8, "practicality": .8, "novelty": .8}}
        a = score_article(dict(base, topics=["data_ingestion", "dbt_analytics_engineering"]), conf, now)
        self.assertEqual(a["learning"], conf.topics["data_ingestion"]["name"])
        b = score_article(dict(base, topics=["dbt_analytics_engineering", "ai_agents_rag", "data_ingestion"]), conf, now)
        self.assertIsNone(b["learning"])


class TestDeepdiveChoice(unittest.TestCase):
    """Dagelijkse keuzes: 5 geldige opties; alleen issues van de eigenaar tellen."""

    def _opts(self):
        o = lambda i: {"id": f"onderwerp-{i}", "title": f"Titel {i}", "question": "Vraag?", "why": "Omdat.",
                       "topics": ["ai_context_engineering"], "area": "context_agents"}
        return {"format_version": 1, "generated_at": "2026-10-29T06:00:00Z", "options": [o(i) for i in range(5)], "history": []}

    def test_validate_options(self):
        from pipeline import deepdives
        topics = set(cfg.load().topics)
        good = self._opts()
        self.assertEqual(deepdives.validate_options(good, topics, set()), [])
        self.assertTrue(deepdives.validate_options({**good, "options": good["options"][:4]}, topics, set()))
        self.assertTrue(deepdives.validate_options(good, topics, {"onderwerp-2"}), "al geschreven mag niet terugkomen")
        bad = self._opts(); bad["options"][0]["id"] = "Met Spaties"
        self.assertTrue(deepdives.validate_options(bad, topics, set()))

    def test_only_owner_issues_count(self):
        sys.path.insert(0, str(cfg.ROOT / "scripts"))
        import next_deepdive
        issues = [{"number": 5, "title": "Verdieping: b-onderwerp", "user": {"login": "TomasR91"}},
                  {"number": 3, "title": "Verdieping: a-onderwerp", "user": {"login": "tomasr91"}},
                  {"number": 4, "title": "Verdieping: c-onderwerp", "user": {"login": "vreemde"}},
                  {"number": 6, "title": "Iets anders", "user": {"login": "tomasr91"}},
                  {"number": 9, "title": "Verdieping: d", "user": {"login": "tomasr91"}, "pull_request": {}}]
        self.assertEqual(next_deepdive.choices(issues, "tomasr91"), [(3, "a-onderwerp"), (5, "b-onderwerp")])

    def test_chosen_option_is_valid_plan_id(self):
        from pipeline import deepdives
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "opts.json"
            path.write_text(json.dumps(self._opts()))
            self.assertIn("onderwerp-3", deepdives.known_options(path))


class TestFeedback(unittest.TestCase):
    """Duimpjes: issue lezen, voorkeuren berekenen, score bijsturen, duim omlaag = weg."""

    def test_parse_and_owner_only(self):
        sys.path.insert(0, str(cfg.ROOT / "scripts"))
        import collect_feedback as cf
        body = 'Tekst\n\n```json\n{"votes":[{"id":"841d424db697","v":-1,"r":"te_basic"},{"id":"xyz","v":1},{"id":"aaaaaaaaaaaa","v":1,"r":"onzin"}]}\n```'
        self.assertEqual(cf.parse_votes(body), [{"id": "841d424db697", "v": -1, "r": "te_basic"}, {"id": "aaaaaaaaaaaa", "v": 1, "r": None}])
        b2 = 'x\n```json\n{"votes": [{"id": "aaaaaaaaaaaa", "v": 1, "r": "score_te_laag", "s": 55}, {"id": "bbbbbbbbbbbb", "v": 1, "s": 300}]}\n```'
        self.assertEqual(cf.parse_explain('```json\n{"votes": [], "explain": ["aaaaaaaaaaaa", "nope"]}\n```'), ["aaaaaaaaaaaa"])
        self.assertEqual(cf.parse_votes(b2), [{"id": "aaaaaaaaaaaa", "v": 1, "r": "score_te_laag", "s": 55}, {"id": "bbbbbbbbbbbb", "v": 1, "r": None}])
        issues = [{"number": 1, "title": "Feedback: 2 beoordelingen", "user": {"login": "tomasr91"}},
                  {"number": 2, "title": "Feedback: 1", "user": {"login": "vreemde"}},
                  {"number": 3, "title": "Verdieping: x", "user": {"login": "tomasr91"}}]
        self.assertEqual([i["number"] for i in cf.owner_issues(issues, "tomasr91")], [1])

    def test_preferences_and_score(self):
        from pipeline import feedback
        data = {"votes": {f"{i:012x}": {"v": -1, "r": "geen_interesse", "at": "2026-10-28T00:00:00Z", "topics": ["powerbi_semantic_models"], "source_id": "powerbi_blog"} for i in range(3)}}
        prefs = feedback.preferences(data, NOW)
        self.assertLess(prefs["topics"]["powerbi_semantic_models"], -0.4)
        conf = cfg.load()
        a = normalize(raw("powerbi_blog", "Power BI semantic model DAX Microsoft Fabric news", "https://example.org/pbi"))
        a["processing_status"] = "raw"
        plain = score_article(dict(a), conf, NOW)["relevance_score"]
        tuned = score_article(dict(a), conf, NOW, prefs, data["votes"])
        self.assertLess(tuned["relevance_score"], plain)
        self.assertLessEqual(plain - tuned["relevance_score"], 15)
        down = score_article(dict(a), conf, NOW, prefs, {a["id"]: {"v": -1}})
        self.assertNotEqual(down.get("decision"), "hidden_by_feedback")   # duim omlaag haalt het artikel niet weg


class TestSkippedRetry(unittest.TestCase):
    """Onleesbare pagina: na een week nog één keer op de werklijst; daarna niet meer."""

    def test_unreadable_gets_one_retry(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from pipeline import build, enrich
        tmp = Path(tempfile.mkdtemp())
        (tmp / "skipped").mkdir()
        def put(i, reason, at):
            (tmp / "skipped" / f"{i}.json").write_text(json.dumps({"article_id": i, "reason": reason, "checked_at": at}), encoding="utf-8")
        put("aaaaaaaaaaaa", "Bronpagina niet te lezen: fout", "2026-10-20T03:00:00Z")
        put("bbbbbbbbbbbb", "Niet mijn stack", "2026-10-20T03:00:00Z")
        put("cccccccccccc", "Pagina niet te lezen", "2026-10-30T03:00:00Z")
        now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        with mock.patch.object(enrich, "CACHE", tmp), mock.patch.object(build, "RETRIED", tmp / "retried.json"):
            self.assertEqual(build.skipped_ids(now), {"bbbbbbbbbbbb", "cccccccccccc"})
            self.assertEqual(build.skipped_ids(now), {"bbbbbbbbbbbb", "cccccccccccc"})   # kans blijft tot Claude opnieuw kijkt
            put("aaaaaaaaaaaa", "Bronpagina niet te lezen: weer fout", "2026-11-02T03:00:00Z")
            self.assertIn("aaaaaaaaaaaa", build.skipped_ids(datetime(2026, 11, 20, tzinfo=timezone.utc)))


class TestTaste(unittest.TestCase):
    """Leren van wat T goed vindt: soort artikel, Claudes 'past bij jou' (fit) en minder snel verzadigen."""

    def test_fit_kind_and_validation(self):
        from pipeline import feedback, enrich
        conf = cfg.load()
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        base = {"id": "f1", "title": "x", "url": "https://x", "source_id": "dbt_labs_blog", "published_at": "2026-10-31T00:00:00Z",
                "processing_status": "enriched", "topics": ["dbt_analytics_engineering"], "quality": {"depth": .6, "practicality": .6, "novelty": .6}}
        plain = score_article(dict(base), conf, now)["relevance_score"]
        hi = score_article(dict(base, fit={"score": 1.0, "why": "Zoals je praktische dbt-stukken."}), conf, now)
        lo = score_article(dict(base, fit={"score": 0.0, "why": "Aankondiging zonder inhoud."}), conf, now)
        self.assertEqual(hi["relevance_score"] - plain, 10)
        self.assertEqual(plain - lo["relevance_score"], 10)
        data = {"votes": {"a": {"v": 1, "at": "2026-10-31T00:00:00Z", "topics": [], "source_id": "", "soort": "praktisch"},
                          "b": {"v": -1, "at": "2026-10-31T00:00:00Z", "topics": [], "source_id": "", "soort": "aankondiging"}}}
        prefs = feedback.preferences(data, now)
        self.assertGreater(prefs["kinds"]["praktisch"], 0)
        self.assertLess(prefs["kinds"]["aankondiging"], 0)
        self.assertGreater(feedback.article_factor({"topics": [], "soort": "praktisch"}, prefs), 0)
        self.assertLess(feedback.preferences({"votes": {str(i): {"v": 1, "at": "2026-10-31T00:00:00Z", "topics": ["t"]} for i in range(2)}}, now)["topics"]["t"], 0.7)
        self.assertEqual(enrich.validate_fit({"score": 0.7, "why": "Past bij je dbt-werk."}), [])
        self.assertTrue(enrich.validate_fit({"score": 1.4, "why": "x"}))
        self.assertTrue(enrich.validate_fit({"score": 0.4, "why": ""}))


class TestRelevantNotFun(unittest.TestCase):
    """Minder leuk maar wel relevant: kwaliteitsredenen raken het onderwerp niet, en 'altijd volgen'."""

    def test_quality_reasons_spare_topic(self):
        from pipeline import feedback
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        vote = lambda r: {"v": -1, "r": r, "at": "2026-10-31T00:00:00Z", "topics": ["data_governance_privacy"], "source_id": "s", "soort": "aankondiging"}
        q = feedback.preferences({"votes": {"a": vote("te_vaag"), "b": vote("te_basic")}}, now)
        self.assertNotIn("data_governance_privacy", q["topics"])
        self.assertNotIn("s", q["sources"])
        self.assertLess(q["kinds"]["aankondiging"], 0)
        self.assertNotIn("data_governance_privacy", feedback.preferences({"votes": {"a": vote(None)}}, now)["topics"])   # 👎 zonder reden: over het artikel
        g = feedback.preferences({"votes": {"a": vote("geen_interesse")}}, now)
        self.assertLess(g["topics"]["data_governance_privacy"], 0)

    def test_follow_blocks_push_down_and_keeps_one(self):
        from pipeline import build
        conf = cfg.load()
        tid = "data_governance_privacy"
        next(t for t in conf.interests["topics"] if t["id"] == tid)["follow"] = True
        conf.topics[tid]["follow"] = True
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        prefs = {"topics": {tid: -1.0}, "sources": {}, "offset": 0.0}
        a = {"id": "g1", "title": "x", "url": "https://x", "source_id": "databricks_blog", "published_at": "2026-10-30T00:00:00Z",
             "processing_status": "enriched", "topics": [tid], "quality": {"depth": .2, "practicality": .2, "novelty": .2},
             "fit": {"score": 0.1, "why": "Saai."}}
        r = score_article(dict(a), conf, now, prefs)
        self.assertNotIn("feedback", r["score_parts"])
        self.assertEqual(r["score_parts"]["fit"], 0.0)
        r["decision"] = "below_threshold"
        extra = build.follow_minimum([r], [], conf, now)
        self.assertEqual([x["id"] for x in extra], ["g1"])
        self.assertEqual(r["decision"], "follow_minimum")


class TestBalance(unittest.TestCase):
    """Maximum per gebied en alleen recente artikelen op de werklijst (T, 4-11-2026)."""

    def test_area_cap_and_age(self):
        from pipeline import build
        conf = cfg.load()
        now = datetime(2026, 11, 4, tzinfo=timezone.utc)
        mk = lambda i, t, sc: {"id": f"{i:012x}", "topics": [t], "relevance_score": sc, "decision": "included", "source_id": "x"}
        shown = [mk(i, "ai_agents_rag", 90 - i) for i in range(16)] + [mk(100 + i, "dbt_analytics_engineering", 70) for i in range(4)]
        shown[15]["id"] = "liked0000000"
        kept = build.area_cap(list(shown), conf, {"liked0000000": {"v": 1}})
        agents = [a for a in kept if a["topics"] == ["ai_agents_rag"]]
        self.assertEqual(len(agents), 9 + 1)                     # 1,5 x 30% van 20 = 9, plus het artikel met 👍
        self.assertIn("liked0000000", [a["id"] for a in agents])
        self.assertEqual(sum(a["decision"] == "area_cap" for a in shown), 6)
        self.assertEqual(len([a for a in kept if a["topics"] == ["dbt_analytics_engineering"]]), 4)
        self.assertGreater(build._age_days({"published_at": "2026-10-06T00:00:00Z"}, now), build.QUEUE_MAX_AGE_DAYS)
        self.assertLessEqual(build._age_days({"published_at": "2026-10-28T00:00:00Z"}, now), build.QUEUE_MAX_AGE_DAYS)


class TestShortTier(unittest.TestCase):
    """Meer artikelen: uitgelegd en tussen 45 en de drempel komt ook in de feed; korte uitleg is geldig."""

    def test_low_band_and_short_validation(self):
        from pipeline import enrich
        conf = cfg.load()
        now = datetime(2026, 11, 5, tzinfo=timezone.utc)
        base = {"id": "n1", "title": "x", "url": "https://x", "source_id": "sqlbi", "published_at": "2026-11-04T00:00:00Z",
                "processing_status": "enriched", "topics": ["open_source_tools"], "quality": {"depth": .4, "practicality": .4, "novelty": .4}}
        r = score_article(dict(base), conf, now)
        lo, thr = conf.scoring["min_relevance_score_short"] * 100, conf.scoring["min_relevance_score"] * 100
        if lo <= r["relevance_score"] < thr:
            self.assertEqual(r["decision"], "included_low")
        raw = score_article(dict(base, processing_status="raw", quality=None), conf, now)
        self.assertNotEqual(raw["decision"], "included_low")       # alleen al uitgelegde artikelen
        short = {"format_version": 2, "diepte": "kort", "headline": "Kop", "summary": "Twee zinnen.", "topics": ["open_source_tools"],
                 "availability_status": "onbekend", "quality": {"depth": .3, "practicality": .4, "novelty": .4},
                 "soort": "aankondiging", "fit": {"score": 0.5, "why": "Neutraal."}, "labels": ["lakefs"]}
        self.assertEqual(enrich.validate(short, set(conf.topics)), [])
        self.assertTrue(enrich.validate({k: v for k, v in short.items() if k != "labels"}, set(conf.topics)))


class TestLearnScoreCorrection(unittest.TestCase):
    """Duim = correctie op de score: snel waar het specifiek is, traag waar het breed is (pipeline/learn.py)."""

    def _fb(self, **vote):
        base = {"v": 1, "at": "2026-11-04T00:00:00Z", "title": "Metric views in Unity Catalog", "topics": ["databricks_data_engineering"],
                "source_id": "databricks_blog", "soort": "praktisch", "labels": ["metric-views", "unity-catalog"],
                "text": "Metric views in Unity Catalog definieer je metrics eenmalig in YAML", "s": 55}
        return {"votes": {"aaaaaaaaaaaa": {**base, **vote}}, "reads": {}}

    def test_levels_and_caps(self):
        from pipeline import learn
        now = datetime(2026, 11, 5, tzinfo=timezone.utc)
        m = learn.model(self._fb(), now)
        same = {"title": "Metric views krijgen materialisatie", "labels": ["metric-views", "unity-catalog"], "summary": "Metric views in Unity Catalog",
                "topics": ["databricks_data_engineering"], "source_id": "databricks_blog", "soort": "praktisch"}
        other = {"title": "Auto Loader leest sneller", "labels": ["auto-loader"], "summary": "Bestanden inlezen",
                 "topics": ["databricks_data_engineering"], "source_id": "simon_whiteley", "soort": "aankondiging"}
        far = {"title": "Claude Code hooks", "labels": ["claude-code-hooks"], "topics": ["claude_ai_development"], "source_id": "claude_blog"}
        d_same, why = learn.effect(same, m)
        d_other, _ = learn.effect(other, m)
        d_far, _ = learn.effect(far, m)
        self.assertGreater(d_same, 0.12)                 # één duim op een 55 doet al echt iets bij vergelijkbare artikelen
        self.assertLessEqual(d_same, learn.TOTAL_CAP)
        self.assertEqual(why["by"], "similar")
        self.assertTrue(0 < d_other < 0.08)               # zelfde onderwerp, ander ding: weinig
        self.assertEqual(d_far, 0.0)
        # duim bij 92: de score klopte al, dus bijna geen effect
        d_hi, _ = learn.effect(same, learn.model(self._fb(s=92), now))
        self.assertLess(d_hi, 0.02)
        # 'score te laag' telt zwaarder
        d_strong, _ = learn.effect(other, learn.model(self._fb(r="score_te_laag"), now))
        self.assertGreater(d_strong, d_other)
        # 👎 om de kwaliteit raakt alleen de soort, niet het onderwerp of vergelijkbare artikelen
        mq = learn.model(self._fb(v=-1, r="te_vaag"), now)
        self.assertEqual(mq["examples"], [])
        self.assertNotIn("databricks_data_engineering", mq["levels"]["topic"])
        # 👎 'interesseert me niet' duwt vergelijkbare artikelen omlaag
        d_down, _ = learn.effect(same, learn.model(self._fb(v=-1, r="geen_interesse", s=80), now))
        self.assertLess(d_down, -0.1)

    def test_score_article_uses_model_and_follow(self):
        from pipeline import learn
        conf = cfg.load()
        now = datetime(2026, 11, 5, tzinfo=timezone.utc)
        art = {"id": "bbbbbbbbbbbb", "title": "Metric views krijgen materialisatie", "url": "https://x", "source_id": "databricks_blog",
               "published_at": "2026-11-04T00:00:00Z", "processing_status": "enriched", "topics": ["databricks_data_engineering"],
               "labels": ["metric-views", "unity-catalog"], "summary": "Metric views in Unity Catalog", "soort": "praktisch",
               "quality": {"depth": .5, "practicality": .5, "novelty": .5}}
        plain = score_article(dict(art), conf, now)["relevance_score"]
        prefs = {"model": learn.model(self._fb(), now)}
        tuned = score_article(dict(art), conf, now, prefs)
        self.assertGreater(tuned["relevance_score"], plain + 10)
        self.assertEqual(tuned["fb_why"]["by"], "similar")
        self.assertLessEqual(tuned["relevance_score"] - plain, 20)
        down = {"model": learn.model(self._fb(v=-1, r="geen_interesse", s=80), now)}
        tid = "databricks_data_engineering"
        next(t for t in conf.interests["topics"] if t["id"] == tid)["follow"] = True
        conf.topics[tid]["follow"] = True
        self.assertNotIn("feedback", score_article(dict(art), conf, now, down)["score_parts"])   # altijd volgen: niet omlaag


class TestFetchLess(unittest.TestCase):
    """Alleen ophalen als het nodig is; anders opnieuw samenstellen uit het archief (T, 5-11-2026)."""

    def test_should_fetch_and_archive_provider(self):
        import tempfile
        from pathlib import Path
        from pipeline import build
        from pipeline.providers import archive
        conf = cfg.load()
        d = Path(tempfile.mkdtemp())
        feed, req = d / "feed.json", d / "run-request"
        now = datetime(2026, 11, 5, 9, tzinfo=timezone.utc)
        srcs = [{"id": s["id"], "status": "ok", "items": 3} for s in conf.source_list if s.get("enabled")]
        self.assertTrue(build.should_fetch(conf, now, feed, req))                      # geen feed: ophalen
        feed.write_text(json.dumps({"last_successful_update": "2026-11-05T03:00:00Z", "mode": "live", "sources": srcs}))
        self.assertFalse(build.should_fetch(conf, now, feed, req))                     # 6 uur geleden: niet
        self.assertTrue(build.should_fetch(conf, now + timedelta(hours=13), feed, req))  # te lang geleden
        req.write_text("2026-11-06")
        self.assertTrue(build.should_fetch(conf, now, feed, req))                      # de nachttaak vraagt erom
        req.write_text("2026-11-05")
        self.assertFalse(build.should_fetch(conf, now, feed, req))
        feed.write_text(json.dumps({"last_successful_update": "2026-11-05T03:00:00Z", "sources": srcs[1:]}))
        self.assertTrue(build.should_fetch(conf, now, feed, req))                      # nieuwe bron
        (d / "archive.json").write_text(json.dumps({"items": {"x:1": {"source_id": "x", "title": "t", "url": "https://x"}}}))
        r = archive.collect(conf, d / "archive.json", feed)
        self.assertEqual(len(r.items), 1)
        self.assertEqual(r.extra["captured_at"], "2026-11-05T03:00:00Z")


class TestRodeDraad(unittest.TestCase):
    """Dataflow (context/rode-draad.yml): verwijzing in de uitleg en 5 punten voorrang."""

    def test_project_ref(self):
        from pipeline import enrich
        conf = cfg.load()
        now = datetime(2026, 11, 10, tzinfo=timezone.utc)
        self.assertEqual(len(enrich.rode_draad()["phases"]), 8)
        story = ["Een alinea.", "Met snapshots bewaar je in dbt de historie van een tabel."]
        ok = {"fase": 4, "quote": "Met snapshots bewaar je in dbt de historie", "why": "Snapshots zitten in fase 4."}
        self.assertEqual(enrich.validate_project_ref({"story": story, "project_ref": ok}), [])
        self.assertEqual(enrich.validate_project_ref({"story": story, "project_ref": None}), [])
        self.assertTrue(enrich.validate_project_ref({"story": story, "project_ref": {**ok, "fase": 12}}))
        self.assertTrue(enrich.validate_project_ref({"story": story, "project_ref": {**ok, "quote": "staat er niet in maar is lang genoeg"}}))
        base = {"id": "p1", "title": "x", "url": "https://x", "source_id": "dbt_labs_blog", "published_at": "2026-11-09T00:00:00Z",
                "processing_status": "enriched", "topics": ["dbt_analytics_engineering"], "quality": {"depth": .5, "practicality": .5, "novelty": .5}}
        plain = score_article(dict(base), conf, now)["relevance_score"]
        self.assertEqual(score_article(dict(base, project_ref=ok), conf, now)["relevance_score"] - plain, 5)
        a = {}
        enrich.attach(a, {"project_ref": None})
        self.assertTrue(a["project_checked"])


class TestLeerregels(unittest.TestCase):
    """Toelichting bij een duim -> leerregel (pipeline/rules.py): raakt alleen passende artikelen, nooit een artikel weg."""
    RULE = {"id": "einde-support", "text": "Einde van support voor versies", "richting": -1, "sterkte": 1.0,
            "keywords": ["end of support", "einde support"], "labels": ["einde-support"], "van": "0123456789ab", "at": "2026-11-12", "active": True}

    def art(self, title, **kw):
        return {"id": "x1", "title": title, "url": "https://x", "source_id": "dbt_labs_blog", "published_at": "2026-11-09T00:00:00Z",
                "processing_status": "enriched", "topics": ["dbt_analytics_engineering"],
                "quality": {"depth": .5, "practicality": .5, "novelty": .5}, **kw}

    def test_validate(self):
        from pipeline import rules
        self.assertEqual(rules.validate(self.RULE), [])
        self.assertTrue(rules.validate({**self.RULE, "richting": 0}))
        self.assertTrue(rules.validate({**self.RULE, "keywords": ["dbt"], "labels": []}))       # te kort/los
        self.assertTrue(rules.validate({**self.RULE, "keywords": [], "labels": []}))
        self.assertTrue(rules.validate({**self.RULE, "sterkte": 2}))
        self.assertTrue(rules.validate({**self.RULE, "id": "Fout id"}))

    def test_raakt_alleen_passende_artikelen(self):
        from pipeline import rules
        conf, now = cfg.load(), datetime(2026, 11, 12, tzinfo=timezone.utc)
        plain = score_article(self.art("Snapshots in dbt"), conf, now, {"rules": [self.RULE]})
        self.assertNotIn("rule_why", plain)
        base = score_article(self.art("Databricks Runtime 17.3: end of support in december"), conf, now)["relevance_score"]
        hit = score_article(self.art("Databricks Runtime 17.3: end of support in december"), conf, now, {"rules": [self.RULE]})
        self.assertEqual(base - hit["relevance_score"], 15)
        self.assertEqual(hit["rule_why"][0]["id"], "einde-support")
        self.assertNotEqual(hit["decision"], "excluded")   # een regel haalt niets weg
        lab = score_article(self.art("Iets anders", labels=["einde-support"]), conf, now, {"rules": [self.RULE]})
        self.assertIn("regel", lab["score_parts"])
        up = {**self.RULE, "id": "meer", "richting": 1, "sterkte": 0.5, "keywords": ["iets anders"]}
        self.assertEqual(rules.effect({"title": "Iets anders", "labels": []}, [up])[1][0]["pts"], 8)

    def test_cap_en_actief(self):
        from pipeline import rules
        two = [self.RULE, {**self.RULE, "id": "twee"}]
        self.assertEqual(rules.effect({"title": "end of support"}, two)[0], -0.15)   # samen hooguit 15 punten
        data = {"rules": [self.RULE, {**self.RULE, "id": "uit", "active": False}, {**self.RULE, "id": "fout", "richting": 5}], "noted": {}}
        self.assertEqual([r["id"] for r in rules.active_rules(data)], ["einde-support"])

    def test_view_stale_en_todo(self):
        from pipeline import rules
        data = {"rules": [{**self.RULE, "at": "2026-06-01"}], "noted": {"aaaaaaaaaaaa": None}}
        v = rules.view(data, [{"title": "Snapshots", "decision": "included"}], "2026-11-12")
        self.assertTrue(v[0]["stale"])
        self.assertEqual(rules.view(data, [{"title": "end of support", "decision": "included"}], "2026-11-12")[0]["hits"], 1)
        fb = {"votes": {"aaaaaaaaaaaa": {"v": -1, "n": "al bekeken"}, "bbbbbbbbbbbb": {"v": -1, "n": "nieuw", "title": "T"}, "cccccccccccc": {"v": 1}}}
        with tempfile.TemporaryDirectory() as tmp:
            old = rules.TODO
            rules.TODO = Path(tmp) / "todo.json"
            try:
                self.assertEqual(rules.write_todo(fb, data), 1)
                self.assertEqual(json.loads(rules.TODO.read_text())["items"][0]["id"], "bbbbbbbbbbbb")
            finally:
                rules.TODO = old

    def test_collect_feedback(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import collect_feedback as cf
        body = '```json\n{"votes": [{"id": "0123456789ab", "v": -1, "r": null, "n": "  Einde  support\\n van versies  "}], "rules_off": ["einde-support", "Fout id"]}\n```'
        self.assertEqual(cf.parse_votes(body)[0]["n"], "Einde support van versies")
        self.assertEqual(cf.parse_rules_off(body), ["einde-support"])
        self.assertNotIn("n", cf.parse_votes('```json\n{"votes": [{"id": "0123456789ab", "v": 1}]}\n```')[0])

    def test_validate_script_en_taak(self):
        text = (Path(__file__).resolve().parent.parent / "taken" / "LEERREGELS.md").read_text(encoding="utf-8")
        self.assertIn("validate_rules.py", text)
        self.assertTrue((Path(__file__).resolve().parent.parent / "scripts" / "validate_rules.py").exists())


class TestTrends(unittest.TestCase):
    def test_only_trends_with_enough_articles_and_sources(self):
        from pipeline import trends
        shown = [{"id": f"a{i}", "source_id": "s1" if i < 3 else "s2"} for i in range(5)]
        data = {"generated_at": "2026-10-29T06:00:00Z", "trends": [
            {"id": "goed", "title": "T", "summary": "S", "article_ids": ["a0", "a1", "a3"]},
            {"id": "een-bron", "title": "T", "summary": "S", "article_ids": ["a0", "a1", "a2"]},
            {"id": "verdwenen", "title": "T", "summary": "S", "article_ids": ["a0", "a3", "weg"]}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trends.json"
            path.write_text(json.dumps(data))
            out, problems = trends.load(set(), shown, path)
        self.assertEqual(problems, [])
        self.assertEqual([t["id"] for t in out], ["goed"])
        self.assertTrue(trends.validate({"generated_at": "x", "trends": [{"id": "a", "title": "t", "summary": "s", "article_ids": ["1"]}]}, set()))


class TestPractice(unittest.TestCase):
    """'Zo ziet het eruit': vorm controleren."""

    def test_showcase(self):
        from pipeline.practice import validate_showcase
        good = {"caption": "c", "language": "sql", "code": "SELECT 1", "note": "n", "result": {"columns": ["a"], "rows": [[1]]}}
        self.assertEqual(validate_showcase(good), [])
        self.assertTrue(validate_showcase({**good, "language": "cobol"}))
        self.assertTrue(validate_showcase({**good, "result": {"columns": ["a", "b"], "rows": [[1]]}}))


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

    def _explain(self, item):
        """Zet een geldige uitleg (formaat 2) klaar, zoals de geplande Claude-taak dat doet."""
        data = json.loads((self._data / "enrichment" / "841d424db697.json").read_text(encoding="utf-8"))
        aid = normalize(item)["id"]
        enrich.CACHE.mkdir(parents=True, exist_ok=True)
        (enrich.CACHE / f"{aid}.json").write_text(json.dumps(data), encoding="utf-8")
        return aid

    def _provider(self, items, mode="partial"):
        return lambda c: ProviderResult(items=items, source_results=[{"source_id": "dbt_labs_blog", "status": "ok", "items": len(items), "message": "", "checked_at": F}], mode=mode)

    def test_end_to_end_without_key(self):
        items = [raw("dbt_labs_blog", "dbt tests for data quality and lineage", "https://example.org/1",
                     excerpt="dbt tests, data lineage, semantic layer"),
                 raw("databricks_blog", "dbt tests for data quality and lineage!", "https://example.org/1?utm_source=rss",
                     excerpt="dbt tests, data lineage, semantic layer")]
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider(items), now=NOW)
        self.assertEqual(feed["articles"], [], "niet uitgelegd = niet in de app")
        self.assertEqual(feed["quality_report"]["merged_duplicates"], 1)
        self._explain(items[0])
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider(items), now=NOW)
        self.assertEqual(len(feed["articles"]), 1, "dubbel artikel één keer getoond")
        self.assertEqual(feed["articles"][0]["processing_status"], "enriched")
        self.assertTrue(list((cfg.DATA / "raw").glob("*.json")), "ruwe laag wordt bewaard")

    def test_archive_keeps_articles_that_left_the_feed(self):
        item = raw("dbt_labs_blog", "dbt tests for data quality and lineage", "https://example.org/1",
                   excerpt="dbt tests, data lineage, semantic layer")
        self._explain(item)
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
        self.assertEqual(feed["articles"], [], "ongeldige uitleg telt niet: artikel blijft verborgen")
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
        for it in items:
            self._explain(it)
        feed = build_mod.build("feeds", self.out, provider_fn=self._provider(items), now=NOW)
        self.assertEqual({a["source_id"] for a in feed["articles"]}, {"dbt_labs_blog"})

    def test_failed_fetch_keeps_previous_feed(self):
        self.out.write_text(json.dumps({"mode": "live", "articles": [{"id": "x"}], "sources": []}))
        failing = lambda c: ProviderResult(items=[], source_results=[], mode="failed", note="offline")
        feed = build_mod.build("feeds", self.out, provider_fn=failing, now=NOW)
        self.assertEqual(feed["mode"], "stale")
        self.assertEqual(feed["articles"], [{"id": "x"}])


class TestDeepdives(unittest.TestCase):
    def setUp(self):
        self.topics = set(cfg.load().topics)
        self.plan = {"topics": [{"id": "a", "enabled": True}, {"id": "b", "enabled": True}]}
        self.good = {"id": "a", "plan_id": "a", "headline": "Kop", "summary": "s", "experiment": "e",
                     "currency_check": "Gecontroleerd.", "written_at": "2026-10-29T06:00:00Z", "processed_by": "Claude",
                     "sections": [{"heading": f"H{i}", "paragraphs": ["p"]} for i in range(3)],
                     "further_reading": [{"label": "x", "url": "https://example.org/1"}, {"label": "y", "url": "https://example.org/2"}],
                     "limitations": [], "topics": ["dbt_analytics_engineering"]}

    def test_valid_and_invalid(self):
        from pipeline import deepdives
        self.assertEqual(deepdives.validate(self.good, self.topics, {"a", "b"}), [])
        self.assertTrue(deepdives.validate({**self.good, "plan_id": "z"}, self.topics, {"a", "b"}))
        self.assertTrue(deepdives.validate({**self.good, "sections": self.good["sections"][:2]}, self.topics, {"a", "b"}))
        self.assertTrue(deepdives.validate({**self.good, "further_reading": [{"label": "x", "url": "http://x"}] * 2}, self.topics, {"a", "b"}))
        self.assertTrue(deepdives.validate({**self.good, "currency_check": ""}, self.topics, {"a", "b"}))

    def test_next_topic_skips_done(self):
        from pipeline import deepdives
        with tempfile.TemporaryDirectory() as tmp:
            old = deepdives.DIR
            deepdives.DIR = Path(tmp)
            try:
                self.assertEqual(deepdives.next_topic(self.plan)["id"], "a")
                (Path(tmp) / "a.json").write_text(json.dumps(self.good))
                self.assertEqual(deepdives.next_topic(self.plan)["id"], "b")
                good, bad = deepdives.load_all(self.topics, self.plan)
                self.assertEqual([d["id"] for d in good], ["a"])
                self.assertEqual(bad, [])
            finally:
                deepdives.DIR = old


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
                needed = ((["headline", "summary", "availability_status"] if a.get("diepte") == "kort" else ["headline", "summary", "story", "key_facts", "availability_status"]) if a.get("format_version") == 2
                          else ["summary", "what_is_new", "personal_relevance", "availability_status"])
                for k in needed:
                    self.assertIn(k, a, f"{a['title']}: {k}")
        self.assertTrue(set(f["daily_top"]) <= set(ids))
        self.assertLessEqual(len(f["daily_top"]), 5)


if __name__ == "__main__":
    unittest.main()
