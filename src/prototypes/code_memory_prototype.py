import json
import os
import random

from github import Auth
from github import Github

# todo: save a json document indicating where the line of code was found


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
