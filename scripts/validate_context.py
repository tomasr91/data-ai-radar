"""Valideer de contextbestanden van de Data & AI Radar.

Gebruik: python scripts/validate_context.py  (vanuit de hoofdmap)
Exitcode 0 = geen fouten; waarschuwingen (zoals placeholders) blokkeren niet.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CTX = ROOT / "context"

REQUIRED_FILES = ["profile.md", "tech-stack.md", "projects.md",
                  "interests.yml", "sources.yml", "editorial-guide.md"]
TOPIC_FIELDS = ["id", "name", "description", "enabled", "priority", "keywords", "related_topics"]
SOURCE_FIELDS = ["id", "name", "url", "type", "topics", "priority", "enabled", "trust_level",
                 "language", "fetch_method", "verification"]

errors, warnings = [], []


def check_unique(items, label):
    ids = [i.get("id") for i in items]
    for dup in {i for i in ids if ids.count(i) > 1}:
        errors.append(f"{label}: dubbele id '{dup}'")
    return set(ids)


for name in REQUIRED_FILES + ["../README.md"]:
    if not (CTX / name).exists():
        errors.append(f"Bestand ontbreekt: {name}")

interests = yaml.safe_load((CTX / "interests.yml").read_text(encoding="utf-8"))
sources = yaml.safe_load((CTX / "sources.yml").read_text(encoding="utf-8"))

topics = interests.get("topics", [])
topic_ids = check_unique(topics, "interests")
excluded_ids = check_unique(interests.get("excluded_topics", []), "excluded_topics")
for clash in topic_ids & excluded_ids:
    errors.append(f"id '{clash}' staat zowel in topics als in excluded_topics")
levels = set(interests.get("priority_levels", {}))

group_ids = {g["id"] for g in interests.get("feed_groups", [])}
for t in topics:
    tid = t.get("id")
    if t.get("feed_group") not in group_ids:
        errors.append(f"interest '{tid}': feed_group '{t.get('feed_group')}' bestaat niet in feed_groups")
    for f in TOPIC_FIELDS:
        if f not in t:
            errors.append(f"interest '{tid}': veld '{f}' ontbreekt")
    if t.get("priority") not in levels:
        errors.append(f"interest '{tid}': priority {t.get('priority')} niet in 1-5")
    if not isinstance(t.get("enabled"), bool):
        errors.append(f"interest '{tid}': enabled moet true/false zijn")
    for rel in t.get("related_topics", []):
        if rel not in topic_ids:
            errors.append(f"interest '{tid}': onbekend related_topic '{rel}'")
        if rel == tid:
            errors.append(f"interest '{tid}': verwijst naar zichzelf")

defs = sources.get("definitions", {})
src_list = sources.get("sources", [])
check_unique(src_list, "sources")

for s in src_list:
    sid = s.get("id")
    for f in SOURCE_FIELDS:
        if f not in s:
            errors.append(f"source '{sid}': veld '{f}' ontbreekt")
    for field, key in [("type", "type"), ("trust_level", "trust_level"), ("fetch_method", "fetch_method")]:
        if s.get(field) not in defs.get(key, {}):
            errors.append(f"source '{sid}': ongeldige {field} '{s.get(field)}'")
    for tp in s.get("topics", []):
        if tp not in topic_ids:
            errors.append(f"source '{sid}': onbekend topic '{tp}'")
    status = (s.get("verification") or {}).get("status")
    if status not in defs.get("verification_status", {}):
        errors.append(f"source '{sid}': ongeldige verification.status '{status}'")
    if s.get("priority") not in range(1, 6):
        errors.append(f"source '{sid}': priority moet 1-5 zijn")
    if status == "user_supplied" and s.get("enabled"):
        warnings.append(f"bron aan maar niet zelf gecontroleerd: {sid}")
    if status == "to_verify":
        if s.get("enabled"):
            errors.append(f"source '{sid}': to_verify maar enabled: true")
        warnings.append(f"placeholder/te controleren bron: {sid}")
    if s.get("fetch_method") in ("rss", "atom") and not s.get("feed_url"):
        errors.append(f"source '{sid}': {s['fetch_method']} zonder feed_url")

covered = {tp for s in src_list if s.get("enabled") for tp in s.get("topics", [])}
for t in topics:
    if t.get("enabled") and t["priority"] >= 3 and t["id"] not in covered:
        warnings.append(f"geen ingeschakelde bron voor onderwerp '{t['id']}' (prioriteit {t['priority']})")

for w in warnings:
    print("WAARSCHUWING:", w)
for e in errors:
    print("FOUT:", e)
print(f"\n{len(topics)} onderwerpen, {len(src_list)} bronnen, {len(errors)} fouten, {len(warnings)} waarschuwingen")
sys.exit(1 if errors else 0)
