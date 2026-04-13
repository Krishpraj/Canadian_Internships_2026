import re
from datetime import date, timedelta

from parsers.base import BaseParser, Internship


class SimplifyJobsParser(BaseParser):
    """
    Parses SimplifyJobs/Summer2026-Internships README-Off-Season.md

    Uses HTML <table> with <tr> rows. Each row has:
    <td><strong><a href="...">Company</a></strong></td>
    <td>Role</td>
    <td>Location</td>
    <td>Terms</td>
    <td><div align="center"><a href="APPLY_URL">...</a> <a href="SIMPLIFY_URL">...</a></div></td>
    <td>2d</td>
    """

    _TR_RE = re.compile(r"<tr>(.*?)</tr>", re.DOTALL)
    _TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)
    _COMPANY_RE = re.compile(r'<a href="[^"]*">([^<]+)</a>')
    _APPLY_RE = re.compile(r'<a href="([^"]+)">')
    _AGE_RE = re.compile(r"(\d+)(d|mo)")

    def parse(self, content: str, today: date) -> list[Internship]:
        results: list[Internship] = []

        for tr_match in self._TR_RE.finditer(content):
            tr_html = tr_match.group(1)
            tds = self._TD_RE.findall(tr_html)
            if len(tds) < 6:
                continue

            company_cell = tds[0]
            role_cell = tds[1]
            location_cell = tds[2]
            apply_cell = tds[4]
            age_cell = tds[5]

            # Skip closed positions
            if "\U0001f512" in tr_html:  # 🔒
                continue

            # Company name
            company_match = self._COMPANY_RE.search(company_cell)
            if not company_match:
                continue
            company = company_match.group(1).strip()

            role = re.sub(r"<[^>]+>", "", role_cell).strip()
            location = re.sub(r"<[^>]+>", "", location_cell).strip()

            # Apply URL - take the FIRST <a href> (direct link, not Simplify)
            apply_match = self._APPLY_RE.search(apply_cell)
            if not apply_match:
                continue
            apply_url = apply_match.group(1)

            # Age
            age_match = self._AGE_RE.search(age_cell)
            if not age_match:
                continue
            amount = int(age_match.group(1))
            unit = age_match.group(2)
            days_ago = amount if unit == "d" else amount * 30
            date_posted = today - timedelta(days=days_ago)

            uid = Internship.make_uid("simplifyjobs", company, role, apply_url)
            results.append(
                Internship(
                    uid=uid,
                    company=company,
                    role=role,
                    location=location,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="simplifyjobs",
                    is_closed=False,
                )
            )

        return results
