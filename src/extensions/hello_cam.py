import os

from core.base import CustomClient
from dotenv import load_dotenv
from interactions import Extension
from interactions import InteractionContext
from interactions import slash_command

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
