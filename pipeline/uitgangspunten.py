"""context/uitgangspunten.md: T's uitgangspunten (wel / niet interessant / twijfel), als lijst voor de app.

Elke regel ("- ...") onder een kopje "## ..." krijgt een vast id (eerste 8 tekens van sha1 van de tekst),
zodat T hem in de app kan weghalen (✕); scripts/collect_feedback.py haalt die regel dan meteen uit het bestand.
"""
import hashlib
import re

from .config import ROOT

PATH = ROOT / "context" / "uitgangspunten.md"
MAX_LINES = 30


def line_id(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:8]


def load(path=None) -> list:
    path = path or PATH
    if not path.exists():
        return []
    out, kop = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("## "):
            kop = raw[3:].strip()
        elif kop and re.match(r"^\s*[-*] \S", raw):
            text = re.sub(r"^\s*[-*] ", "", raw).strip()
            out.append({"id": line_id(text), "kop": kop, "text": text})
    return out


def remove(ids, path=None) -> int:
    """Haal regels met deze id's uit het bestand. Geeft het aantal weggehaalde regels."""
    path = path or PATH
    if not path.exists() or not ids:
        return 0
    ids, n, keep = set(ids), 0, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*[-*] (\S.*)$", raw)
        if m and line_id(m.group(1)) in ids:
            n += 1
            continue
        keep.append(raw)
    if n:
        path.write_text("\n".join(keep) + "\n", encoding="utf-8")
    return n
