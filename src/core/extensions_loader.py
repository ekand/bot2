import logging
import os

from core.base import CustomClient


def load_extensions(bot: CustomClient, feature_flags: dict):
    """Automatically load all extension in the ./extensions folder"""

    bot.logger.info("Loading Extensions...")

    # go through all folders in the directory and load the extensions from all files
    # Note: files must end in .py
    for root, dirs, files in os.walk(os.path.join("src", "extensions")):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                file_name = file.removesuffix(".py")

                # Check feature flag for extension
                flag = feature_flags.get(file_name)

                # Check if flag is set to False
                if flag is False:
                    logging.info(f"{file_name} is disabled")
                    continue

                # Check if flag is set to None
                elif flag is None:
                    logging.warning(f"{file_name} not in feature flags")
                    continue

                # Make relative path to extension
                path = os.path.join(root, file_name)
                python_import_path = path.replace(os.sep, ".").removeprefix("src.")

                # load the extension
                bot.load_extension(python_import_path)
                logging.info(f"Loaded extension from path {python_import_path}")

    # Log all the commands loaded
    # bot.logger.info(f"< {len(bot.interactions.get(0, []))} > Global Interactions Loaded")
