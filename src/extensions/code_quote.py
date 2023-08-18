import logging
import os
import random

from core.base import CustomClient
from dotenv import find_dotenv
from dotenv import load_dotenv
from github import Auth
from github import Github
from interactions import Extension
from interactions import InteractionContext
from interactions import IntervalTrigger
from interactions import listen
from interactions import slash_command
from interactions import Task

load_dotenv(find_dotenv())


class CodeQuoteExtension(Extension):
    bot: CustomClient

    @slash_command(name="code-quote", description="Quote a line of code from our repos")
    async def code_quote(self, ctx: InteractionContext):
        await ctx.defer()
        await ctx.send(
            f"Here's a random line of code from one of our repositories.\n"
            f"Will you be able to guess which repository?\n```\n{get_random_line()}```"
        )

    @Task.create(IntervalTrigger(minutes=77))
    async def print_code_quote_every_seventy_seven(
        self,
    ):  # todo let any server opt in to these
        logging.info("in print_code_quote_every_seventy_seven")
        await self.bot.get_guild(config.TEST_GUILD_ID).get_channel(
            config.TEST_BOT_CHANNEL
        ).send(
            f"Here's a random line of code from one of our repositories.\n"
            f"Will you be able to guess which repository?\n```\n{get_random_line()}```"
        )

    @listen()
    async def on_startup(self):
        self.print_code_quote_every_seventy_seven.start()


def setup(bot: CustomClient):
    CodeQuoteExtension(bot)


def get_random_line():
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))

    g = Github(auth=auth)

    repos = list(g.get_user("thebytebunch").get_repos())
    random.shuffle(repos)
    content_files = []
    while not content_files:
        repo = repos.pop()
        contents = repo.get_contents("")
        while len(contents) > 0:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                content_files.append(file_content)

        content_files = [
            content_file
            for content_file in content_files
            if content_file.path.endswith(".py")
        ]

    content_file = random.choice(content_files)
    lines = content_file.decoded_content.decode("ASCII").split("\n")
    chosen_line = ""
    while not chosen_line.strip():
        chosen_line = random.choice(lines)
    return chosen_line
