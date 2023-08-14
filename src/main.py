# System imports
import logging
import os
import traceback

import config
from core.base import CustomClient
from core.extensions_loader import load_extensions
from dotenv import load_dotenv
from interactions import Intents
from interactions import listen
from interactions import MISSING
from interactions.api.events import CommandError
from interactions.ext.debug_extension import DebugExtension

# Third party imports
# Local imports

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

    # create our bot instance
    intents = Intents.DEFAULT  # TODO: decrease intents needed
    intents.GUILD_MESSAGES = True
    intents.MESSAGE_CONTENT = True
    intents.MESSAGES = True

    bot = CustomClient(
        dev_mode=config.DEV_MODE,
        mongo_mode=config.MONGO_MODE,
        debug_scope=config.DEV_GUILD_ID if config.DEV_MODE else MISSING,
        intents=intents,  # intents are what events we want to receive from discord, `DEFAULT` is usually fine
        auto_defer=False,  # True  # automatically deferring interactions
        activity=config.ACTIVITY,  # the status message of the bot
        sync_interactions=config.SYNC_INTERACTIONS,  # whether to sync the interactions with discord
        delete_unused_application_cmds=config.DELETE_UNUSED_APPLICATION_CMDS,
    )

    if not config.DEV_MODE and config.USE_SENTRY:
        bot.load_extension("interactions.ext.sentry", token=os.getenv("SENTRY_DSN"))

    @listen(CommandError, disable_default_listeners=True)
    async def on_command_error(event: CommandError):
        # tell the dispatcher that this replaces the default listener
        logging.error(event.error.__repr__())
        logging.error(traceback.format_exc())
        if not event.ctx.responded:
            await event.ctx.send("Something went wrong.")

    # load the debug extension if that is wanted
    if config.LOAD_DEBUG_COMMANDS:
        DebugExtension(bot=bot)

    # load all extensions in the ./extensions folder
    load_extensions(bot=bot, feature_flags=config.FEATURE_FLAGS)

    # start the bot
    bot.start(os.getenv("DISCORD_TOKEN"))
