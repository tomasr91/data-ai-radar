"""Zoekt feeds voor bronnen zonder feed_url en controleert ze echt.

Werkwijze per bron:
1. Lees de pagina en zoek <link rel="alternate" type="application/rss+xml|atom+xml">.
2. Probeer daarna gangbare feedpaden (/feed, /rss.xml, ...).
3. Een adres telt alleen als het een geldige feed met artikelen oplevert.

Resultaat: data/feed_discovery.json en (op GitHub) een samenvatting bij de run.
sources.yml wordt NIET automatisch aangepast; dat gebeurt na beoordeling.
Gebruik: python scripts/discover_feeds.py
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.config import load  # noqa: E402
from pipeline.normalize import parse_date  # noqa: E402
from pipeline.providers.feeds import http_get, parse_feed  # noqa: E402

COMMON = ["feed", "feed/", "feed.xml", "rss.xml", "rss", "index.xml", "atom.xml", "blog/rss.xml", "blog/feed.xml"]
LINK_TAG = re.compile(r"<link\b[^>]*>", re.I)


def autodiscover(html: str, base: str) -> list:
    found = []
    for tag in LINK_TAG.findall(html):
        if re.search(r'rel=["\']?alternate', tag, re.I) and re.search(r'type=["\']?application/(rss|atom)\+xml', tag, re.I):
            m = re.search(r'href=["\']([^"\']+)', tag, re.I)
            if m:
                found.append(urljoin(base, m.group(1)))
    return found


def candidates(url: str, html: str) -> list:
    parts = urlsplit(url)
    root = f"{parts.scheme}://{parts.netloc}/"
    base = url if url.endswith("/") else url + "/"
    cands = autodiscover(html, url) if html else []
    cands += [urljoin(base, c) for c in COMMON] + [urljoin(root, c) for c in COMMON]
    return list(dict.fromkeys(cands))


def try_feed(url: str):
    try:
        items = parse_feed(http_get(url), "x", "")
    except Exception as e:  # noqa: BLE001 - elke fout betekent: geen bruikbare feed
        return None, str(e)[:120]
    dates = sorted((d for d in (parse_date(i["published_raw"]) for i in items) if d), reverse=True)
    return {"feed_url": url, "items": len(items), "latest": dates[0] if dates else None,
            "sample_titles": [i["title"] for i in items[:3]],
            "method": "atom" if b"<feed" in http_get(url)[:500] else "rss"}, None


def main():
    conf = load()
    report = {"checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "sources": []}
    for src in conf.source_list:
        if not src.get("enabled") or src.get("feed_url") or src["fetch_method"] in ("rss", "atom", "github_releases"):
            continue
        entry = {"id": src["id"], "url": src["url"], "found": None, "page": None, "tried": 0}
        try:
            html = http_get(src["url"]).decode("utf-8", "replace")
            entry["page"] = "ok"
        except Exception as e:  # noqa: BLE001
            html, entry["page"] = "", f"pagina niet bereikbaar: {str(e)[:100]}"
        for cand in candidates(src["url"], html):
            entry["tried"] += 1
            ok, _ = try_feed(cand)
            if ok:
                entry["found"] = ok
                break
        report["sources"].append(entry)
        status = f"GEVONDEN {entry['found']['feed_url']} ({entry['found']['items']} items, laatste {entry['found']['latest']})" if entry["found"] else f"geen feed ({entry['page']})"
        print(f"{src['id']:<28} {status}")

    out = ROOT / "data" / "feed_discovery.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        lines = ["| Bron | Resultaat |", "|---|---|"]
        for e in report["sources"]:
            res = f"{e['found']['feed_url']} ({e['found']['items']} items)" if e["found"] else f"geen feed ({e['page']})"
            lines.append(f"| {e['id']} | {res} |")
        Path(summary).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
