"""Normaliseren: uniforme velden, UTC-datums, stabiele id.

Een ruw item (van welke provider dan ook) heeft minimaal:
  source_id, title, url, published_raw (str|None), fetched_at (ISO), excerpt (str)
"""
import hashlib
import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMS = re.compile(r"^(utm_|ref$|source$|fbclid$|gclid$|mc_)")


def canonical_url(url: str) -> str:
    """Zelfde publicatie -> zelfde URL. Fragment blijft staan: in documentatie
    wijst een anker vaak naar een ander onderdeel."""
    parts = urlsplit(url.strip())
    scheme = "https" if parts.scheme in ("http", "https") else parts.scheme
    host = parts.netloc.lower().removeprefix("www.")
    path = re.sub(r"/+$", "", parts.path) or "/"
    # Locale-varianten van Microsoft Learn naar één vorm
    if host == "learn.microsoft.com":
        path = re.sub(r"^/[a-z]{2}-[a-z]{2}(?=/)", "", path)
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not TRACKING_PARAMS.match(k)])
    return urlunsplit((scheme, host, path, query, parts.fragment))


def article_id(url: str) -> str:
    return hashlib.sha1(canonical_url(url).encode()).hexdigest()[:12]


def parse_date(raw):
    """RFC 822 (RSS), ISO 8601 (Atom) of JJJJ-MM-DD -> ISO-string in UTC.
    Onbekend of onleesbaar -> None. Nooit terugvallen op de ophaaldatum."""
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError):
        dt = None
    if dt is None:
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(text: str, limit: int = 1200) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(title or "")).strip()


def normalize(raw: dict) -> dict:
    url = raw["url"].strip()
    return {
        "id": article_id(url),
        "title": clean_title(raw["title"]),
        "url": url,
        "canonical_url": canonical_url(url),
        "source_id": raw["source_id"],
        "published_at": parse_date(raw.get("published_raw")),
        "published_raw": raw.get("published_raw"),
        "fetched_at": raw["fetched_at"],
        "excerpt": clean_text(raw.get("excerpt", "")),
        "also_reported_by": [],
        **({"development_key": raw["development_key"]} if raw.get("development_key") else {}),
    }
