"""Opnieuw samenstellen zonder ophalen: leest de artikelen uit data/archive.json (van de laatste keer
ophalen) en de bronstatus uit de vorige feed. Voor builds na een opslag van de nachttaak of na
feedback: dan is er niets nieuws op te halen, alleen de feed opnieuw te bouwen (T, 5-11-2026)."""
import json

from . import ProviderResult
from ..config import DATA


def collect(config, archive_path=DATA / "archive.json", feed_path=DATA / "feed.json") -> ProviderResult:
    archive = json.loads(archive_path.read_text(encoding="utf-8")) if archive_path.exists() else {"items": {}}
    prev = json.loads(feed_path.read_text(encoding="utf-8")) if feed_path.exists() else {}
    results = [{"source_id": s["id"], "status": s.get("status", "not_fetched"), "items": s.get("items", 0),
                "message": s.get("message"), "checked_at": s.get("checked_at")} for s in prev.get("sources", [])]
    return ProviderResult(items=list(archive.get("items", {}).values()), source_results=results,
                          mode=prev.get("mode", "live") if prev.get("mode") in ("live", "partial") else "live",
                          note="Opnieuw samengesteld uit de laatste keer ophalen.",
                          extra={"captured_at": prev.get("last_successful_update")})
