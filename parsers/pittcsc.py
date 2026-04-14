import re
from datetime import date, timedelta

from parsers.base import BaseParser, Internship


class PittCSCParser(BaseParser):
    """
    Parses pittcsc/Summer2026-Internships README.md

    Uses HTML <table> with <tr> rows. Each data row has:
    <td><strong><a href="...">Company</a></strong></td>
    <td>Role</td>
    <td>Location</td>
    <td><div align="center"><a href="APPLY_URL">...</a> <a href="SIMPLIFY_URL">...</a></div></td>
    <td>2d</td>
    """

    _TR_RE = re.compile(r"<tr>(.*?)</tr>", re.DOTALL)
    _TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)
    _COMPANY_RE = re.compile(r'<a href="[^"]*">([^<]+)</a>')
    _APPLY_RE = re.compile(r'<a href="([^"]+)">')
    _AGE_RE = re.compile(r"(\d+)(d|mo)")

    @staticmethod
    def _strip_html(html: str) -> str:
        return re.sub(r"<[^>]+>", "", html).strip()

    def parse(self, content: str, today: date) -> list[Internship]:
        results: list[Internship] = []
        current_company = ""

        for tr_match in self._TR_RE.finditer(content):
            tr_html = tr_match.group(1)
            tds = self._TD_RE.findall(tr_html)
            if len(tds) < 5:
                continue

            company_cell = tds[0]
            role_cell = tds[1]
            location_cell = tds[2]
            apply_cell = tds[3]
            age_cell = tds[4]

            # Skip closed positions
            if "\U0001f512" in tr_html:
                continue

            # Company name, handling continuation rows marked with arrows.
            company_match = self._COMPANY_RE.search(company_cell)
            if company_match:
                company = company_match.group(1).strip()
                current_company = company
            else:
                company_text = self._strip_html(company_cell)
                if company_text in {"", "\u21b3", "\u00e2\u2020\u00b3"} and current_company:
                    company = current_company
                elif company_text:
                    company = company_text
                    current_company = company
                else:
                    continue

            role = self._strip_html(role_cell)
            location = self._strip_html(location_cell)

            apply_match = self._APPLY_RE.search(apply_cell)
            if not apply_match:
                continue
            apply_url = apply_match.group(1)

            age_match = self._AGE_RE.search(age_cell)
            if not age_match:
                continue
            amount = int(age_match.group(1))
            unit = age_match.group(2)
            days_ago = amount if unit == "d" else amount * 30
            date_posted = today - timedelta(days=days_ago)

            uid = Internship.make_uid("pittcsc", company, role, apply_url)
            results.append(
                Internship(
                    uid=uid,
                    company=company,
                    role=role,
                    location=location,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="pittcsc",
                    is_closed=False,
                )
            )

        return results