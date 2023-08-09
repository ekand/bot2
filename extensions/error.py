import logging
import traceback

from interactions import Extension
from interactions import InteractionContext
from interactions import listen
from interactions import slash_command
from interactions.api.events import CommandError

from core.base import CustomClient


class Error(Extension):
    bot: CustomClient

    @slash_command(name="make-error", description="Ping...")  # , scopes=[test_guild_id]
    async def ping(self, ctx: InteractionContext):
        try:
            s = 1 / 0
            await ctx.send(f"Pong!")
        except ZeroDivisionError as e:

            await ctx.send("Something went wrong.")


def setup(bot: CustomClient):
    Error(bot)
