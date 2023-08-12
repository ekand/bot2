import os

from dotenv import load_dotenv
from interactions import Extension
from interactions import InteractionContext
from interactions import slash_command

from core.base import CustomClient

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class Reset(Extension):
    bot: CustomClient

    @slash_command(
        name="reset",
        description="Ping...",  #  scopes=[test_guild_id]
    )
    async def ping(self, ctx: InteractionContext):
        pass
        # await ctx.send(f"resseting!")
        # reset_server_slash_commands = True
        # if reset_server_slash_commands:
        #     self.bot.get_guild(test_guild_id).commands.set([])
        # reset_global_slash_commands = True
        # if reset_global_slash_commands:
        #     self.bot.get_guild(test_guild_id)


def setup(bot: CustomClient):
    Reset(bot)
