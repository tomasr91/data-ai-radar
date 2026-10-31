"""AI-verrijking volgens context/editorial-guide.md.

Elk artikel wordt hoogstens één keer verwerkt: het resultaat staat in
data/enrichment/<article_id>.json en wordt daarna hergebruikt.

- Met ANTHROPIC_API_KEY: nieuwe artikelen zonder cache worden via de API verwerkt.
- Zonder sleutel: alleen bestaande cachebestanden worden gebruikt; andere
  artikelen blijven 'raw' (titel, bron, datum) en de app blijft werken.

Alleen openbare publicaties gaan naar de API, plus de eigen contextbestanden.
Nooit patiëntgegevens of interne documenten.
"""
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone

from .config import CONTEXT, DATA

CACHE = DATA / "enrichment"
PROMPT_VERSION = "2026-10-28.2"
API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-5-5"

TEXT_FIELDS = ["summary", "what_is_new", "simple_explanation", "practical_example",
               "personal_relevance", "practical_application", "experiment"]
STATUSES = {"beschikbaar", "preview", "aangekondigd", "experimenteel", "onbekend"}
ARTICLE_TYPES = {"nieuws", "opinie"}


def context_hash() -> str:
    h = hashlib.sha1()
    for name in ["profile.md", "tech-stack.md", "projects.md", "editorial-guide.md", "interests.yml"]:
        h.update((CONTEXT / name).read_bytes())
    return h.hexdigest()[:10]


def load_cached(article_id: str):
    path = CACHE / f"{article_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def validate(data: dict, topic_ids: set) -> list:
    """Geeft een lijst problemen; leeg = geldig.

    Twee formaten:
      1 = losse secties (what_is_new, simple_explanation, ...), het oorspronkelijke formaat
      2 = Nederlandse kop + doorlopend verhaal + bronfeiten (format_version: 2)
    """
    problems = []
    if data.get("format_version") == 2:
        for f in ["headline", "summary", "personal_relevance", "experiment"]:
            if not isinstance(data.get(f), str) or not data[f].strip():
                problems.append(f"veld '{f}' ontbreekt")
        if isinstance(data.get("headline"), str) and len(data["headline"]) > 90:
            problems.append("headline is langer dan 90 tekens")
        story = data.get("story")
        if not isinstance(story, list) or not 2 <= len(story) <= 6 or not all(isinstance(x, str) and x.strip() for x in story):
            problems.append("story moet een lijst van 2 tot 6 alinea's zijn")
        facts = data.get("key_facts")
        if not isinstance(facts, list) or not facts or not all(isinstance(x, str) and x.strip() for x in facts):
            problems.append("key_facts moet een niet-lege lijst met feiten uit de bron zijn")
    else:
        for f in ["summary", "what_is_new", "personal_relevance"]:
            if not isinstance(data.get(f), str) or not data[f].strip():
                problems.append(f"veld '{f}' ontbreekt")
        for f in TEXT_FIELDS:
            if f in data and data[f] is not None and not isinstance(data[f], str):
                problems.append(f"veld '{f}' moet tekst zijn")
    kind = data.get("article_type", "nieuws")
    if kind not in ARTICLE_TYPES:
        problems.append(f"ongeldig article_type '{kind}' (nieuws of opinie)")
    elif kind == "opinie" and not (isinstance(data.get("author"), str) and data["author"].strip()):
        problems.append("bij article_type 'opinie' is 'author' verplicht")
    if data.get("availability_status") not in STATUSES:
        problems.append(f"ongeldige availability_status '{data.get('availability_status')}'")
    if not isinstance(data.get("limitations", []), list):
        problems.append("limitations moet een lijst zijn")
    unknown = [t for t in data.get("topics", []) if t not in topic_ids]
    if unknown:
        problems.append(f"onbekende topics {unknown}")
    from .practice import validate_showcase
    problems += validate_showcase(data.get("showcase"))
    q = data.get("quality", {})
    for k in ["depth", "practicality", "novelty"]:
        if not isinstance(q.get(k), (int, float)) or not 0 <= q[k] <= 1:
            problems.append(f"quality.{k} moet tussen 0 en 1 liggen")
    return problems


def attach(article: dict, cached: dict) -> None:
    for k in TEXT_FIELDS + ["availability_status", "limitations", "official_docs", "topics",
                            "quality", "development_key", "exceptional", "date_note",
                            "format_version", "headline", "story", "key_facts", "article_type", "author",
              "showcase"]:
        if k in cached and cached[k] not in (None, ""):
            article[k] = cached[k]
    article["processing_status"] = "enriched"
    article["processed_by"] = cached.get("processed_by", "onbekend")
    article["processed_at"] = cached.get("processed_at")


def _prompt(article: dict, topic_ids: list) -> str:
    ctx = "\n\n".join(f"### {n}\n{(CONTEXT / n).read_text(encoding='utf-8')}"
                      for n in ["profile.md", "tech-stack.md", "projects.md", "editorial-guide.md"])
    return f"""Je verwerkt één openbaar nieuwsbericht voor de persoonlijke nieuwsfeed Data & AI Radar.
Volg de redactiegids en gebruik het profiel. Verzin niets: gebruik alleen wat in de brontekst staat.
Staat iets niet in de bron, laat het veld dan leeg ("") in plaats van te speculeren.

{ctx}

### Artikel
Titel: {article['title']}
Bron-URL: {article['url']}
Publicatiedatum (feed): {article.get('published_raw')}
Brontekst (uit feed, mogelijk ingekort):
{article.get('excerpt') or '(geen tekst in de feed)'}

### Antwoord
Schrijf volgens formaat 2 uit de redactiegids. Geef uitsluitend JSON met deze velden:
format_version (2), headline (Nederlandse kop, max. ~70 tekens), summary (1-2 zinnen),
story (lijst van 3-5 korte alinea's), key_facts (lijst feiten uit de bron), personal_relevance (1 zin),
experiment (past binnen een middag, nooit met patiëntgegevens), limitations (lijst korte zinnen),
availability_status (beschikbaar|preview|aangekondigd|experimenteel|onbekend), official_docs (lijst {{label,url}}
alleen met URL's uit de brontekst), topics (subset van {topic_ids}),
quality {{depth, practicality, novelty}} (0..1), development_key (korte sleutel voor de ontwikkeling),
exceptional (true alleen bij een grote, bevestigde wijziging in de eigen stack)."""


def call_api(article: dict, topic_ids: list, api_key: str) -> dict:
    body = json.dumps({
        "model": os.environ.get("RADAR_MODEL", DEFAULT_MODEL),
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": _prompt(article, topic_ids)}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.loads(resp.read())
    text = "".join(b.get("text", "") for b in payload.get("content", []))
    start, end = text.find("{"), text.rfind("}")
    if start < 0:
        raise ValueError("antwoord bevat geen JSON")
    return json.loads(text[start:end + 1])


def enrich_new(articles: list, topic_ids: set, limit: int, api_key=None, caller=call_api) -> dict:
    """Verwerkt maximaal `limit` artikelen zonder cache (in de gegeven volgorde)."""
    api_key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY")
    report = {"api_key_present": bool(api_key), "processed": 0, "failed": [], "skipped_no_key": 0}
    todo = [a for a in articles if a.get("processing_status") != "enriched"]
    if not api_key:
        report["skipped_no_key"] = len(todo)
        return report
    CACHE.mkdir(parents=True, exist_ok=True)
    for art in todo[:limit]:
        try:
            data = caller(art, sorted(topic_ids), api_key)
            problems = validate(data, topic_ids)
            if problems:
                raise ValueError("; ".join(problems))
            data.update({
                "article_id": art["id"], "url": art["url"],
                "processed_by": os.environ.get("RADAR_MODEL", DEFAULT_MODEL) + " (API)",
                "processed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "prompt_version": PROMPT_VERSION, "context_hash": context_hash(),
            })
            (CACHE / f"{art['id']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            attach(art, data)
            report["processed"] += 1
        except Exception as e:  # één mislukte verrijking mag de run niet stoppen
            report["failed"].append({"id": art["id"], "title": art["title"], "error": str(e)[:200]})
    return report
