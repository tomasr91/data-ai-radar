"""Leest hoe ver T is met Dataflow uit zijn (privé) repository en schrijft data/voortgang.json.

Gebruik: python scripts/dataflow_status.py <pad naar clone van tomasr91/personal-data-platform>

Bronnen, in deze volgorde:
1. Commitberichten die beginnen met "Fase <n>" of "Fase <n>.<m>" (T's eigen werkwijze).
2. Bestanden die bij een fase horen (bijv. dbt/dbt_project.yml = fase 4 begonnen).
De hoogste fase die zo begonnen is, is "bezig"; de fases ervoor "klaar"; de rest "open".

Alleen fasenummers, status en de korte stapnaam uit het laatste fase-commit komen in de (openbare) radar.
Geen bestandsinhoud, paden of instellingen.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "voortgang.json"
FASE_RE = re.compile(r"^\s*fase\s+(\d+)(?:\.(\d+))?\s*[:\-–]?\s*(.*)$", re.I)
SIGNALS = [   # (fase, glob): bestaat er iets, dan is die fase begonnen
    (2, "platform/terraform/catalog.tf"),
    (3, "ingestion/*/*.py"),
    (4, "dbt/dbt_project.yml"),
    (4, "dbt/**/dbt_project.yml"),
    (5, "databricks.yml"),
    (5, "resources/*.yml"),
    (7, "agent/**/*.py"),
]
SAFE = re.compile(r"(https?://|\w+\.(cloud\.)?databricks\.com|/Volumes/|token|secret|password|@)", re.I)


def commits(repo: Path) -> list:
    out = subprocess.run(["git", "-C", str(repo), "log", "--format=%cs\t%s", "-n", "200"],
                         capture_output=True, text=True, check=True).stdout
    return [line.split("\t", 1) for line in out.splitlines() if "\t" in line]


def status(repo: Path, n_phases: int = 8) -> dict:
    cur, stap, op = 0, "", ""
    for day, subject in commits(repo):          # nieuwste eerst
        m = FASE_RE.match(subject)
        if m and 1 <= int(m.group(1)) <= n_phases:
            if int(m.group(1)) > cur:
                cur = int(m.group(1))
                nr = f"{m.group(1)}.{m.group(2)}" if m.group(2) else m.group(1)
                tekst = re.sub(r"\s+", " ", m.group(3)).strip()[:80]
                stap, op = (f"{nr} {tekst}".strip() if tekst and not SAFE.search(tekst) else nr), day
    for fase, pattern in SIGNALS:
        if fase > cur and any(p.is_file() for p in repo.glob(pattern)):
            cur, stap, op = fase, "", ""
    fases = {str(i): ("klaar" if i < cur else "bezig" if i == cur else "open") for i in range(1, n_phases + 1)}
    return {"bijgewerkt": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "huidig": cur or None,
            "stap": stap, "stap_op": op, "fases": fases}


def main() -> int:
    if len(sys.argv) != 2 or not (Path(sys.argv[1]) / ".git").exists():
        print("Gebruik: python scripts/dataflow_status.py <pad naar clone>")
        return 2
    sys.path.insert(0, str(ROOT))
    from pipeline.enrich import rode_draad
    data = status(Path(sys.argv[1]), len(rode_draad().get("phases", [])) or 8)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Dataflow: fase {data['huidig']} bezig ({data['stap'] or 'geen stapnaam'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
