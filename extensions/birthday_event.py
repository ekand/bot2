import datetime
import json
import logging
import traceback

import aiohttp
import interactions.models
import pymongo
from interactions import ActionRow
from interactions import Button
from interactions import ButtonStyle
from interactions import Extension
from interactions import InputText
from interactions import InteractionContext
from interactions import IntervalTrigger
from interactions import listen
from interactions import Modal
from interactions import OptionType
from interactions import ShortText
from interactions import slash_command
from interactions import slash_option
from interactions import SlashCommandChoice
from interactions import SlashContext
from interactions import StringSelectMenu
from interactions import Task

from core.base import CustomClient


class BirthdayEvents(Extension):
    bot: CustomClient

    @slash_command(name="opt-out-server-events")
    async def opt_out_server_from_birthday_events(self, ctx: SlashContext):
        server_birthday_event_opt_in_collection = self.bot.mongo_motor_db[
            "server_birthday_event_opt_in_collection"
        ]
        document = {
            "guild_id": ctx.guild.id,
            "channel_id": 0,
            "created_date": datetime.datetime.now(tz=datetime.timezone.utc),
            "opt_in": False,
        }
        await server_birthday_event_opt_in_collection.insert_one(document)
        await ctx.send("opted_out")

    @slash_command(name="opt-in-server-to-birthday-events")
    async def opt_in_server_to_birthday_events(self, ctx: SlashContext):
        await ctx.defer()
        server_birthday_event_opt_in_collection = self.bot.mongo_motor_db[
            "server_birthday_event_opt_in_collection"
        ]
        choices_list = []
        channels = ctx.guild.channels
        for i, birthday_channel in enumerate(channels):
            choices_list.append(
                Button(
                    custom_id=f"channel_choice_{i}",
                    style=ButtonStyle.GREEN,
                    label=birthday_channel.name,
                )
            )
        from asyncio import TimeoutError

        await ctx.send(
            "Please choose a channel for the events.", components=choices_list
        )
        used_component = await self.bot.wait_for_component(
            components=choices_list, timeout=30
        )
        custom_id = used_component.ctx.custom_id
        birthday_channel = channels[int(custom_id.split("_")[-1])]

        document = {
            "guild_id": ctx.guild.id,
            "channel_id": birthday_channel.id,
            "created_date": datetime.datetime.now(tz=datetime.timezone.utc),
            "opt_in": True,
        }
        await server_birthday_event_opt_in_collection.insert_one(document)
        await used_component.ctx.send(
            f"opted in. Events will happen in channel: {birthday_channel.name}"
        )

        # InputText(StringSelectMenu(
        #     *choices_list,
        #     placeholder="Which channel to use?",
        #     min_values=1,
        #     max_values=1,
        #     )), title="choose channel")

        # OptionType.CHANNEL
        #     ShortText(OptionType=), title='title')
        # ShortText()

        # result = await ctx.send_modal(modal=my_modal)

        # ShortText(
        #     label="Short Input Text",
        #     custom_id="short_text",
        #     value="Pre-filled text",
        #     min_length=10,
        # ),
        #
        # document = {
        #     "guild_id": ctx.guild.id,
        #     "selected_channel_id":
        #     "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
        # }

        # from interactions import slash_command, SlashContext, Modal, ShortText, ParagraphText

        # @slash_command(name="my_modal_command", description="Playing with Modals")
        # async def my_command_function(ctx: SlashContext):
        #     my_modal = Modal(
        #         ShortText(label="Short Input Text", custom_id="short_text"),
        #         ParagraphText(label="Long Input Text", custom_id="long_text"),
        #         title="My Modal",
        #     )
        #     await ctx.send_modal(modal=my_modal)

    @slash_command(
        name="register-birthday",
        description="Tell the bot your birthday and it'll create a special event all for you.",
    )
    @slash_option(
        name="month_option",
        description="Month Number",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1,
        max_value=12,
    )
    @slash_option(
        name="day_option",
        description="Day Number",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1,
        max_value=31,
    )
    async def register_birthday(
        self, ctx: SlashContext, month_option, day_option
    ):  # , birthday_type: str
        await ctx.defer()
        mongo_motor_birthday_collection = self.bot.mongo_motor_db["birthdayCollection"]
        document = {
            "guild_id": ctx.guild.id,
            "member_id": ctx.member.id,
            "month": month_option,
            "day": day_option,
            "last_event_datetime": datetime.datetime(year=2001, month=1, day=1),
            "next_event_datetime": datetime.datetime(
                year=2023, month=month_option, day=day_option
            ),
            "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        await mongo_motor_birthday_collection.insert_one(document)
        logging.info("tried to insert mongo document")
        await ctx.send("added.")

    #     @slash_option(
    #         name="birthday_type",
    #         description="Integer Option",
    #         required=True,
    #         opt_type=OptionType.STRING,
    #         choices=[
    #             SlashCommandChoice(name="Real Birthday", value='real_birthday'),
    #             SlashCommandChoice(name="Un-Birthday", value='un_birthday')
    #         ]

    # def schedule_discord_event(self, guild, document):
    #
    #     await self.create_guild_event(guild_id=guild.id,
    #         event_name=f"Birthday Party For {guild.fetch_member(document['member_id'])}",
    #         event_description="Happy Birthday!",
    #         event_start_time=document['next_event_datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
    #         event_end_time=(document['next_event_datetime'] + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),
    #         event_metadata={},
    #                                   event_privacy_level=2
    #                                   channel_id=
    #
    #
    #                                   )
    # : str,
    # : str,
    # : str,
    # : dict,
    #  = 2,
    # channel_id = None
    # )

    # document = {
    #     "guild_id": ctx.guild.id,
    #     "member_id": ctx.member.id,
    #     "month": month,
    #     "day": day,
    #     'last_event_datetime': datetime.datetime(year=2021)
    #     "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
    # }

    # @Task.create(IntervalTrigger(hours=11))
    @Task.create(IntervalTrigger(seconds=15))
    async def create_birthday_events(self):
        logging.info("In create_birthday_events")
        server_birthday_event_opt_in_collection = self.bot.mongo_motor_db[
            "server_birthday_event_opt_in_collection"
        ]
        mongo_motor_birthday_collection = self.bot.mongo_motor_db["birthdayCollection"]
        for guild in self.bot.guilds:
            search_criteria = {"guild_id": guild.id}
            sort_criteria = [("created_datetime", pymongo.DESCENDING)]
            opt_in_document = await server_birthday_event_opt_in_collection.find_one(
                search_criteria, sort=sort_criteria
            )
            if opt_in_document is None:
                continue
            if not opt_in_document["opt_in"]:
                continue
            seen_users = set()
            async for birthday_document in mongo_motor_birthday_collection.find(
                {"guild_id": {"$eq": guild.id}},
                sort=[("created_datetime", pymongo.DESCENDING)],
            ):
                member_id = birthday_document["member_id"]
                if member_id in seen_users:
                    continue
                seen_users.add(member_id)
                event_date = datetime.datetime(
                    year=2023,
                    month=birthday_document["month"],
                    day=birthday_document["day"],
                )
                now = datetime.datetime.now()
                if (event_date - now).seconds > 0 and (event_date - now).days < 1:
                    if (
                        (event_date - birthday_document["last_event_datetime"]).days
                        > 364
                        and (event_date - now).seconds > 0
                        and (event_date - now).days < 5
                    ):
                        await self.schedule_discord_event(
                            guild, birthday_document, opt_in_document
                        )
                _id = birthday_document["_id"]
                birthday_document["last_event_datetime"] = event_date
                mongo_motor_birthday_collection.replace_one(
                    {"_id": _id}, birthday_document
                )

    # define a function to start the task on startup
    @listen()
    async def on_startup(self):
        self.create_birthday_events.start()

    async def schedule_discord_event(
        self, guild: interactions.models.Guild, birthday_document, opt_in_document
    ):
        member = guild.get_member(birthday_document["member_id"])
        if member is None:
            member = await guild.fetch_member(birthday_document["member_id"])
        member_name = member.display_name
        next_event_datetime: datetime.datetime = birthday_document[
            "next_event_datetime"
        ]
        next_event_datetime_str = next_event_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        event_end_time_str = (
            next_event_datetime + datetime.timedelta(hours=1)
        ).strftime("%Y-%m-%dT%H:%M:%S")

        #     async def create_guild_event_2(self, guild_id: int, event_name: str,
        #                                  event_description: str, event_start_time: str, event_end_time: str,
        #                                  event_metadata: dict, channel_id: int = None):

        logging.info("in schedule_discord_event, calling create_guild_event_2")
        await self.create_guild_event_2(
            guild_id=int(guild.id),
            event_name=f"{member_name}'s Birthday Party",
            event_description="Happy Birthday!",
            event_start_time=next_event_datetime_str,
            event_end_time=event_end_time_str,
            event_metadata={},
            channel_id=opt_in_document["channel_id"],
        )

    async def create_guild_event(
        self,
        guild_id: str,
        event_name: str,
        event_description: str,
        event_start_time: str,
        event_end_time: str,
        event_metadata: dict,
        event_privacy_level=2,
        channel_id=None,
    ) -> None:
        auth_headers = {
            "Authorization": f"Bot {self.bot.token}",
            "User-Agent": "DiscordBot (https://your.bot/url) Python/3.9 aiohttp/3.8.1",
            "Content-Type": "application/json",
        }
        base_api_url = "https://discord.com/api"
        """Creates a guild event using the supplied arguments
        The expected event_metadata format is event_metadata={'location': 'YOUR_LOCATION_NAME'}
        The required time format is %Y-%m-%dT%H:%M:%S"""
        event_create_url = f"{base_api_url}/guilds/{guild_id}/scheduled-events"
        event_data = json.dumps(
            {
                "name": event_name,
                "privacy_level": event_privacy_level,
                "scheduled_start_time": event_start_time,
                "scheduled_end_time": event_end_time,
                "description": event_description,
                "channel_id": channel_id,
                "entity_metadata": event_metadata,
                "entity_type": 3,
            }
        )

        async with aiohttp.ClientSession(headers=auth_headers) as session:
            try:
                async with session.post(event_create_url, data=event_data) as response:
                    response.raise_for_status()
                    assert response.status == 200
            except Exception as e:
                logging.error(f"EXCEPTION: {e}")
            finally:
                await session.close()

    async def create_guild_event_2(
        self,
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
            "Authorization": f"Bot {self.bot.token}",
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


def setup(bot: CustomClient):
    BirthdayEvents(bot)
