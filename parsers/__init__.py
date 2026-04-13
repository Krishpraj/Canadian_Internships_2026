from parsers.base import BaseParser
from parsers.speedyapply import SpeedyApplyParser
from parsers.simplifyjobs import SimplifyJobsParser
from parsers.canadian import CanadianParser

_PARSERS: dict[str, BaseParser] = {
    "speedyapply": SpeedyApplyParser(),
    "simplifyjobs": SimplifyJobsParser(),
    "canadian": CanadianParser(),
}


def get_parser(name: str) -> BaseParser:
    return _PARSERS[name]
