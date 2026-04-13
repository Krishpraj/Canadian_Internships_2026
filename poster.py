import asyncio
import logging

import discord

from db import mark_posted
from parsers.base import Internship

log = logging.getLogger(__name__)

SOURCE_COLORS = {
    "speedyapply": 0x5865F2,   # blurple
    "simplifyjobs": 0x57F287,  # green
    "canadian": 0xED4245,      # red
}

SOURCE_LABELS = {
    "speedyapply": "SpeedyApply (US)",
    "simplifyjobs": "SimplifyJobs (Off-Season)",
    "canadian": "Canadian Tech",
}


def build_embed(internship: Internship) -> discord.Embed:
    embed = discord.Embed(
        title=f"{internship.company} — {internship.role}",
        url=internship.apply_url,
        color=SOURCE_COLORS.get(internship.source, 0x99AAB5),
    )
    if internship.location:
        embed.add_field(name="Location", value=internship.location, inline=True)
    embed.add_field(
        name="Posted",
        value=internship.date_posted.strftime("%b %d, %Y"),
        inline=True,
    )
    embed.add_field(
        name="Source",
        value=SOURCE_LABELS.get(internship.source, internship.source),
        inline=True,
    )
    return embed


async def post_internships(
    channel: discord.TextChannel, internships: list[Internship]
) -> None:
    # Sort oldest first so newest appear at the bottom
    internships.sort(key=lambda i: i.date_posted)

    # Post in batches of 10 embeds (Discord limit per message)
    batch_size = 10
    for i in range(0, len(internships), batch_size):
        batch = internships[i : i + batch_size]
        embeds = [build_embed(item) for item in batch]
        try:
            await channel.send(embeds=embeds)
            for item in batch:
                mark_posted(item.uid)
            log.info("Posted %d internships", len(batch))
        except Exception:
            log.exception("Failed to post batch starting at index %d", i)

        if i + batch_size < len(internships):
            await asyncio.sleep(1)
