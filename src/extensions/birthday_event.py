"""Creates scheduled guild events for (un-)birthdays



"""
import datetime
import json
import logging

import aiohttp
import interactions.models
import pymongo
from core.base import CustomClient
from interactions import Button
from interactions import ButtonStyle
from interactions import Extension
from interactions import IntervalTrigger
from interactions import listen
from interactions import OptionType
from interactions import Permissions
from interactions import slash_command
from interactions import slash_default_member_permission
from interactions import slash_option
from interactions import SlashCommandChoice
from interactions import SlashContext
from interactions import Task


class BirthdayEvents(Extension):
    bot: CustomClient

    @slash_command(name="opt-out-from-birthday-events")
    @slash_default_member_permission(Permissions.MANAGE_EVENTS)
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
    @slash_default_member_permission(Permissions.MANAGE_EVENTS)
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
    @slash_option(
        name="real_or_un_birthday",
        description="Choose Real Birthday or Un-Birthday",
        required=True,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Real Birthday", value="real"),
            SlashCommandChoice(name="Un-Birthday", value="un"),
        ],
    )
    async def register_birthday(
        self,
        ctx: SlashContext,
        month_option: int,
        day_option: int,
        real_or_un_birthday: str,
    ):  # , birthday_type: str
        await ctx.defer()
        mongo_motor_birthday_collection = self.bot.mongo_motor_db["birthdayCollection"]
        document = {
            "guild_id": ctx.guild.id,
            "member_id": ctx.member.id,
            "month": month_option,
            "day": day_option,
            "real_or_un_birthday": real_or_un_birthday,
            "last_event_datetime": datetime.datetime(year=2001, month=1, day=1),
            "next_event_datetime": datetime.datetime(
                year=2023, month=month_option, day=day_option
            ),
            "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        await mongo_motor_birthday_collection.insert_one(document)
        logging.info("tried to insert mongo document")
        await ctx.send("added.")

    # @Task.create(IntervalTrigger(seconds=15))
    @Task.create(IntervalTrigger(hours=7))
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
                if (event_date - now).seconds > 0 and (event_date - now).days <= 3:
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
                    await mongo_motor_birthday_collection.replace_one(
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

        event_description = f"Happy {'Un-' if birthday_document['real_or_un_birthday'] == 'un' else ''}Birthday!"
        event_name = (
            f"{member_name}'s {'Un-' if birthday_document['real_or_un_birthday'] == 'un' else ''}"
            f"Birthday Party"
        )
        await self.create_guild_event(
            guild_id=int(guild.id),
            event_name=event_name,
            event_description=event_description,
            event_start_time=next_event_datetime_str,
            event_end_time=event_end_time_str,
            event_metadata={},
            channel_id=opt_in_document["channel_id"],
        )


def setup(bot: CustomClient):
    BirthdayEvents(bot)
