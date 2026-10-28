"""Data & AI Radar pipeline.

Stappen (elk in een eigen module):
  config     -> leest context/interests.yml en context/sources.yml
  providers  -> levert ruwe artikelen (feeds, momentopname; later een GitHub-repo)
  normalize  -> uniforme velden, UTC-datums, stabiele id
  dedupe     -> dubbele publicaties samenvoegen
  enrich     -> AI-uitleg (cache, optioneel API) volgens editorial-guide.md
  score      -> relevantiescore volgens interests.yml
  build      -> schrijft data/feed.json (het enige bestand dat de app leest)
"""
