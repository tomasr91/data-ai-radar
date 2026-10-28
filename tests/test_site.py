"""Controleert de opbouw van de PWA-site (scripts/make_site.py)."""
import json
import struct
import unittest

from scripts import make_site


class TestSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        make_site.main()
        cls.site = make_site.SITE

    def test_html_links_manifest_and_registers_sw(self):
        html = (self.site / "index.html").read_text(encoding="utf-8")
        head = html.split("</head>")[0]
        self.assertIn('<link rel="manifest" href="manifest.webmanifest">', head)
        self.assertIn("<title>Data &amp; AI Radar</title>", head)
        self.assertEqual(html.count("<title>"), 1)
        self.assertIn('register("sw.js", { scope: "./" })', html)

    def test_manifest_relative_paths(self):
        m = json.loads((self.site / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual((m["start_url"], m["scope"], m["display"]), ("./", "./", "standalone"))
        for icon in m["icons"]:
            self.assertFalse(icon["src"].startswith("/"), "pad moet relatief zijn voor /data-ai-radar/")
            png = (self.site / icon["src"]).read_bytes()
            self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
            w, h = struct.unpack(">II", png[16:24])
            self.assertEqual(f"{w}x{h}", icon["sizes"])

    def test_service_worker_gets_build_id(self):
        sw = (self.site / "sw.js").read_text(encoding="utf-8")
        html = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("__BUILD__", sw)
        build = html.split('name="build" content="')[1].split('"')[0]
        self.assertIn(f'const BUILD = "{build}"', sw)


if __name__ == "__main__":
    unittest.main()
