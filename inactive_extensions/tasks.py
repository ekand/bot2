from core.base import CustomClient

from interactions import Task, IntervalTrigger, Extension


class TasksExtension(Extension):
    bot: CustomClient

    @Task.create(IntervalTrigger(seconds=5))
    async def print_every_thirty_three(self):
        print("It's been 33 minutes!")


def setup(bot: CustomClient):
    """Let interactions load the extension"""

    TasksExtension(bot)
