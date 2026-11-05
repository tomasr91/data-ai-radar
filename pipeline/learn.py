"""Leren van T's duimen als correctie op de score (plan 5-11-2026, claude/plan-score-correcties.md).

Een duim zegt of de score klopte:
- 👍 = "dit hoort rond 85"; met reden "score te laag" telt hij 1,5 keer.
- 👎 met reden over het onderwerp (geen interesse, niet mijn stack) = "dit hoort rond 30".
- 👎 met reden "score te hoog" = "dit hoort rond 40", telt 1,5 keer.
- 👎 zonder reden of om de kwaliteit (te basic, te vaag, oud nieuws) gaat over dát artikel:
  alleen de soort artikel leert ervan.
- Helemaal gelezen (zonder duim) = een kwart duim omhoog.
Afwijking = doelscore min de score op het moment van de duim. Een duim op 92 leert dus niets
(een duim omhoog duwt nooit omlaag), een duim op 55 veel.

Vier niveaus, van specifiek naar breed. Hoe specifieker, hoe sneller het leert en hoe zwaarder het
mag tellen. Per niveau: effect = som(gewicht x afwijking) / (som(gewicht) + K). Bij één duim is dat
1/(1+K) van de afwijking; bij veel duimen loopt het op naar de gemiddelde afwijking.

  niveau                    eerste duim   maximaal
  vergelijkbaar artikel        ~60%         ±20
  zelfde label                 ~40%         ±15
  zelfde onderwerp             ~15%         ±10
  zelfde bron of soort         ~10%          ±5

De niveaus overlappen (een vergelijkbaar artikel heeft vaak hetzelfde label en onderwerp). Daarom
telt het sterkste niveau volledig, het tweede half, het derde een kwart, enzovoort; samen hooguit ±20.
Duimen vervagen: na 60 dagen tellen ze half.
"""
import math
import re
from datetime import datetime, timezone

HALF_LIFE_DAYS = 60
TARGET_UP, TARGET_DOWN, TARGET_TOO_HIGH = 0.85, 0.30, 0.40
TOPIC_DOWN = {"geen_interesse", "niet_mijn_stack"}
READ_WEIGHT = 0.25
STRONG = 1.5   # "score te laag" / "score te hoog"
DEFAULT_SCORE = 0.70   # duim zonder bekende score (van vóór 5-11-2026)

# K (hoe snel) en maximum per niveau, als fractie van 100 punten
LEVELS = {
    "similar": (0.67, 0.20),
    "label": (1.5, 0.15),
    "topic": (5.7, 0.10),
    "source": (9.0, 0.05),
    "kind": (9.0, 0.05),
}
TOTAL_CAP = 0.20
SIM_MIN = 0.25   # minder overeenkomst dan dit telt niet als vergelijkbaar

STOP = set("""the a an and of to in for on with is are be by from at as or it this that your you we our how what why
now new can will into more than when which who using use used via about over not but also its their they all one
de het een en van in op met voor is zijn dat die dit je jouw we ons hoe wat waarom nu nieuw kan wordt naar meer
dan als bij uit om ook niet maar door aan te er zo nog wel""".split())


def _tokens(text: str) -> dict:
    out = {}
    for w in re.findall(r"[a-z0-9][a-z0-9\-]{2,}", (text or "").lower()):
        if w not in STOP:
            out[w] = out.get(w, 0) + 1
    return out


def _cosine(a: dict, b: dict) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _jaccard(a, b) -> float:
    a, b = set(a or []), set(b or [])
    return len(a & b) / len(a | b) if a and b else 0.0


def text_of(a: dict) -> str:
    """Tekst voor de vergelijking: koppen, samenvatting, feiten en labels."""
    parts = [a.get("title", ""), a.get("headline", ""), a.get("summary", ""), " ".join(a.get("key_facts", []) or []),
             " ".join(a.get("labels", []) or []), a.get("text", "")]
    return " ".join(p for p in parts if p)


def similarity(a: dict, b: dict) -> float:
    """0-1. Labels wegen het zwaarst; zonder labels alleen de woorden."""
    j = _jaccard(a.get("labels"), b.get("labels"))
    c = _cosine(a.get("_tok") or _tokens(text_of(a)), b.get("_tok") or _tokens(text_of(b)))
    return 0.6 * j + 0.4 * c if (a.get("labels") and b.get("labels")) else c


def _age(at: str, now) -> float:
    try:
        dt = datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    except ValueError:
        return 1.0
    return math.pow(0.5, max(0.0, (now - dt).days) / HALF_LIFE_DAYS)


def examples(fb_data: dict, now=None) -> list:
    """Elke duim (en elk gelezen artikel zonder duim) als leervoorbeeld met afwijking en gewicht."""
    now = now or datetime.now(timezone.utc)
    out = []
    votes = fb_data.get("votes", {})
    for aid, v in votes.items():
        s = v.get("s")
        s = s / 100 if isinstance(s, (int, float)) else DEFAULT_SCORE
        r, vote = v.get("r"), v.get("v")
        levels = set(LEVELS)
        if vote == 1:
            target, w = TARGET_UP, STRONG if r == "score_te_laag" else 1.0
        elif r == "score_te_hoog":
            target, w = TARGET_TOO_HIGH, STRONG
        elif r in TOPIC_DOWN:
            target, w = TARGET_DOWN, 1.0
        elif vote == -1:
            target, w, levels = TARGET_DOWN, 1.0, {"kind"}   # over dít artikel: alleen de soort
        else:
            continue
        # Een duim omhoog duwt nooit omlaag (ook niet bij een score boven 85), een duim omlaag nooit omhoog.
        err = max(0.0, target - s) if vote == 1 else min(0.0, target - s)
        out.append(_example(aid, v, err, w * _age(v.get("at", ""), now), levels, vote, s))
    for aid, r in fb_data.get("reads", {}).items():
        if aid in votes:
            continue
        s = r.get("s")
        s = s / 100 if isinstance(s, (int, float)) else DEFAULT_SCORE
        out.append(_example(aid, r, max(0.0, TARGET_UP - s), READ_WEIGHT * _age(r.get("at", ""), now), set(LEVELS), 0, s))
    return out


def _example(aid, x, err, w, levels, vote, s):
    return {"id": aid, "title": x.get("title", ""), "e": err, "w": w, "levels": levels, "v": vote, "s": s,
            "labels": x.get("labels", []) or [], "topics": (x.get("topics") or [])[:2], "source_id": x.get("source_id"),
            "soort": x.get("soort"), "_tok": _tokens(text_of(x))}


def _shrunk(pairs, k, cap):
    """pairs: [(gewicht, afwijking)] -> begrensd effect met krimp naar 0 bij weinig duimen."""
    sw = sum(w for w, _ in pairs)
    if sw <= 0:
        return 0.0
    eff = sum(w * e for w, e in pairs) / (sw + k)
    return max(-cap, min(cap, eff))


def model(fb_data: dict, now=None) -> dict:
    ex = examples(fb_data, now)
    agg = {"label": {}, "topic": {}, "source": {}, "kind": {}}
    for x in ex:
        if "label" in x["levels"]:
            for lab in x["labels"]:
                agg["label"].setdefault(lab, []).append((x["w"], x["e"]))
        if "topic" in x["levels"]:
            for t in x["topics"]:
                agg["topic"].setdefault(t, []).append((x["w"], x["e"]))
        if "source" in x["levels"] and x["source_id"]:
            agg["source"].setdefault(x["source_id"], []).append((x["w"], x["e"]))
        if "kind" in x["levels"] and x["soort"]:
            agg["kind"].setdefault(x["soort"], []).append((x["w"], x["e"]))
    levels = {lvl: {key: _shrunk(p, *LEVELS[lvl]) for key, p in d.items()} for lvl, d in agg.items()}
    return {"examples": [x for x in ex if "similar" in x["levels"]], "levels": levels}


def effect(article: dict, m: dict):
    """(effect als fractie van 100 punten, uitleg) voor één artikel."""
    if not m or (not m["examples"] and not any(m["levels"].values())):
        return 0.0, None
    contrib = []   # (waarde, uitleg)
    a = dict(article)
    a["_tok"] = _tokens(text_of(article))
    near = [(similarity(a, x), x) for x in m["examples"]]
    near = [(s, x) for s, x in near if s >= SIM_MIN]
    if near:
        k, cap = LEVELS["similar"]
        val = _shrunk([(s * x["w"], x["e"]) for s, x in near], k, cap)
        best = max(near, key=lambda sx: sx[0] * x_abs(sx[1]))
        contrib.append((val, {"by": "similar", "title": best[1]["title"], "id": best[1]["id"], "v": best[1]["v"],
                              "s": round(best[1]["s"] * 100)}))
    L = m["levels"]
    labs = [(L["label"][lab], lab) for lab in article.get("labels", []) or [] if lab in L["label"]]
    if labs:
        contrib.append((sum(v for v, _ in labs) / len(labs), {"by": "label", "name": max(labs, key=lambda x: abs(x[0]))[1]}))
    tops = [(L["topic"][t], t) for t in (article.get("topics") or [])[:2] if t in L["topic"]]
    if tops:
        contrib.append((sum(v for v, _ in tops) / len(tops), {"by": "topic", "name": max(tops, key=lambda x: abs(x[0]))[1]}))
    if article.get("source_id") in L["source"]:
        contrib.append((L["source"][article["source_id"]], {"by": "source", "name": article["source_id"]}))
    if article.get("soort") in L["kind"]:
        contrib.append((L["kind"][article["soort"]], {"by": "kind", "name": article["soort"]}))
    contrib = [c for c in contrib if abs(c[0]) >= 0.005]
    if not contrib:
        return 0.0, None
    contrib.sort(key=lambda c: -abs(c[0]))
    total = sum(v * (0.5 ** i) for i, (v, _) in enumerate(contrib))
    total = max(-TOTAL_CAP, min(TOTAL_CAP, total))
    return total, {**contrib[0][1], "pts": round(total * 100)}


def x_abs(x):
    return abs(x["e"]) * x["w"]


def summary(fb_data: dict, m: dict, now=None) -> dict:
    """Voor de app: per niveau de punten, de afwijking van je duimen en de grootste verrassingen."""
    now = now or datetime.now(timezone.utc)
    lv = {lvl: {k: round(v * 100) for k, v in d.items() if round(v * 100)} for lvl, d in m["levels"].items()}

    def dev(lo, hi):
        errs = []
        for v in fb_data.get("votes", {}).values():
            if not isinstance(v.get("s"), (int, float)) or v.get("v") != 1 and v.get("r") not in TOPIC_DOWN | {"score_te_hoog"}:
                continue
            try:
                age = (now - datetime.fromisoformat(str(v.get("at")).replace("Z", "+00:00"))).days
            except ValueError:
                continue
            if lo <= age < hi:
                tgt = TARGET_UP if v["v"] == 1 else TARGET_TOO_HIGH if v.get("r") == "score_te_hoog" else TARGET_DOWN
                errs.append(max(0.0, tgt * 100 - v["s"]) if v["v"] == 1 else max(0.0, v["s"] - tgt * 100))
        return (round(sum(errs) / len(errs)), len(errs)) if errs else (None, 0)
    now_dev, n_now = dev(0, 30)
    before_dev, n_before = dev(30, 60)
    surprises = sorted([{"id": k, "title": v.get("title", ""), "s": v["s"]} for k, v in fb_data.get("votes", {}).items()
                        if v.get("v") == 1 and isinstance(v.get("s"), (int, float)) and v["s"] <= 60],
                       key=lambda x: x["s"])[:5]
    return {"levels": lv, "deviation": {"now": now_dev, "n": n_now, "before": before_dev, "n_before": n_before},
            "surprises": surprises}
