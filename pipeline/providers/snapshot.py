"""Momentopname: echte artikelen die eenmalig buiten de pipeline zijn opgehaald
(bijv. door Claude in een sessie zonder netwerktoegang voor de pipeline).
Bestand: data/snapshot/raw_items.json
"""
import json
from pathlib import Path

from . import ProviderResult
from ..config import DATA


def collect(config, path: Path = DATA / "snapshot" / "raw_items.json") -> ProviderResult:
    snap = json.loads(path.read_text(encoding="utf-8"))
    known = {s["source_id"] for s in snap["source_results"]}
    results = list(snap["source_results"])
    for src in config.source_list:
        if src.get("enabled") and src["id"] not in known:
            results.append({"source_id": src["id"], "status": "not_fetched", "items": 0,
                            "message": "Niet opgenomen in deze momentopname.", "checked_at": snap["captured_at"]})
    return ProviderResult(items=snap["items"], source_results=results, mode="snapshot",
                          note=snap["note"], extra={"captured_at": snap["captured_at"]})
