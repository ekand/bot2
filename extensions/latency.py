import os

from dotenv import load_dotenv
from interactions import Extension
from interactions import InteractionContext
from interactions import slash_command

from core.base import CustomClient

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class Latency(Extension):
    bot: CustomClient

    @slash_command(name="latency", description="Get client latency")
    async def latency(self, ctx: InteractionContext):
        await ctx.send(f"{round((ctx.client.latency * 1000))}ms")


def setup(bot: CustomClient):
    Latency(bot)
