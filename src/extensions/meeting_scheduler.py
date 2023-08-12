"""Will schedule events...

v 0.1.0
Will schedule a sit-down meeting
every weekday at 16:00 UTC.
The meeting will be added to Discord 36 hours
before the event start time.
The event duration will be one hour
"""
import pymongo
from core.base import CustomClient
from interactions import Extension
from interactions import InteractionContext
from interactions import slash_command


class MeetingScheduler(Extension):
    bot: CustomClient

    @slash_command(
        name="activate-sit-down-meetings",
        description="Activates sit down meetings weekdays at 16:00 UTC",
    )
    async def ping(self, ctx: InteractionContext):
        self.bot.mongo_m


def setup(bot: CustomClient):
    MeetingScheduler(bot)
