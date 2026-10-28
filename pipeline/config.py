"""Leest de contextbestanden. De pipeline schrijft nooit in context/."""
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = ROOT / "context"
DATA = ROOT / "data"


@dataclass
class Config:
    interests: dict
    sources: dict

    @property
    def topics(self) -> dict:
        return {t["id"]: t for t in self.interests["topics"] if t.get("enabled", True)}

    @property
    def all_topics(self) -> dict:
        return {t["id"]: t for t in self.interests["topics"]}

    @property
    def excluded_topics(self) -> list:
        return self.interests.get("excluded_topics", [])

    @property
    def feed_groups(self) -> list:
        return self.interests.get("feed_groups", [])

    @property
    def scoring(self) -> dict:
        return self.interests.get("scoring", {})

    @property
    def source_list(self) -> list:
        return self.sources["sources"]

    def source(self, source_id: str) -> dict:
        for s in self.source_list:
            if s["id"] == source_id:
                return s
        raise KeyError(source_id)


def load(context_dir: Path = CONTEXT) -> Config:
    def read(name):
        return yaml.safe_load((context_dir / name).read_text(encoding="utf-8"))
    return Config(interests=read("interests.yml"), sources=read("sources.yml"))
