"""
Module to define CustomClient, which inherits from interactions.Client

CustomClient also includes a mongo_motor_db client and
a flag for dev_mode.

"""
import os

import config
import motor.motor_asyncio
from interactions import Client
from interactions import listen

# TODO remove 'mongo_motor_collection'


class CustomClient(Client):
    """Subclass of interactions.Client with our own logger and on_startup event"""

    def __init__(self, dev_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dev_mode = dev_mode
        mongo_motor_client = get_mongo_motor_client()
        mongo_motor_db = mongo_motor_client["testDB"]
        self.mongo_motor_db = mongo_motor_db
        self.mongo_motor_collection = mongo_motor_db[
            "testCol"
        ]  # todo remove this when possible

    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        self.logger.info(f"{os.getenv('PROJECT_NAME')} - Startup Finished!")


def get_mongo_motor_client():
    if config.MONGO_MODE == "localhost":
        MONGO_LOCAL_URI = os.getenv("MONGO_LOCAL_URI")
        assert MONGO_LOCAL_URI is not None
        assert MONGO_LOCAL_URI != "changeme"
        mongo_motor_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_LOCAL_URI)
    else:
        MONGO_CERT_PATH = os.getenv("MONGO_CERT_PATH")
        assert MONGO_CERT_PATH is not None
        assert MONGO_CERT_PATH != "changeme"
        MONGO_URI = os.getenv("MONGO_URI")
        assert MONGO_URI is not None
        assert MONGO_CERT_PATH != "changeme"
        mongo_motor_client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_URI, tlsCertificateKeyFile=MONGO_CERT_PATH
        )

    return mongo_motor_client
