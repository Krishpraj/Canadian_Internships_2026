from parsers.base import BaseParser
from parsers.speedyapply import SpeedyApplyParser
from parsers.simplifyjobs import SimplifyJobsParser
from parsers.pittcsc import PittCSCParser
from parsers.canadian import CanadianParser

_PARSERS: dict[str, BaseParser] = {
    "speedyapply": SpeedyApplyParser(),
    "simplifyjobs": SimplifyJobsParser(),
    "pittcsc": PittCSCParser(),
    "canadian": CanadianParser(),
}


def get_parser(name: str) -> BaseParser:
    return _PARSERS[name]
