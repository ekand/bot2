from core.base import CustomClient

from interactions import Extension, InteractionContext, slash_command

# import os
# from dotenv import load_dotenv
#
# load_dotenv()
# test_guild_id = os.getenv("TEST_GUILD_ID")


class Ping(Extension):
    bot: CustomClient

    @slash_command(name="ping", description="Ping...")  # , scopes=[test_guild_id]
    async def ping(self, ctx: InteractionContext):
        await ctx.send(f"Pong!")


def setup(bot: CustomClient):
    Ping(bot)
