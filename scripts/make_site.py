"""Maakt de map site/ voor GitHub Pages: app/index.html in een volledig HTML-document, plus feed.json.

app/index.html is geschreven als pagina-inhoud (zonder <html>/<head>), zodat dezelfde file
ook als Claude-artifact gepubliceerd kan worden. Hier krijgt hij het ontbrekende skelet.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

HEAD = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    page = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    (SITE / "index.html").write_text(HEAD + page + "\n</body>\n</html>\n", encoding="utf-8")
    shutil.copy(ROOT / "data" / "feed.json", SITE / "feed.json")
    (SITE / ".nojekyll").write_text("")
    print(f"site/ klaar: {sorted(p.name for p in SITE.iterdir())}")


if __name__ == "__main__":
    main()
