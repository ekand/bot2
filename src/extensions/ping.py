from core.base import CustomClient
from interactions import Extension
from interactions import InteractionContext
from interactions import slash_command


class Ping(Extension):
    bot: CustomClient

    @slash_command(name="ping", description="Ping...")
    async def ping(self, ctx: InteractionContext):
        await ctx.send(f"Pong!")


def setup(bot: CustomClient):
    Ping(bot)
