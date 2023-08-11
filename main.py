import logging
import os
import traceback

import sentry_sdk
from dotenv import load_dotenv
from interactions import Client
from interactions import Intents
from interactions import IntervalTrigger
from interactions import listen
from interactions import MISSING
from interactions import Task
from interactions.api.events import CommandError
from interactions.ext.debug_extension import DebugExtension

import config
from core.base import CustomClient
from core.extensions_loader import load_extensions

load_dotenv()
LOCAL_DEV_MODE = True if os.getenv("LOCAL_DEV_MODE") == "yes" else False
DEV_TEST_GUILD_ID = os.getenv("DEV_TEST_GUILD_ID")
if LOCAL_DEV_MODE:
    assert DEV_TEST_GUILD_ID, "DEV_TEST_GUILD_ID should not be empty or falsy"

DELETE_UNUSED_APPLICATION_CMDS = (
    True if os.getenv("DELETE_UNUSED_APPLICATION_CMDS") == "yes" else False
)


if __name__ == "__main__":
    # load the environmental vars from the .env file
    load_dotenv()
    dir_name = os.path.dirname(__file__)
    logging.basicConfig(
        filename=dir_name + "/" + "logs/interactions.log",
        level=logging.INFO,
        format="%(asctime)s UTC || %(levelname)s || %(message)s",
    )
    print("logging to logs/interactions.py")
    logging.info("logging to logs/interactions.py")

    # create our bot instance
    # bot = Client(intents=Intents.DEFAULT, activity="Another interactions.py bot")
    intents = Intents.DEFAULT
    intents.GUILD_MESSAGES = True
    intents.MESSAGE_CONTENT = True
    intents.MESSAGES = True

    bot = CustomClient(
        python_project_root_dir=dir_name,
        local_dev_mode=LOCAL_DEV_MODE,
        debug_scope=DEV_TEST_GUILD_ID if LOCAL_DEV_MODE else MISSING,
        intents=intents,  # intents are what events we want to receive from discord, `DEFAULT` is usually fine
        auto_defer=False,  # True  # automatically deferring interactions
        activity="interactions.py",  # the status message of the bot
        sync_interactions=True,
        delete_unused_application_cmds=DELETE_UNUSED_APPLICATION_CMDS,
    )
    if os.getenv("USE_SENTRY") == "yes":
        bot.load_extension("interactions.ext.sentry", token=os.getenv("SENTRY_DSN"))

    @listen(
        CommandError, disable_default_listeners=True
    )  # tell the dispatcher that this replaces the default listener
    async def on_command_error(event: CommandError):
        logging.error(event.error.__repr__())
        if not event.ctx.responded:
            await event.ctx.send("Something went wrong.")

    # load the debug extension if that is wanted
    if os.getenv("LOAD_DEBUG_COMMANDS") == "true":
        DebugExtension(bot=bot)

    # load all extensions in the ./extensions folder
    load_extensions(bot=bot)

    # start the bot
    bot.start(os.getenv("DISCORD_TOKEN"))
