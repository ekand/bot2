"""Will schedule events...

v 0.1.0
Will schedule a sit-down meeting
every weekday at 16:00 UTC.
The meeting will be added to Discord 36 hours
before the event start time.
The event duration will be one hour
"""
import datetime
import logging

from src.core.base import CustomClient
from interactions import Button
from interactions import ButtonStyle
from interactions import Extension
from interactions import InteractionContext
from interactions import IntervalTrigger
from interactions import listen
from interactions import slash_command
from interactions import Task

from src.core.utils import create_scheduled_event


class MeetingScheduler(Extension):
    bot: CustomClient

    @slash_command(
        name="enable-sit-down-meetings",
        description="Activates sit down meetings weekdays at 16:00 UTC",
    )
    async def enable_sit_down_meetings(self, ctx: InteractionContext):
        choices_list = []
        channels = ctx.guild.channels

        for i, selected_channel in enumerate(channels):
            choices_list.append(
                Button(
                    custom_id=f"channel_choice_{i}",
                    style=ButtonStyle.GREEN,
                    label=selected_channel.name,
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
        selected_channel = channels[int(custom_id.split("_")[-1])]

        enable_sit_down_meetings_collection = self.bot.mongo_motor_db[
            "enable_sit_down_meetings_collection"
        ]

        find_one_record = await enable_sit_down_meetings_collection.find_one(
            {"guild_id": ctx.guild.id}
        )

        if find_one_record is None:
            document = {
                "guild_id": ctx.guild.id,
                "enabled": True,
                "last_scheduled_event_start_time": datetime.datetime(
                    year=2001, month=1, day=1
                ),
                "next_scheduled_meeting_start_time": get_next_schedule_meeting_start_time(),
                "channel_id": selected_channel.id,
            }
            await enable_sit_down_meetings_collection.insert_one(document)
        else:
            find_one_record["enable"] = True
            await enable_sit_down_meetings_collection.replace_one(
                {"guild_id": ctx.guild.id}, find_one_record
            )

        await ctx.send("Week day sit down meetings scheduler enabled.")

    @slash_command(
        name="disable-sit-down-meetings",
        description="Activates sit down meetings weekdays at 16:00 UTC",
    )
    async def disable_sit_down_meetings(self, ctx: InteractionContext):
        enable_sit_down_meetings_collection = self.bot.mongo_motor_db[
            "enable_sit_down_meetings_collection"
        ]

        find_one_record = enable_sit_down_meetings_collection.find_one(
            {"guild_id": ctx.guild.id}
        )

        if find_one_record is None:
            return
        else:
            find_one_record["enabled"] = False
            enable_sit_down_meetings_collection.replace_one(
                {"guild_id": ctx.guild.id}, find_one_record
            )
        await ctx.send("Week day sit down meetings scheduler disabled.")

    @Task.create(IntervalTrigger(hours=6))
    async def schedule_meetings(self):
        for guild in self.bot.guilds:
            enable_sit_down_meetings_collection = self.bot.mongo_motor_db[
                "enable_sit_down_meetings_collection"
            ]
            document = enable_sit_down_meetings_collection.find_one(
                {"guild_id": guild.id}
            )
            if document["enabled"]:
                if self.is_it_time_to_schedule_meeting(document):
                    self.create_meeting(guild, document)

    def is_it_time_to_schedule_meeting(self, document):
        pass

    # define a function to start the task on startup
    @listen()
    async def on_startup(self):
        self.schedule_meetings.start()

    def create_meeting(self, guild, document):
        await create_scheduled_event.create_guild_event(
            bot=self.bot,
            guild_id=guild.id,
            event_name="Sit-Down Meeting",
            event_description="Informal weekday meeting",
            event_start_time=document["next_scheduled_meeting_start_time"].strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            event_end_time=(
                document["next_scheduled_event_meeting_start_time"]
                + datetime.timedelta(hours=1)
            ).strftime("%Y-%m-%dT%H:%M:%S"),
            event_metadata={},
            channel_id=document["chanel_id"],
        )
        # todo save next next scheduled meeting start time to document


def setup(bot: CustomClient):
    MeetingScheduler(bot)


def get_next_schedule_meeting_start_time():
    pass
