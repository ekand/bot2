from core.base import CustomClient

import interactions

import logging

from interactions import (
    Extension,
    slash_command,
    slash_option,
    OptionType,
    SlashContext,
    listen,
    InteractionContext,
    Modal,
    ShortText,
    ModalContext,
)
from interactions.api.events import MessageReactionAdd, MessageReactionRemove

ALLOWED_ROLE_NAMES = ["new-role", "other-role"]


def get_role_and_emoji_from_message(content: str):
    lines = content.split("\n")

    for line in lines:
        if not line.startswith("React"):
            continue
        try:
            t = line.split(" ")
            emoji = t[2]
            role_name = t[-1]
            assert role_name in ALLOWED_ROLE_NAMES
            yield role_name, emoji
        except IndexError:
            yield None, None
        except AssertionError:
            yield None, None


def construct_message_content(role_name, emoji, lines):
    return


class RolesExtension(Extension):
    bot: CustomClient

    def __init__(self, bot):
        self.current_role_message = None

    @slash_command(
        name="how-do-i-role-emoji",
        description="Instructions for how to create a role emoji reaction message",
    )
    async def how_do_i(self, ctx: SlashContext):
        await ctx.send(
            "Use /start-role-emoji-message to initialize the message, then use /add-role-to-message one or more times"
        )

    @slash_command(
        name="start-role-emoji-message", description="Create Role Assigning Message"
    )
    async def start_role_emoji_message(self, ctx: InteractionContext):
        current_role_message = await ctx.send("Role Emoji Reaction Message")
        self.current_role_message = current_role_message

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
        if role_name not in ALLOWED_ROLE_NAMES:
            return  # todo give an error or warning message to user
        message_content = f"React with {emoji} to gain role {role_name}"
        if self.current_role_message is None:
            return
        bot_message = self.current_role_message
        content = bot_message.content
        content += "\n" + message_content
        await bot_message.add_reaction(emoji)
        await bot_message.edit(content=content)
        await ctx.send(f"Added role {role_name} with emoji {emoji}")
        return
        pass  # todo add rolename and string to temporary structure

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
            if role_name not in ALLOWED_ROLE_NAMES:
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
                logging.warning("on_message_reaction_add(): role_name not recognized")

    @listen(MessageReactionRemove)
    async def on_message_reaction_remove(
        self, reaction: interactions.api.events.MessageReactionRemove
    ):
        if reaction.author.id == self.bot.user.id:
            return
        if reaction.message.author.id != reaction.bot.user.id:
            return
        role_name = reaction.message.content.split()[-1]
        selected_role = None
        for role_name, emoji in get_role_and_emoji_from_message(
            reaction.message.content
        ):
            if role_name is None:
                continue
            if role_name not in ALLOWED_ROLE_NAMES:
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
                logging.warning(
                    "on_message_reaction_remove(): role_name not recognized"
                )

    # @slash_option(
    #     name="role_name",
    #     description="Role Name",
    #     required=True,
    #     opt_type=OptionType.STRING
    # )
    # @slash_option(
    #     name="emoji", description="Emoji", required=True, opt_type=OptionType.STRING
    # )
    # @slash_option(
    #     name="add-another-role",
    #     description="Would you like to add another role to the message?",
    #     required=True,
    #     opt_type=OptionType.BOOLEAN)

    # @slash_command(name="create-role-emoji-message", description="Create Role Assigning Message")
    # async def create_role_emoji_message(self, ctx: InteractionContext):
    #     """Creates a mesage that users can react to, to be assigned roles."""
    #     first_call = True
    #     add_another_role = False
    #     modal_ctx = None
    #     lines = []
    #     while first_call or add_another_role:
    #         my_modal = Modal(
    #             ShortText(label="Role Name", custom_id="role_name"),
    #             ShortText(label="Emoji", custom_id="emoji"),
    #             ShortText(label="Add Another Role", custom_id='add_another_role', value='No'),
    #             title="Add a role to the message",
    #         )
    #         await ctx.send_modal(modal=my_modal)
    #
    #         modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)
    #         role_name = modal_ctx.responses['role_name']
    #         emoji = modal_ctx.responses['emoji']
    #         add_another_role_str = modal_ctx.responses['add_another_role']
    #         add_another_role = add_another_role_str.lower() == 'yes'
    #         lines.append(f"React with {emoji} to gain role {role_name}")
    #     print(lines)
    #
    #     return
    #         #
    #         # add_another_role =
    #     if role_name not in ALLOWED_ROLE_NAMES:
    #         return  # todo give an error or warning message to user
    #     if first_call:
    #         lines = []
    #     while first_call or add_another_role:
    #         first_call = False
    #         lines.append(f"React with {emoji} to gain role {role_name}")
    #         if not add_another_role:
    #             break
    #
    #     message_content = '\n'.join(lines)
    #     bot_message = await ctx.send(message_content)
    #     for line in lines:
    #         emoji = line[2]
    #         await bot_message.add_reaction(emoji)

    # adds a component to the message


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    RolesExtension(bot)
