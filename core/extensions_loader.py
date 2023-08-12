import logging
import os

from core.base import CustomClient


def load_extensions(bot: CustomClient):
    """Automatically load all extension in the ./extensions folder"""

    bot.logger.info("Loading Extensions...")

    # go through all folders in the directory and load the extensions from all files
    # Note: files must end in .py
    for root, dirs, files in os.walk(bot.python_project_root_dir + "/" + "extensions"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__"):
                file = file.removesuffix(".py")
                path = os.path.join(root, file)
                python_import_path = path.replace("/", ".").replace("\\", ".")
                python_import_path = ".".join(
                    python_import_path.split(".")[-2:]
                )  # this is hacky, fix later

                # load the extension
                bot.load_extension(python_import_path)
                logging.info(f"Loaded extension from path {python_import_path}")

    # bot.logger.info(f"< {len(bot.interactions.get(0, []))} > Global Interactions Loaded")
