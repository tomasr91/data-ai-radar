"""Begrippen: korte uitleg van lastige termen, in het stuk zelf en verzameld op één plek.

Claude zet bij een uitleg of verdieping een lijst `terms` met de begrippen die T misschien nog
niet kent (beginnersniveau in ingestion, bundels en release pipelines):
    "terms": [{"term": "Auto Loader", "explanation": "Eén zin: wat het is en waarvoor."}, ...]
De app onderstreept de eerste keer dat het begrip in de tekst staat; tik erop voor de uitleg.
Alle begrippen samen staan in de app onder Verdieping > Begrippen (feed.json: "glossary").
"""
import re

MAX_TERMS = {"article": 5, "deepdive": 8}
MAX_TERM_LEN = 40
MAX_EXPLANATION = 240


def term_re(term: str):
    """Het begrip als los woord (niet midden in een ander woord), hoofdletters maken niet uit."""
    return re.compile(r"(?<![\w])" + re.escape(term.strip()) + r"(?![\w])", re.I)


def validate_terms(terms, text: str, kind: str = "article") -> list:
    if terms is None:
        return []
    if not isinstance(terms, list):
        return ["terms moet een lijst zijn"]
    p, seen = [], set()
    if len(terms) > MAX_TERMS[kind]:
        p.append(f"hooguit {MAX_TERMS[kind]} terms")
    for i, t in enumerate(terms):
        if not isinstance(t, dict) or not isinstance(t.get("term"), str) or not isinstance(t.get("explanation"), str):
            p.append(f"terms[{i}] moet term en explanation hebben")
            continue
        term, exp = t["term"].strip(), t["explanation"].strip()
        if not term or len(term) > MAX_TERM_LEN:
            p.append(f"terms[{i}]: term leeg of langer dan {MAX_TERM_LEN} tekens")
        if not exp or len(exp) > MAX_EXPLANATION:
            p.append(f"terms[{i}]: explanation leeg of langer dan {MAX_EXPLANATION} tekens")
        if term and not term_re(term).search(text or ""):
            p.append(f"terms[{i}]: '{term}' staat niet letterlijk in de tekst (nodig om het te kunnen aanwijzen)")
        if term.lower() in seen:
            p.append(f"terms[{i}]: '{term}' staat er dubbel in")
        seen.add(term.lower())
    return p


def article_text(a: dict) -> str:
    """De tekst waarin de app begrippen onderstreept: het verhaal (story)."""
    parts = list(a.get("story") or [])
    return " ".join(x for x in parts if isinstance(x, str))


def deepdive_text(d: dict) -> str:
    """De samenvatting bovenaan en de alinea's van de secties."""
    parts = [d.get("summary")]
    for s in d.get("sections") or []:
        if isinstance(s, dict):
            parts += list(s.get("paragraphs") or [])
    return " ".join(x for x in parts if isinstance(x, str))


def glossary(articles: list, deepdives: list) -> list:
    """Alle begrippen, alfabetisch. Bij hetzelfde begrip telt de nieuwste uitleg;
    `refs` wijst naar de stukken waar het in staat (nieuwste eerst)."""
    items = [("a", a["id"], a.get("headline") or a.get("title", ""), a.get("processed_at") or a.get("fetched_at") or "", a)
             for a in articles] + \
            [("v", d["id"], d.get("headline", ""), d.get("written_at") or "", d) for d in deepdives]
    items.sort(key=lambda x: x[3], reverse=True)
    out = {}
    for kind, id_, title, _, doc in items:
        for t in doc.get("terms") or []:
            key = t["term"].strip().lower()
            entry = out.setdefault(key, {"term": t["term"].strip(), "explanation": t["explanation"].strip(), "refs": []})
            if len(entry["refs"]) < 5:
                entry["refs"].append({"kind": kind, "id": id_, "title": title})
    return sorted(out.values(), key=lambda e: e["term"].lower())
