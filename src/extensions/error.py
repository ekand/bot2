from core.base import CustomClient
from interactions import Extension
from interactions import InteractionContext
from interactions import Permissions
from interactions import slash_command
from interactions import slash_default_member_permission


class Error(Extension):
    bot: CustomClient

    @slash_command(name="make-error", description="Ping...")
    @slash_default_member_permission(Permissions.ADMINISTRATOR)
    async def ping(self, ctx: InteractionContext):
        x = 1 / 0
        await ctx.send("I did it!")


def setup(bot: CustomClient):
    Error(bot)
