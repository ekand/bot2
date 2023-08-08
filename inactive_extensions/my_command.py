from core.base import CustomClient

from interactions import (
    Button,
    ButtonStyle,
    ComponentContext,
    Embed,
    Extension,
    InteractionContext,
    component_callback,
    slash_command,
)

# from interactions.something import ButtonStyles
# create a recurring task
import os
from dotenv import load_dotenv

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class CommandExtension(Extension):
    bot: CustomClient

    @slash_command(
        name="hello_world_new",
        description="My first command :)",
        scopes=[test_guild_id],
    )
    async def my_command(self, ctx: InteractionContext):
        """Says hello to the world"""

        # adds a component to the message
        components = Button(
            style=ButtonStyle.GREEN, label="Hiya", custom_id="hello_world_button"
        )

        # adds an embed to the message
        embed = Embed(title="Hello World 2", description="Now extra fancy")

        # respond to the interaction
        await ctx.send("Hello World", embeds=embed, components=components)

    @component_callback("hello_world_button")
    async def my_callback(self, ctx: ComponentContext):
        """Callback for the component from the hello_world command"""

        await ctx.send("Hiya to you too")


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    CommandExtension(bot)
