import logging
import os

from dotenv import load_dotenv
from interactions import Extension
from interactions import IntervalTrigger
from interactions import listen
from interactions import Task

from core.base import CustomClient
from core.utils.basic_utils import get_dev_config
from core.utils.basic_utils import get_general_settings

load_dotenv()
general_settings = get_general_settings()
dev_mode = get_general_settings()["dev_mode"]

if dev_mode:
    dev_config = get_dev_config()
    test_guild_id = dev_config["guild_id"]
    test_channel_id = dev_config["channel_id"]

    class TimePassed(Extension):
        bot: CustomClient

        @Task.create(IntervalTrigger(minutes=33))
        async def print_every_thirty_three(self):
            await self.bot.get_guild(dev_config["guild_id"]).get_channel(
                test_channel_id
            ).send("it's been 33 minutes")
            logging.info("It's been 33 minutes!")

        # define a function to start the task on startup
        @listen()
        async def on_startup(self):
            self.print_every_thirty_three.start()

    def setup(bot: CustomClient):
        """Let interactions load the extension"""

        TimePassed(bot)
