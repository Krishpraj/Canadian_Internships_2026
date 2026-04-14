import os
from dataclasses import dataclass
from pathlib import Path

# Load .env file manually (avoid extra dependency)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _val = _line.split("=", 1)
            os.environ.setdefault(_key.strip(), _val.strip())

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))
POLL_INTERVAL_MINUTES = int(os.environ.get("POLL_INTERVAL_MINUTES", "30"))
DB_PATH = os.environ.get("DB_PATH", "seen.db")


@dataclass
class RepoSource:
    name: str
    url: str
    parser: str


SOURCES = [
    RepoSource(
        name="speedyapply",
        url="https://raw.githubusercontent.com/speedyapply/2026-SWE-College-Jobs/main/README.md",
        parser="speedyapply",
    ),
    RepoSource(
        name="simplifyjobs",
        url="https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README-Off-Season.md",
        parser="simplifyjobs",
    ),
    RepoSource(
        name="canadian",
        url="https://raw.githubusercontent.com/negarprh/Canadian-Tech-Internships-2026/main/README.md",
        parser="canadian",
    ),
    RepoSource(
        name="pittcsc",
        url="https://raw.githubusercontent.com/pittcsc/Summer2026-Internships/master/README.md",
        parser="pittcsc",
    ),
]
