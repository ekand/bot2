import datetime
import logging
import os

import interactions
import pymongo
from dotenv import load_dotenv
from interactions import Extension
from interactions import InteractionContext
from interactions import listen
from interactions import OptionType
from interactions import slash_command
from interactions import slash_option
from interactions import SlashContext
from interactions.api.events import MessageReactionAdd
from interactions.api.events import MessageReactionRemove

from core.base import CustomClient

load_dotenv()
test_guild_id = os.getenv("TEST_GUILD_ID")

DISALLOWED_ROLE_NAMES = ["admin"]


class RolesExtension(Extension):
    bot: CustomClient

    @slash_command(
        name="how-do-i-role-emoji",
        description="Instructions for how to create a role emoji reaction message",
    )
    async def how_do_i(self, ctx: SlashContext):
        await ctx.send(
            "Use /start-role-emoji-message to initialize the message, then use /add-role-to-message one or more times"
        )

    @slash_command(
        name="start-role-emoji-message",
        description="Create Role Assigning Message",
    )
    async def start_role_emoji_message(self, ctx: InteractionContext):
        current_role_message = await ctx.send("Role Emoji Reaction Message")
        document = {
            "guild_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "current_role_message_id": current_role_message.id,
            "created_datetime": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        await self.bot.mongo_motor_collection.insert_one(document)
        logging.info("tried to insert mongo document")

    @slash_command(name="add-role-to-message")
    @slash_option(
        name="role_name",
        description="Role Name",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="emoji", description="Emoji", required=True, opt_type=OptionType.STRING
    )
    async def add_role_to_message(self, ctx: SlashContext, role_name: str, emoji: str):
        if role_name in DISALLOWED_ROLE_NAMES:
            raise ValueError("role_name in DISALLOWED_ROLE_NAMES")
        if role_name not in [role.name for role in ctx.guild.roles]:
            raise ValueError("role_name not in guild roles")
        search_criteria = {"guild_id": ctx.guild.id}
        sort_criteria = [("created_datetime", pymongo.DESCENDING)]
        most_recent_result = await self.bot.mongo_motor_collection.find_one(
            search_criteria, sort=sort_criteria
        )
        if most_recent_result is None:
            raise ValueError("in add_role_to_message, most_recent_result is None")

        channel = ctx.guild.get_channel(most_recent_result["channel_id"])
        if channel is None:
            channel = ctx.guild.fetch_channel(most_recent_result["channel_id"])
        bot_message = channel.get_message(most_recent_result["current_role_message_id"])
        if bot_message is None:
            bot_message = await channel.fetch_message(
                most_recent_result["current_role_message_id"]
            )
        current_message_content = bot_message.content
        content = (
            current_message_content
            + "\n"
            + f"React with {emoji} to gain role {role_name}"
        )

        await bot_message.add_reaction(emoji)
        await bot_message.edit(content=content)
        await ctx.send(f"Role added", ephemeral=True)

    @listen(MessageReactionAdd)
    async def on_message_reaction_add(
        self, reaction: interactions.api.events.MessageReactionAdd
    ):
        if reaction.author.id == self.bot.user.id:
            return
        if reaction.message.author.id != reaction.bot.user.id:
            return
        for role_name, emoji in get_role_and_emoji_from_message(
            reaction.message.content
        ):
            if role_name is None:
                continue
            if role_name in DISALLOWED_ROLE_NAMES:
                continue  # todo give error
            selected_role = None
            if emoji != reaction.emoji.name:
                continue  # todo error message
            for role in reaction.message.guild.roles:
                if role.name == role_name:
                    selected_role = role
            if selected_role is not None:
                await reaction.author.add_role(selected_role.id)
            else:
                raise ValueError("on_message_reaction_add(): role_name not recognized")

    @listen(MessageReactionRemove)
    async def on_message_reaction_remove(
        self, reaction: interactions.api.events.MessageReactionRemove
    ):
        if reaction.author.id == self.bot.user.id:
            return
        if reaction.message.author.id != reaction.bot.user.id:
            return
        for role_name, emoji in get_role_and_emoji_from_message(
            reaction.message.content
        ):
            if role_name is None:
                continue
            if role_name in DISALLOWED_ROLE_NAMES:
                continue  # todo give error
            selected_role = None
            if emoji != reaction.emoji.name:
                continue  # todo error message
            for role in reaction.message.guild.roles:
                if role.name == role_name:
                    selected_role = role
            if selected_role is not None:
                await reaction.author.remove_role(selected_role.id)
            else:
                raise ValueError("on_message_reaction_add(): role_name not recognized")


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    RolesExtension(bot)


def get_role_and_emoji_from_message(content: str):
    """Takes content from the role emoji reaction message, which can look like the following:
    Role Emoji Reaction Message
    React with 🌞 to gain role new-role
    React with 👒 to gain role other-role
    """
    lines = content.split("\n")

    for line in lines:
        if not line.startswith("React"):
            continue
        try:
            t = line.split(" ")
            emoji = t[2]
            role_name = t[-1]
            assert role_name not in DISALLOWED_ROLE_NAMES
            yield role_name, emoji
        except IndexError:
            yield None, None
        except AssertionError:
            yield None, None
