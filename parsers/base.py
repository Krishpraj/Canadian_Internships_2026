from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class Internship:
    uid: str
    company: str
    role: str
    location: str
    apply_url: str
    date_posted: date
    source: str
    is_closed: bool

    @staticmethod
    def make_uid(source: str, company: str, role: str, apply_url: str) -> str:
        raw = f"{source}|{company}|{role}|{apply_url}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str, today: date) -> list[Internship]:
        ...
