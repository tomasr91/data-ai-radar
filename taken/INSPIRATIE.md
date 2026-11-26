# Taak: Inspiratie (na Verdiepen, alleen op werkdagen)

Eén kaart met vier AI-ideeën voor T. Houd het zuinig: dit hoort weinig tijd en tokens te kosten.

1. Draai `python scripts/inspiratie_status.py`. Bij `NIET NU`: niets doen, ga verder met je taakverslag.
2. Lees `context/inspiratie.md` (de briefing) en de lijst "Al geweest" en de duimpjes uit stap 1. Herhaal niets: geen idee, product of link dat al geweest is. Doe meer in de richting van 👍 en minder van 👎.
3. Zoek met **hooguit 5 WebSearch-zoekopdrachten**. Gebruik geen WebFetch. Een link mag alleen als hij letterlijk in de zoekresultaten van deze nacht staat; anders geen link. Verzin geen producten, cijfers of feiten.
4. Schrijf `data/inspiratie/<datum>.json` (datum in Nederlandse tijd, `TZ=Europe/Amsterdam date +%F`):

```json
{"date": "2026-11-24", "written_at": "2026-11-24T04:20:00Z", "processed_by": "claude",
 "ideas": [
  {"cat": "zelf", "kort": "…", "naam": "…", "wat": "…", "waarom": "…", "tech": "…", "link": "https://…"},
  {"cat": "zelf", "kort": "…", "naam": "…", "wat": "…", "waarom": "…", "tech": "…"},
  {"cat": "product", "kort": "…", "naam": "…", "wat": "…", "waarom": "…", "tech": "…", "link": "https://…"},
  {"cat": "product", "kort": "…", "naam": "…", "wat": "…", "waarom": "…", "tech": "…"}]}
```

   Precies 2 `zelf` (AI voor developers zoals T) en 2 `product` (producten op silver- en gold-modellen), in die volgorde; zie de briefing. Geen specifieke ziekenhuistoepassingen. `kort` is het label op de kaart: 2 tot 4 woorden, hooguit 24 tekens (bijv. "Vragen aan je gold-laag"). Kort: `wat` en `waarom` elk één of twee zinnen. Eenvoudig Nederlands.
5. `python scripts/validate_enrichment.py` moet `0 fout` geven. Commit alleen dat bestand ("Inspiratie <datum>"), `git pull --rebase`, `git push`.
6. Zet in je taakverslag in `counts` ook `"inspiratie": 1` (of 0) en noem het kort in `summary`.
