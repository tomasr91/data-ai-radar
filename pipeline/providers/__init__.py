"""Providers leveren ruwe artikelen. Elke provider heeft dezelfde vorm:

    collect(config) -> ProviderResult(items, source_results, mode, note)

items:          lijst ruwe dicts (source_id, title, url, published_raw, fetched_at, excerpt)
source_results: per bron {source_id, status, items, message, checked_at}
                status: ok | failed | not_supported | skipped | not_fetched
mode:           live | partial | snapshot | demo

Beschikbaar:
  feeds     - haalt RSS/Atom/GitHub-releases live op (feeds.py)
  snapshot  - leest een vastgelegde momentopname uit data/snapshot/ (snapshot.py)

Later: een provider die artikelbestanden uit een GitHub-repository leest.
Die hoeft alleen dezelfde ProviderResult terug te geven; normaliseren,
verrijken, scoren en de app blijven ongewijzigd.
"""
from dataclasses import dataclass, field


@dataclass
class ProviderResult:
    items: list
    source_results: list
    mode: str
    note: str = ""
    extra: dict = field(default_factory=dict)
