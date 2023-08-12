import logging
import os

from core.base import CustomClient
from core.utils.basic_utils import get_feature_flags


def load_extensions(bot: CustomClient):
    """Automatically load all extension in the ./extensions folder"""

    bot.logger.info("Loading Extensions...")

    # go through all folders in the directory and load the extensions from all files
    # Note: files must end in .py
    feature_flags = get_feature_flags()
    for root, dirs, files in os.walk("src/extensions"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__"):
                file_name = file.removesuffix(".py")
                if feature_flags.get(file_name) != "1":
                    continue
                path = os.path.join(root, file_name)
                python_import_path = path.replace("/", ".").replace("\\", ".")[4:]
                # print(python_import_path)

                # load the extension
                bot.load_extension(python_import_path)
                logging.info(f"Loaded extension from path {python_import_path}")

    # bot.logger.info(f"< {len(bot.interactions.get(0, []))} > Global Interactions Loaded")
