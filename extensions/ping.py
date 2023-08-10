import logging

from interactions import Extension
from interactions import InteractionContext
from interactions import logger_name
from interactions import slash_command

from core.base import CustomClient

# import os
# from dotenv import load_dotenv
#
# load_dotenv()
# test_guild_id = os.getenv("TEST_GUILD_ID")

# logger = logging.getLogger(logger_name)


class Ping(Extension):
    bot: CustomClient

    @slash_command(name="ping", description="Ping...")  # , scopes=[test_guild_id]
    async def ping(self, ctx: InteractionContext):
        # logger.info("got a ping")
        await ctx.send(f"Pong!")


def setup(bot: CustomClient):
    Ping(bot)
