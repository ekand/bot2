import logging
import os

from core.base import CustomClient


def load_extensions(bot: CustomClient, feature_flags: dict):
    """Automatically load all extension in the ./extensions folder"""

    bot.logger.info("Loading Extensions...")

    # go through all folders in the directory and load the extensions from all files
    # Note: files must end in .py
    for root, dirs, files in os.walk("src/extensions"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__"):
                file_name = file.removesuffix(".py")
                if not feature_flags.get(file_name):
                    if feature_flags.get(file_name) is None:
                        logging.warning(f"{file_name} not in feature flags")
                    continue
                path = os.path.join(root, file_name)
                python_import_path = path.replace("/", ".").replace("\\", ".")[4:]
                # print(python_import_path)

                # load the extension
                bot.load_extension(python_import_path)
                logging.info(f"Loaded extension from path {python_import_path}")

    # bot.logger.info(f"< {len(bot.interactions.get(0, []))} > Global Interactions Loaded")
