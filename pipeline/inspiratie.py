"""Inspiratie: één kaart per werkdag met 4 AI-ideeën (2 voor developers, 2 producten op silver/gold).

- Briefing van T: context/inspiratie.md. Nachttaak: taken/INSPIRATIE.md (na Verdiepen).
- Bestanden: data/inspiratie/<JJJJ-MM-DD>.json. De feed toont de laatste 14 dagen.
"""
import json
import re
from datetime import datetime, timedelta, timezone

from .config import DATA

DIR = DATA / "inspiratie"
KEEP_DAYS = 14
CATS = {"zelf": 2, "product": 2}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX = {"kort": 24, "naam": 70, "wat": 260, "waarom": 260, "tech": 120}


def _iso_ok(v) -> bool:
    try:
        datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate(data: dict, stem: str = None) -> list:
    p = []
    d = data.get("date")
    if not isinstance(d, str) or not DATE_RE.match(d):
        p.append("veld 'date' (JJJJ-MM-DD) ontbreekt")
    elif stem and d != stem:
        p.append(f"date '{d}' past niet bij bestandsnaam '{stem}'")
    if not _iso_ok(data.get("written_at", "")) or not data.get("written_at"):
        p.append("veld 'written_at' ontbreekt of is geen tijd")
    ideas = data.get("ideas")
    if not isinstance(ideas, list) or len(ideas) != sum(CATS.values()):
        return p + ["ideas moet precies 4 ideeën hebben"]
    count = {c: 0 for c in CATS}
    for i, x in enumerate(ideas, 1):
        if not isinstance(x, dict):
            p.append(f"idee {i} is geen object")
            continue
        if x.get("cat") not in CATS:
            p.append(f"idee {i}: cat moet 'zelf' of 'product' zijn")
        else:
            count[x["cat"]] += 1
        for f in ["naam", "wat", "waarom"]:
            if not isinstance(x.get(f), str) or not x[f].strip():
                p.append(f"idee {i}: veld '{f}' ontbreekt")
        for f, n in MAX.items():
            if isinstance(x.get(f), str) and len(x[f]) > n:
                p.append(f"idee {i}: '{f}' is langer dan {n} tekens")
        link = x.get("link")
        if link is not None and not (isinstance(link, str) and link.startswith("https://")):
            p.append(f"idee {i}: link moet met https:// beginnen")
    if count != CATS:
        p.append("precies 2 ideeën 'zelf' en 2 'product'")
    return p


def load_all(now=None, keep_days=KEEP_DAYS, folder=None):
    """(geldige kaarten nieuwste eerst, ongeldige [{file, problems}])."""
    folder = folder or DIR
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=keep_days)).date().isoformat()
    good, bad = [], []
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad.append({"file": f.name, "problems": [f"geen geldige JSON ({e})"]})
            continue
        problems = validate(data, f.stem)
        if problems:
            bad.append({"file": f.name, "problems": problems})
        elif data["date"] >= cutoff:
            good.append({"date": data["date"], "written_at": data["written_at"],
                         "ideas": [{k: x[k] for k in ["cat", "kort", "naam", "wat", "waarom", "tech", "link"] if x.get(k)}
                                   for x in data["ideas"]]})
    good.sort(key=lambda x: x["date"], reverse=True)
    return good, bad
