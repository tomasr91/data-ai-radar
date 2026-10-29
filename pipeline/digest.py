"""Weekoverzicht voor bronnen die heel vaak kleine releases uitbrengen.

Claude Code brengt elke versie uit als patchrelease (v2.1.304, v2.1.305, ...), soms
meerdere per dag. Losse patches vallen weg via `minor_builds` in interests.yml. Voor
bronnen met `weekly_digest` in sources.yml maakt de pipeline daarom per afgeronde week
(maandag t/m zondag, UTC) één artikel dat alle releases van die week bundelt. De
geplande Claude-taak legt dat artikel uit zoals elk ander artikel, met alleen de
echt nieuwe functies.
"""
import re
from datetime import datetime, timedelta
from email.utils import format_datetime

from .normalize import clean_text, parse_date

WEEKS_BACK = 4   # zoveel afgeronde weken krijgen een overzicht
EXCERPT_PER_RELEASE = 160


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
            rel.sort(key=lambda r: _version_key(r["title"]))
            year, week, _ = start.isocalendar()
            end = start + timedelta(days=7) - timedelta(seconds=1)
            versions = f"{rel[0]['title']} t/m {rel[-1]['title']}" if len(rel) > 1 else rel[0]["title"]
            notes = " · ".join(f"{r['title']}: {clean_text(r.get('excerpt', ''))[:EXCERPT_PER_RELEASE]}" for r in rel)
            out.append({
                "source_id": src["id"],
                "title": spec.get("title", "{name}: week {week}").format(name=src["name"], week=week, versions=versions),
                "url": f"{src['url'].rstrip('/')}?week={year}-W{week:02d}",
                "published_raw": format_datetime(end, usegmt=True),
                "fetched_at": max(r["fetched_at"] for r in rel),
                "excerpt": f"Weekoverzicht van {len(rel)} releases ({versions}). Release notes: "
                           + ", ".join(r["url"] for r in rel) + ". " + notes,
                "development_key": f"{src['id']}-{year}-W{week:02d}",
            })
    return out
