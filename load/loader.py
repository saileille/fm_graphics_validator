"""Functions for loading user settings."""
import os.path
import re

import variables


def remove_comments(string: str) -> str:
    """Remove comments from a settings file."""
    return re.sub(">.*", "", string)


def load_flags() -> None:
    """Load the flags-file."""
    with open("settings/flags.txt", encoding="utf-8") as file:
        ignore_list = remove_comments(file.read()).split("\n")

    current_directory = None
    for line in ignore_list:
        line = line.strip()
        if not line:
            continue

        if line in variables.VALID_FLAGS:
            if not current_directory:
                raise SyntaxError(f"Encountered ignore flag {line} when no directory was set.")
            variables.FLAGS[current_directory].add(line)

        if line not in variables.VALID_FLAGS:
            if os.path.isdir(line):
                current_directory = line
                variables.FLAGS[line] = set()
            else:
                raise NotADirectoryError(f"{line} is not a directory.")
