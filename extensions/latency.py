from core.base import CustomClient

from interactions import Extension, InteractionContext, slash_command


class Latency(Extension):
    bot: CustomClient

    @slash_command(name="latency", description="Get client latency", scopes=[1137094891764203591])
    async def latency(self, ctx: InteractionContext):
        await ctx.send(f"{(ctx.client.latency * 1000)}ms")


def setup(bot: CustomClient):
    Latency(bot)




