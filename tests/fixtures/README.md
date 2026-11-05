# Vaste testdata

`feed.json` is een vastgelegde kopie van `data/feed.json` (met verdiepingen en keuzes erin) voor `tests/e2e_app.py`.
Zo breken de app-tests niet door nieuwe data uit de nacht.

Opnieuw vastleggen (alleen als de app nieuwe velden nodig heeft):

```
PYTHONPATH=. python3 -c "import json; from pipeline import config as c, deepdives as d; f=json.load(open('data/feed.json')); f['deepdives'],_=d.load_all(set(c.load().topics)); f['deepdive_options'],_=d.load_options(set(c.load().topics)); json.dump(f, open('tests/fixtures/feed.json','w'), ensure_ascii=False)"
```
