import datetime
import json
import logging

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


def check(component: Button) -> bool:
    return component.ctx.author.startswith("a")


class Ping(Extension):
    bot: CustomClient

    @slash_command(name="opt-out-server-from-birthday-events")
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
        name="month",
        description="Month Number",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1,
        max_value=12,
    )
    @slash_option(
        name="day",
        description="Day Number",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1,
        max_value=31,
    )
    async def register_birthday(
        self, ctx: SlashContext, month: int, day: int
    ):  # , birthday_type: str
        await ctx.defer()
        mongo_motor_birthday_collection = self.bot.mongo_motor_db["birthdayCollection"]
        document = {
            "guild_id": ctx.guild.id,
            "member_id": ctx.member.id,
            "month": month,
            "day": day,
            "last_event_datetime": datetime.datetime(year=2001),
            "next_event_datetime": datetime.datetime(year=2023, month=month, day=day),
            "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        await mongo_motor_birthday_collection.insert_one(document)
        logging.info("tried to insert mongo document")

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

    @Task.create(IntervalTrigger(hours=11))
    async def create_birthday_events(self):
        server_birthday_event_opt_in_collection = self.bot.mongo_motor_db[
            "server_birthday_event_opt_in_collection"
        ]
        mongo_motor_birthday_collection = self.bot.mongo_motor_db["birthdayCollection"]
        for guild in self.bot.guilds:
            search_criteria = {"guild_id": guild.id}
            sort_criteria = [("created_datetime", pymongo.DESCENDING)]
            opt_in_document = server_birthday_event_opt_in_collection.find_one(
                search_criteria, sort=sort_criteria
            )
            if not opt_in_document["opt_in"]:
                continue
            async for birthday_document in mongo_motor_birthday_collection.find(
                {"guild_id": {"$eq": guild.id}}
            ):
                event_date = datetime.datetime(
                    year=2023,
                    month=birthday_document["month"],
                    day=birthday_document["day"],
                )
                now = datetime.datetime.now(tz=datetime.timezone.utc)
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

    async def schedule_discord_event(
        self, guild: interactions.models.Guild, birthday_document, opt_in_document
    ):
        member = guild.get_member(birthday_document["member_id"])
        if member is None:
            member = await guild.get_member(birthday_document["member_id"])
        member_name = member.name
        next_event_datetime: datetime.datetime = birthday_document[
            "next_event_datetime"
        ]
        next_event_datetime_str = next_event_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        event_end_time_str = (
            next_event_datetime + datetime.timedelta(hours=1)
        ).strftime("%Y-%m-%dT%H:%M:%S")
        await self.create_guild_event(
            guild_id=str(guild.id),
            event_name=f"{member_name}'s Birthday Party",
            event_description="Happy Birthday!",
            event_start_time=next_event_datetime_str,
            event_end_time=event_end_time_str,
            event_metadata={},
            event_privacy_level=2,
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


def setup(bot: CustomClient):
    Ping(bot)
