import re
from datetime import date, datetime

from parsers.base import BaseParser, Internship


class CanadianParser(BaseParser):
    """
    Parses negarprh/Canadian-Tech-Internships-2026 README.md

    Markdown table between <!-- BEGIN:INTERNSHIPS_TABLE --> and <!-- END:INTERNSHIPS_TABLE -->

    Row format:
    | Company | Role | Location | [![Apply](...)](URL) | Apr 13, 2026 |
    | ↳ | Another Role | Location | [![Apply](...)](URL) | Apr 13, 2026 |
    """

    _APPLY_RE = re.compile(r"\[!\[Apply\]\([^)]*\)\]\(([^)]+)\)")
    _DATE_RE = re.compile(r"([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})")

    def parse(self, content: str, today: date) -> list[Internship]:
        results: list[Internship] = []

        # Extract table section
        start_marker = "<!-- BEGIN:INTERNSHIPS_TABLE -->"
        start_idx = content.find(start_marker)
        if start_idx != -1:
            content = content[start_idx:]

        last_company = ""

        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue

            cells = line.split("|")
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) < 5:
                continue

            # Skip header and separator rows
            if cells[0] in ("Company", "--------") or cells[0].startswith("---"):
                continue

            # Check for closed
            if "\U0001f512" in line or "Closed" in cells[3]:
                # Still track company for ↳ rows
                if cells[0] != "↳":
                    last_company = cells[0]
                continue

            # Company (handle continuation rows)
            if cells[0] == "↳":
                company = last_company
            else:
                company = cells[0]
                last_company = company

            role = cells[1]
            location = cells[2]

            # Apply URL
            apply_match = self._APPLY_RE.search(cells[3])
            if not apply_match:
                continue
            apply_url = apply_match.group(1)

            # Date posted
            date_match = self._DATE_RE.search(cells[4])
            if not date_match:
                continue
            try:
                date_posted = datetime.strptime(
                    date_match.group(1), "%b %d, %Y"
                ).date()
            except ValueError:
                continue

            uid = Internship.make_uid("canadian", company, role, apply_url)
            results.append(
                Internship(
                    uid=uid,
                    company=company,
                    role=role,
                    location=location,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="canadian",
                    is_closed=False,
                )
            )

        return results
