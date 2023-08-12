import json
import logging

import aiohttp

#
# await self.create_guild_event_2(
#     guild_id=int(guild.id),
#     event_name=f"{member_name}'s Birthday Party",
#     event_description="Happy Birthday!",
#     event_start_time=next_event_datetime_str,
#     event_end_time=event_end_time_str,
#     event_metadata={},
#     channel_id=opt_in_document["channel_id"],
# )


async def create_guild_event(
    bot,
    guild_id: int,
    event_name: str,
    event_description: str,
    event_start_time: str,
    event_end_time: str,
    event_metadata: dict,
    channel_id: int = None,
):
    """Creates a guild event using the supplied arguments.
    The expected event_metadata format is event_metadata={"location": "YOUR_LOCATION_NAME"}
    The required time format is %Y-%m-%dT%H:%M:%S aka ISO8601

    Args:
        guild_id (str): Guild id in endpoint
        event_name (str): Name of event
        event_description (str): Description of event
        event_start_time (str): Start timestamp
        event_end_time (str): End timestamp
        event_metadata (dict): External location data
        channel_id (int, optional): Id of voice channel. Defaults to None.
    Raises:
        ValueError: Cannot have both (event_metadata) and (channel_id)
        at the same time.
    """
    if channel_id and event_metadata:
        raise ValueError(
            f"If event_metadata is set, channel_id must be set to None. And vice versa."
        )
    API_URL: str = "https://discord.com/api/v10"
    ENDPOINT_URL = f"{API_URL}/guilds/{guild_id}/scheduled-events"
    entity_type = 2

    event_data = json.dumps(
        {
            "name": event_name,
            "privacy_level": 2,
            "scheduled_start_time": event_start_time,
            "scheduled_end_time": event_end_time,
            "description": event_description,
            "channel_id": channel_id,
            "entity_metadata": event_metadata,
            "entity_type": entity_type,
        }
    )
    BOT_AUTH_HEADER = f"https://discord.com/oauth2/authorize?client_id={1139488619405529159}"  # todo change me
    AUTH_HEADERS: dict = {
        "Authorization": f"Bot {bot.token}",
        "User-Agent": f"DiscordBot ({BOT_AUTH_HEADER}) Python/3.9 aiohttp/3.7.4",
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession(headers=AUTH_HEADERS) as session:
        try:
            async with session.post(ENDPOINT_URL, data=event_data) as response:
                response.raise_for_status()
                assert response.status == 200
                logging.info(f"Post success: to {ENDPOINT_URL}")
        except Exception as e:
            logging.warning(f"Post error: to {ENDPOINT_URL} as {e}")
            await session.close()
            return

        await session.close()
        return response
