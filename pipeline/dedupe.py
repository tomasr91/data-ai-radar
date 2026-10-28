"""Ontdubbelen in drie stappen:
1. Zelfde canonieke URL (bijv. via twee feeds van dezelfde leverancier).
2. Vrijwel gelijke titel bij verschillende bronnen.
3. Zelfde ontwikkeling (development_key uit de verrijking): verschillende
   berichten over één ontwikkeling worden gegroepeerd, niet weggegooid.
Het artikel van de bron met de hoogste trust/prioriteit blijft het hoofdartikel.
"""
import re

TRUST_RANK = {"high": 3, "medium": 2, "low": 1}
STOP = {"the", "a", "an", "and", "of", "to", "in", "for", "on", "with", "is", "now", "de", "het", "een", "en", "van"}


def _tokens(title: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP}


def similar(a: str, b: str, threshold: float = 0.8) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= threshold


def _rank(article, sources):
    src = sources.get(article["source_id"], {})
    return (TRUST_RANK.get(src.get("trust_level"), 0), src.get("priority", 0),
            article.get("processing_status") == "enriched")


def _merge(primary, other, reason):
    primary["also_reported_by"].append({
        "source_id": other["source_id"], "title": other["title"], "url": other["url"],
        "published_at": other.get("published_at"), "reason": reason,
    })
    primary["also_reported_by"].extend(other.get("also_reported_by", []))


def dedupe(articles: list, sources: dict) -> tuple:
    """Geeft (unieke artikelen, aantal samengevoegd)."""
    kept: list = []
    merged = 0
    for art in sorted(articles, key=lambda a: _rank(a, sources), reverse=True):
        match = None
        for k in kept:
            if k["canonical_url"] == art["canonical_url"]:
                match, reason = k, "zelfde URL"
            elif k["source_id"] != art["source_id"] and similar(k["title"], art["title"]):
                match, reason = k, "vrijwel gelijke titel"
            elif art.get("development_key") and k.get("development_key") == art["development_key"]:
                match, reason = k, "zelfde ontwikkeling"
            if match:
                break
        if match:
            _merge(match, art, reason)
            merged += 1
        else:
            kept.append(art)
    return kept, merged
