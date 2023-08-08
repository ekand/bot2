from core.base import CustomClient

import os

from interactions import Extension, InteractionContext, slash_command

from dotenv import load_dotenv

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class HelloCam(Extension):
    bot: CustomClient

    @slash_command(
        name="hello-cam", description="say hello to cam."  # , scopes=[test_guild_id]
    )
    async def hello_cam(self, ctx: InteractionContext):
        await ctx.send("Hello from Cam")


def setup(bot: CustomClient):
    HelloCam(bot)
