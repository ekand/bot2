from core.base import CustomClient

from interactions import Extension, InteractionContext, slash_command


class Ping(Extension):
    bot: CustomClient

    @slash_command(name="ping", description="Ping...", scopes=[1137094891764203591])
    async def ping(self, ctx: InteractionContext):
        await ctx.send(f"Pong!")


def setup(bot: CustomClient):
    Ping(bot)
