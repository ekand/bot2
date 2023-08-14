"""
Module to define CustomClient, which inherits from interactions.Client

CustomClient also includes a mongo_motor_db client and
a flag for dev_mode.

"""
import os
from urllib.parse import urlparse
from typing import List
import asyncio
import logging

import motor.motor_asyncio
from interactions import Client
from interactions import listen

import config


# TODO remove 'mongo_motor_collection'

def parse_mongo_database_name(uri: str) -> str:
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme != 'mongodb':
        raise ValueError("Invalid MongoDB URI. Scheme must be 'mongodb'.")

    if parsed_uri.path:
        # Remove the leading slash from the path to get the database name
        database_name = parsed_uri.path[1:]
        return database_name
    else:
        raise ValueError("Invalid MongoDB URI. Database name not found.")


async def check_and_create_collections(
        client: motor.motor_asyncio.AsyncIOMotorClient,
        database_name: str,
        collections: List[str]
) -> None:
    """
    Connects to a MongoDB server using the provided URI, checks if the specified
    collections exist in the specified database, and creates them if they don't exist.

    Args:
        client (motor.motor_asyncio.AsyncIOMotorClient): A MongoDB client.
        database_name (str): The name of the database to check and create collections in.
        collections (List[str]): A list of collection names to check and create if necessary.

    Returns:
        None
    """
    # Access the specified database
    db = client[database_name]

    # Get existing collection names in the database
    existing_collections = set(await db.list_collection_names())

    # Create a set of new collections
    new_collections = set(collections)

    # Check if collections exist and create them if they don't
    for collection_name in new_collections - existing_collections:
        await db.create_collection(collection_name)
        print(f"Collection: '{collection_name}' created to Database: {database_name}.")
        logging.info(f"Collection: '{collection_name}' created to Database: {database_name}.")


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
        mongo_motor_client = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_uri, tlscertificateKeyFile=os.getenv("MONGO_CERT_PATH")
        )
    else:
        raise ValueError(f"mongo_mode {mongo_mode} not recognized")

    return mongo_motor_client


async def setup_mongodb(mongo_mode):
    """Sets up the mongodb collections"""
    # Make client
    db_client = get_mongo_motor_client(mongo_mode)

    # Parse the MongoDB URI to extract the database name
    database_name = parse_mongo_database_name(get_mongo_uri(mongo_mode))

    # Check and create collections
    collections = config.MONGO_COLLECTIONS
    await check_and_create_collections(db_client, database_name, collections)

    return db_client


class CustomClient(Client):
    """Subclass of interactions.Client with our own logger and on_startup event"""

    def __init__(self, dev_mode, mongo_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dev_mode = dev_mode

        # Set database
        db_client = asyncio.run(setup_mongodb(mongo_mode))
        self.mongo_motor_db = db_client.get_database()

    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""
        print(f"{os.getenv('PROJECT_NAME')} - Startup Finished!")
        self.logger.info(f"{os.getenv('PROJECT_NAME')} - Startup Finished!")
