import logging
import os

import motor.motor_asyncio
from interactions import Client
from interactions import listen
from interactions import logger_name


class CustomClient(Client):
    """Subclass of interactions.Client with our own logger and on_startup event"""

    def __init__(self, dev_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mongo_motor_client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("MONGO_URI"), tlsCertificateKeyFile=os.getenv("MONGO_CERT_PATH")
        )
        mongo_motor_db = mongo_motor_client["testDB"]
        mongo_motor_collection = mongo_motor_db["testCol"]
        self.mongo_motor_collection = mongo_motor_collection
        self.dev_mode = dev_mode

    # you can use that logger in all your extensions
    # logger = logging.getLogger(logger_name)

    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        self.logger.info(f"{os.getenv('PROJECT_NAME')} - Startup Finished!")
