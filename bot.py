import asyncio
import logging
from datetime import date

import aiohttp
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import CHANNEL_ID, DISCORD_TOKEN, POLL_INTERVAL_MINUTES, SOURCES
from db import apply_url_exists, get_unsent, init_db, is_seen, mark_seen
from fetcher import fetch_readme
from parsers import get_parser
from poster import post_internships

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def poll_cycle() -> None:
    today = date.today()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        try:
            channel = await client.fetch_channel(CHANNEL_ID)
        except Exception:
            log.exception("Channel %d not found", CHANNEL_ID)
            return

    async with aiohttp.ClientSession() as session:
        for source in SOURCES:
            raw = await fetch_readme(session, source)
            if raw is None:
                continue

            parser = get_parser(source.parser)
            try:
                internships = parser.parse(raw, today)
            except Exception:
                log.exception("Parser error for %s", source.name)
                continue

            new_ones: list = []
            for item in internships:
                if item.is_closed:
                    continue
                if item.date_posted < today:
                    continue
                # Per-repo dedup
                if is_seen(item.uid):
                    continue
                # Cross-repo dedup by apply URL
                if apply_url_exists(item.apply_url):
                    mark_seen(item)  # Track it but don't post
                    continue
                mark_seen(item)
                new_ones.append(item)

            if new_ones:
                await post_internships(channel, new_ones)
                log.info(
                    "%s: posted %d new internships", source.name, len(new_ones)
                )
            else:
                log.info("%s: no new internships", source.name)


async def backfill() -> None:
    today = date.today()
    unsent = get_unsent(today)
    if not unsent:
        log.info("Backfill: nothing to catch up on")
        return

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        try:
            channel = await client.fetch_channel(CHANNEL_ID)
        except Exception:
            log.exception("Backfill: channel %d not found", CHANNEL_ID)
            return

    log.info("Backfill: posting %d missed internships", len(unsent))
    await post_internships(channel, unsent)


@client.event
async def on_ready() -> None:
    log.info("Logged in as %s", client.user)
    init_db()

    await backfill()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        poll_cycle, "interval", minutes=POLL_INTERVAL_MINUTES, id="poll"
    )
    scheduler.start()

    # Run first poll immediately
    await poll_cycle()


def main() -> None:
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
