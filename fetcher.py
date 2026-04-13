import logging

import aiohttp

from config import RepoSource

log = logging.getLogger(__name__)


async def fetch_readme(
    session: aiohttp.ClientSession, source: RepoSource
) -> str | None:
    try:
        async with session.get(source.url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            return await resp.text()
    except Exception:
        log.exception("Failed to fetch %s", source.name)
        return None
