import logging
import os
from configparser import ConfigParser
from pathlib import Path

from core.base import CustomClient
from core.extensions_loader import load_extensions
from core.utils import basic_utils
from dotenv import load_dotenv
from interactions import Intents
from interactions import listen
from interactions import MISSING
from interactions.api.events import CommandError
from interactions.ext.debug_extension import DebugExtension

load_dotenv()

LOCAL_DEV_MODE = True if os.getenv("LOCAL_DEV_MODE") == "yes" else False
DEV_TEST_GUILD_ID = os.getenv("DEV_TEST_GUILD_ID")
if LOCAL_DEV_MODE:
    assert DEV_TEST_GUILD_ID, "DEV_TEST_GUILD_ID should not be empty or falsy"

DELETE_UNUSED_APPLICATION_CMDS = (
    True if os.getenv("DELETE_UNUSED_APPLICATION_CMDS") == "yes" else False
)

if __name__ == "__main__":
    # get feature flags and dev settings from config.ini
    feature_flags = basic_utils.get_feature_flags()
    dev_settings = basic_utils.get_dev_config()
    general_settings = basic_utils.get_general_settings()
    dev_mode = True if general_settings["dev_mode"] == "1" else False
    debug_scope = dev_settings["guild_id"] if dev_mode else MISSING
    delete_unused_application_cmds = (
        True if general_settings["delete_unused_application_cmds"] == "1" else False
    )
    sync_interactions = (
        True if dev_mode and dev_settings["sync_interactions"] == "1" else False
    )

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

    # create our bot instance
    intents = Intents.DEFAULT
    intents.GUILD_MESSAGES = True
    intents.MESSAGE_CONTENT = True
    intents.MESSAGES = True

    bot = CustomClient(
        dev_mode=dev_mode,
        debug_scope=debug_scope,
        intents=intents,  # intents are what events we want to receive from discord, `DEFAULT` is usually fine
        auto_defer=False,  # True  # automatically deferring interactions
        activity="interactions.py",  # the status message of the bot
        sync_interactions=sync_interactions,
        delete_unused_application_cmds=delete_unused_application_cmds,
    )

    if not dev_mode and general_settings["use_sentry"] == "1":
        bot.load_extension("interactions.ext.sentry", token=os.getenv("SENTRY_DSN"))

    @listen(
        CommandError, disable_default_listeners=True
    )  # tell the dispatcher that this replaces the default listener
    async def on_command_error(event: CommandError):
        logging.error(event.error.__repr__())
        if not event.ctx.responded:
            await event.ctx.send("Something went wrong.")

    # load the debug extension if that is wanted
    if dev_mode and dev_settings["load_debug_commands"] == "1":
        DebugExtension(bot=bot)

    # load all extensions in the ./extensions folder
    load_extensions(bot=bot)

    # start the bot
    bot.start(os.getenv("DISCORD_TOKEN"))
