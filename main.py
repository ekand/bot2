import logging
import os
import traceback

import sentry_sdk
from dotenv import load_dotenv
from interactions import Client
from interactions import Intents
from interactions import IntervalTrigger
from interactions import listen
from interactions import Task
from interactions.api.events import CommandError
from interactions.ext.debug_extension import DebugExtension

import config
from core.base import CustomClient
from core.extensions_loader import load_extensions

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")


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
    bot = CustomClient(
        intents=Intents.DEFAULT,  # intents are what events we want to receive from discord, `DEFAULT` is usually fine
        auto_defer=False,  # True  # automatically deferring interactions
        activity="Another interactions.py bot",  # the status message of the bot
        sync_interactions=True,
        del_unused_app_cmd=True,
        python_project_root_dir=dir_name,
    )
    if config.SENTRY_EXTENSION:
        bot.load_extension("interactions.ext.sentry", token=os.getenv("SENTRY_DSN"))
    elif config.SENTRY_MANUAL:
        sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)

    @listen(
        CommandError, disable_default_listeners=True
    )  # tell the dispatcher that this replaces the default listener
    async def on_command_error(event: CommandError):
        logging.exception(f"event.error: {event.error}, : ")
        traceback.print_exception(event.error)
        if not event.ctx.responded:
            await event.ctx.send("Something went wrong.")

    # load the debug extension if that is wanted
    if os.getenv("LOAD_DEBUG_COMMANDS") == "true":
        DebugExtension(bot=bot)

    # load all extensions in the ./extensions folder
    load_extensions(bot=bot)

    # start the bot
    bot.start(os.getenv("DISCORD_TOKEN"))
