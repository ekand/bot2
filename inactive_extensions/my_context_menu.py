from core.base import CustomClient

from interactions import (
    CommandType,
    InteractionContext,
    Message,
    context_menu,
    Extension,
)

import os
from dotenv import load_dotenv

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class ContextMenuExtension(Extension):
    bot: CustomClient

    @context_menu(
        name="repeat", context_type=CommandType.MESSAGE, scopes=[test_guild_id]
    )
    async def my_context_menu(self, ctx: InteractionContext):
        """Repeat the message on which the context menu was used"""

        message: Message = ctx.target
        await ctx.send(message.content)


def setup(bot: CustomClient):
    """Let naff load the extension"""

    ContextMenuExtension(bot)
