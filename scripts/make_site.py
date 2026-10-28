"""Maakt de map site/ voor GitHub Pages: een installeerbare web-app (PWA).

app/index.html is geschreven als pagina-inhoud (zonder <html>/<head>), zodat dezelfde file
ook als Claude-artifact gepubliceerd kan worden. Hier krijgt hij:
- een volledig HTML-skelet met <title> in de <head>
- het manifest, de app-iconen en de themakleur
- een service worker (app/pwa/sw.js) met een build-nummer, zodat elke deployment een nieuwe
  versie oplevert en oude caches worden opgeruimd

Alle paden zijn relatief, omdat de site onder /data-ai-radar/ staat en niet op de root.
"""
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PWA = ROOT / "app" / "pwa"


def build_id() -> str:
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        try:
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        except OSError:
            sha = ""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{(sha or 'local')[:8]}-{stamp}"


HEAD = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="build" content="{build}">
{title}
<meta name="description" content="De ontwikkelingen die ertoe doen voor jouw data- en AI-werk, uitgelegd in eenvoudig Nederlands.">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#f3f4f1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1217" media="(prefers-color-scheme: dark)">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="AI Radar">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
"""

FOOT = """
<script>
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("sw.js", { scope: "./" }).catch(function () {});
  });
}
</script>
</body>
</html>
"""


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    build = build_id()
    page = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<title>.*?</title>", page, re.S)
    title = m.group(0) if m else "<title>Data &amp; AI Radar</title>"
    page = page.replace(title, "", 1) if m else page
    (SITE / "index.html").write_text(HEAD.format(build=build, title=title) + page + FOOT, encoding="utf-8")
    shutil.copy(ROOT / "data" / "feed.json", SITE / "feed.json")
    shutil.copy(PWA / "manifest.webmanifest", SITE / "manifest.webmanifest")
    shutil.copytree(PWA / "icons", SITE / "icons")
    sw = (PWA / "sw.js").read_text(encoding="utf-8").replace("__BUILD__", build)
    (SITE / "sw.js").write_text(sw, encoding="utf-8")
    (SITE / ".nojekyll").write_text("")
    print(f"site/ klaar (build {build}): {sorted(p.name for p in SITE.iterdir())}")


if __name__ == "__main__":
    main()
