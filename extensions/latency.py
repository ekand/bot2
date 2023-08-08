from core.base import CustomClient

from interactions import Extension, InteractionContext, slash_command

import os
from dotenv import load_dotenv

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class Latency(Extension):
    bot: CustomClient

    @slash_command(
        name="latency", description="Get client latency", scopes=[test_guild_id]
    )
    async def latency(self, ctx: InteractionContext):
        await ctx.send(f"{(ctx.client.latency * 1000)}ms")


def setup(bot: CustomClient):
    Latency(bot)
