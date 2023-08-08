from core.base import CustomClient

from interactions import Extension, InteractionContext, slash_command

import os
from dotenv import load_dotenv

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class Reset(Extension):
    bot: CustomClient

    @slash_command(name="reset", description="Ping...", scopes=[test_guild_id])
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
