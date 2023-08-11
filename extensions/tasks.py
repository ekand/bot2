import logging
import os

from dotenv import load_dotenv
from interactions import Extension
from interactions import IntervalTrigger
from interactions import listen
from interactions import Task

import config
from core.base import CustomClient

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


class TasksExtension(Extension):
    bot: CustomClient

    @Task.create(IntervalTrigger(minutes=33))
    async def print_every_thirty_three(self):
        await self.bot.get_guild(config.TEST_GUILD_ID).get_channel(
            config.TEST_BOT_CHANNEL
        ).send("it's been 33 minutes")
        print("It's been 33 minutes!")

    # define a function to start the task on startup
    @listen()
    async def on_startup(self):
        self.print_every_thirty_three.start()


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    TasksExtension(bot)
