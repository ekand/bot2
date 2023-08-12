from interactions import Extension
from interactions import listen
from interactions.api.events import ChannelCreate

from core.base import CustomClient


class EventExtension(Extension):
    bot: CustomClient

    @listen()
    async def on_channel_create(self, event: ChannelCreate):
        """This event is called when a channel is created in a guild where the bot is"""

        self.bot.logger.info(f"Channel created with name: {event.channel.name}")


def setup(bot: CustomClient):
    """Let interactions.py load the extension"""

    EventExtension(bot)
