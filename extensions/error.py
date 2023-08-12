from interactions import Extension
from interactions import InteractionContext
from interactions import slash_command

from core.base import CustomClient


class Error(Extension):
    bot: CustomClient

    @slash_command(name="make-error", description="Ping...")
    async def ping(self, ctx: InteractionContext):
        x = 1 / 0
        await ctx.send("I did it!")


def setup(bot: CustomClient):
    Error(bot)
