import logging
import os
import traceback

from core.base import CustomClient
from core.extensions_loader import load_extensions
from dotenv import load_dotenv
from interactions import Intents
from interactions import listen
from interactions import MISSING
from interactions.api.events import CommandError
from interactions.ext.debug_extension import DebugExtension

import config


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

    # setup logging
    logging.basicConfig(
        filename="logs/interactions.log",
        level=logging.INFO,
        format="%(asctime)s UTC || %(levelname)s || %(message)s",
    )
    print("Logging to logs/interactions.py")
    logging.info("Logging to logs/interactions.py")

    DEV_MODE = config.DEV_MODE
    if DEV_MODE:
        LOAD_DEBUG_COMMANDS = config.LOAD_DEBUG_COMMANDS
        DEV_GUILD_ID = config.DEV_GUILD_ID
        DEV_CHANNEL_ID = config.DEV_CHANNEL_ID
        DEV_USER_ID = config.DEV_USER_ID
        DEBUG_SCOPE = DEV_GUILD_ID
    else:
        LOAD_DEBUG_COMMANDS = DEV_GUILD_ID = DEV_CHANNEL_ID = DEV_USER_ID = None
        DEBUG_SCOPE = MISSING

    ACTIVITY = config.ACTIVITY
    USE_SENTRY = config.USE_SENTRY
    DELETE_UNUSED_APPLICATION_CMDS = config.DELETE_UNUSED_APPLICATION_CMDS
    SYNC_INTERACTIONS = config.SYNC_INTERACTIONS

    FEATURE_FLAGS = config.FEATURE_FLAGS
    logging.info(f"FEATURE_FLAGS: {FEATURE_FLAGS}")

    # create our bot instance
    intents = Intents.DEFAULT  # todo decrease intents needed
    intents.GUILD_MESSAGES = True
    intents.MESSAGE_CONTENT = True
    intents.MESSAGES = True

    bot = CustomClient(
        dev_mode=DEV_MODE,
        debug_scope=DEBUG_SCOPE,
        intents=intents,  # intents are what events we want to receive from discord, `DEFAULT` is usually fine
        auto_defer=False,  # True  # automatically deferring interactions
        activity=ACTIVITY,  # the status message of the bot
        sync_interactions=SYNC_INTERACTIONS,
        delete_unused_application_cmds=DELETE_UNUSED_APPLICATION_CMDS,
    )

    if not DEV_MODE and USE_SENTRY:
        bot.load_extension("interactions.ext.sentry", token=os.getenv("SENTRY_DSN"))

    @listen(
        CommandError, disable_default_listeners=True
    )  # tell the dispatcher that this replaces the default listener
    async def on_command_error(event: CommandError):
        logging.error(event.error.__repr__())
        logging.error(traceback.format_exc())
        if not event.ctx.responded:
            await event.ctx.send("Something went wrong.")

    # load the debug extension if that is wanted
    if LOAD_DEBUG_COMMANDS:
        DebugExtension(bot=bot)

    # load all extensions in the ./extensions folder
    load_extensions(bot=bot, feature_flags=FEATURE_FLAGS)

    # start the bot

    bot.start(os.getenv("DISCORD_TOKEN"))
