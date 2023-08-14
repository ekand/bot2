"""Birthday Events: Creates scheduled guild events for
member birthdays and un-birthdays.

A server member with `MANAGE_EVENTS` permissions may use
\opt-in-server-to-birthday-events to opt in a server
for birthday events and choose a channel for the events, or
use \opt_out_server_from_birthday_events to remove the server
from participating in birthday events.

The associated functions, `opt_out_server_from_birthday_events`
and `opt_in_server_to_birthday_events` use the motor library
for mongodb to save this information to Mongo DB Atlas.

A server member may user \register-birthday to add their birthday
to the mongo database. They may select real birthday or un-birthday,
as well as a month and year (integers). The function `register_birthday`
implements this and saves information to mongo.

The function `create_birthday_events` exists as a task with an
interval trigger of `interval_seconds` which is 15 for DEV_MODE
or 25200 (7 hrs) for standard mode. This function looks at each
guild and checks if it is opted in. Then for each guild it iterates
over birthday_document records in descending order of creation, skipping
documents for a user that has already been seen.
If the event date is soon but not too soon, and the most recent event
is more than a year ago, a new server event is scheduled and
the last_event_datetime value is update in mongodb, as well as
an "event_create_success" value.

Function `on_startup` activates the `create_birthday_events` function.

Function schedule_discord_event parses information from a provided guild,
a mongo birthday document, and mongo opt_in_document for the guild.
From this it calls "guild.create_scheduled_event" to create the event.

Function setup adds the BirthdayEvents extension to the bot.
"""
import datetime
import logging
from http.client import HTTPException

import config
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

# TODO: Refactor into more functions

DEV_MODE = config.DEV_MODE


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
    ):
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
                year=2023, month=month_option, day=day_option, hour=16
            ),
            "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        result = await mongo_motor_birthday_collection.insert_one(document)
        print(result)
        logging.info("tried to insert mongo document")
        await ctx.send("added.")

    if DEV_MODE:
        interval_seconds = 15
    else:
        interval_seconds = 25200  # 7 hours

    @Task.create(IntervalTrigger(seconds=interval_seconds))
    async def create_birthday_events(self):
        logging.info("In create_birthday_events")
        server_birthday_event_opt_in_collection = self.bot.mongo_motor_db[
            "server_birthday_event_opt_in_collection"
        ]
        mongo_motor_birthday_collection = self.bot.mongo_motor_db["birthdayCollection"]
        for guild in self.bot.guilds:
            # Define your search criteria
            search_criteria = {"guild_id": guild.id}

            # Find the latest document asynchronously
            latest_documents = await server_birthday_event_opt_in_collection.find(
                search_criteria
            ).to_list(length=None)

            # Sort the documents by date in descending order
            latest_documents.sort(key=lambda x: x["created_date"], reverse=True)

            # Select first doc
            opt_in_document = latest_documents[0]

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
                        _id = birthday_document["_id"]
                        birthday_document["last_event_datetime"] = event_date
                        await mongo_motor_birthday_collection.replace_one(
                            {"_id": _id}, birthday_document
                        )
                        await self.schedule_discord_event(
                            guild, birthday_document, opt_in_document
                        )
                        _id = birthday_document["_id"]
                        birthday_document["last_event_datetime"] = event_date
                        birthday_document["event_create_success"] = True
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

        event_description = f"Happy {'Un-' if birthday_document['real_or_un_birthday'] == 'un' else ''}Birthday!"
        event_name = (
            f"{member_name}'s {'Un-' if birthday_document['real_or_un_birthday'] == 'un' else ''}"
            f"Birthday Party"
        )

        try:
            await guild.create_scheduled_event(
                name=event_name,
                event_type=2,
                start_time=next_event_datetime,
                description=event_description,
                end_time=next_event_datetime + datetime.timedelta(hours=1),
                channel_id=opt_in_document["channel_id"],
            )
            return True
        except HTTPException as e:
            logging.info("hi 91578")
            logging.error(e)
            return False


def setup(bot: CustomClient):
    BirthdayEvents(bot)
