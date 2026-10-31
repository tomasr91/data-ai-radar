"""Weekoverzicht voor bronnen die heel vaak kleine releases uitbrengen.

Claude Code brengt elke versie uit als patchrelease (v2.1.304, v2.1.305, ...), soms
meerdere per dag. Losse patches vallen weg via `minor_builds` in interests.yml. Voor
bronnen met `weekly_digest` in sources.yml maakt de pipeline daarom per afgeronde week
(maandag t/m zondag, UTC) één artikel dat alle releases van die week bundelt. De
geplande Claude-taak legt dat artikel uit zoals elk ander artikel, met alleen de
echt nieuwe functies.

Ook voor bronnen die elke week tientallen losse release notes publiceren (Azure Databricks)
werkt dit zo: de losse notes van zo'n bron verdwijnen uit de app (score.py, uitgesloten als
"weekoverzicht") en het weekoverzicht komt ervoor in de plaats. Zo vult één bron niet meer
de halve feed. Instellingen per bron onder `weekly_digest` in sources.yml:
  title          titel met {name}, {week} en {versions}
  unit           woord voor één item in de samenvatting (standaard "releases")
  list_versions  false als de titels geen versienummers zijn (standaard true)
"""
import re
from datetime import datetime, timedelta
from email.utils import format_datetime

from .normalize import clean_text, parse_date

WEEKS_BACK = 4   # zoveel afgeronde weken krijgen een overzicht
EXCERPT_PER_RELEASE = 200


def _week_start(dt: datetime) -> datetime:
    d = dt - timedelta(days=dt.weekday())
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def _version_key(title: str):
    return [int(n) for n in re.findall(r"\d+", title)] or [0]


def weekly_digests(items: list, conf, now: datetime) -> list:
    out = []
    current = _week_start(now)
    for src in conf.source_list:
        spec = src.get("weekly_digest")
        if not spec or not src.get("enabled"):
            continue
        weeks = {}
        for it in items:
            if it.get("source_id") != src["id"]:
                continue
            iso = parse_date(it.get("published_raw"))
            if not iso:
                continue
            start = _week_start(datetime.fromisoformat(iso.replace("Z", "+00:00")))
            if start < current and start >= current - timedelta(weeks=WEEKS_BACK):
                weeks.setdefault(start, []).append(it)
        for start, rel in sorted(weeks.items()):
            # Dezelfde note staat soms op twee pagina's (andere URL, zelfde titel): één keer meenemen.
            rel = list({r["title"].strip().lower(): r for r in rel}.values())
            rel.sort(key=lambda r: _version_key(r["title"]))
            year, week, _ = start.isocalendar()
            end = start + timedelta(days=7) - timedelta(seconds=1)
            versions = f"{rel[0]['title']} t/m {rel[-1]['title']}" if len(rel) > 1 else rel[0]["title"]
            count = f"{len(rel)} {spec.get('unit', 'releases')}"
            if spec.get("list_versions", True):
                count += f" ({versions})"
            notes = " · ".join(f"{r['title']}: {clean_text(r.get('excerpt', ''))[:EXCERPT_PER_RELEASE]}" for r in rel)
            out.append({
                "source_id": src["id"],
                "title": spec.get("title", "{name}: week {week}").format(name=src["name"], week=week, versions=versions),
                "url": f"{src['url'].rstrip('/')}?week={year}-W{week:02d}",
                "published_raw": format_datetime(end, usegmt=True),
                "fetched_at": max(r["fetched_at"] for r in rel),
                # Eerst de inhoud, dan de links (per pagina één keer, zonder #anker).
                "excerpt": f"Weekoverzicht van {count}. " + notes + ". Release notes: "
                           + ", ".join(dict.fromkeys(r["url"].split("#")[0] for r in rel)),
                "development_key": f"{src['id']}-{year}-W{week:02d}",
                "is_digest": True,
            })
    return out
