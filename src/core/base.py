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

def get_mongo_uri(mongo_mode):
    """Returns the mongo_uri based on the dev_mode"""
    mongo_uri = None
    if mongo_mode == "localhost":
        mongo_uri = os.getenv("MONGO_LOCAL_URI")
        # Make sure the user has changed the default value
        assert mongo_uri != "changeme"
    elif mongo_mode == "atlas":
        mongo_uri = os.getenv("MONGO_URI")
        # Make sure the user has changed the default value
        assert mongo_uri != "changeme"

    # Check that mongo_uri is not none
    assert mongo_uri is not None
    return mongo_uri


def get_mongo_motor_client(mongo_mode):
    """Returns the mongo_motor_client based on the dev_mode"""
    mongo_uri = get_mongo_uri(mongo_mode)

    # Create the mongo_motor_client for localhost
    if mongo_mode == "localhost":
        mongo_motor_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)

    # Create the mongo_motor_client for atlas
    elif mongo_mode == "atlas":
        mongo_motor_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri,
                                                                    tlscertificateKeyFile=os.getenv("MONGO_CERT_PATH"))
    else:
        raise ValueError(f"mongo_mode {mongo_mode} not recognized")

    return mongo_motor_client


class CustomClient(Client):
    """Subclass of interactions.Client with our own logger and on_startup event"""

    def __init__(self, dev_mode, mongo_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dev_mode = dev_mode

        # Set database
        db_client = get_mongo_motor_client(mongo_mode)
        self.mongo_motor_db = db_client.get_database()

    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""
        print(f"{os.getenv('PROJECT_NAME')} - Startup Finished!")
        self.logger.info(f"{os.getenv('PROJECT_NAME')} - Startup Finished!")
