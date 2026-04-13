import re
from datetime import date, timedelta

from parsers.base import BaseParser, Internship


class SpeedyApplyParser(BaseParser):
    """
    Parses speedyapply/2026-SWE-College-Jobs README.md

    Row format (pipe-delimited with HTML):
    | <a href="URL"><strong>Company</strong></a> | Position | Location | Salary | <a href="APPLY_URL"><img .../></a> | 33d |
    """

    _COMPANY_RE = re.compile(r'<a href="([^"]+)"><strong>([^<]+)</strong></a>')
    _APPLY_RE = re.compile(r'<a href="([^"]+)"><img ')
    _AGE_RE = re.compile(r"(\d+)d")

    def parse(self, content: str, today: date) -> list[Internship]:
        results: list[Internship] = []

        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("|") or "<a href=" not in line:
                continue

            cells = line.split("|")
            # Remove empty first/last from leading/trailing pipes
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) < 5:
                continue

            # Extract company
            company_match = self._COMPANY_RE.search(cells[0])
            if not company_match:
                continue
            company = company_match.group(2).strip()

            role = cells[1].strip()
            location = cells[2].strip()

            # Apply URL from the posting cell (second to last or varies)
            apply_match = self._APPLY_RE.search(line)
            if not apply_match:
                continue
            apply_url = apply_match.group(1)

            # Age from last cell
            age_match = self._AGE_RE.search(cells[-1])
            if not age_match:
                continue
            days_ago = int(age_match.group(1))
            date_posted = today - timedelta(days=days_ago)

            uid = Internship.make_uid("speedyapply", company, role, apply_url)
            results.append(
                Internship(
                    uid=uid,
                    company=company,
                    role=role,
                    location=location,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="speedyapply",
                    is_closed=False,
                )
            )

        return results
