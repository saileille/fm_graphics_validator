"""Functions related to logging info."""
import time

import variables


def get_beginning_of_string(string: str, chars: int) -> str:
    """Get the beginning of a string, up to given number of characters."""
    if len(string) >= chars:
        return string

    return f"{string[:chars]}..."


def log(priority: str, string: str) -> None:
    """Log something noteworthy for the user."""
    variables.PROGRESS.log[priority] += f"{string}\n"
    print_new(string)


def add_whitespace_to_print(message: str) -> str:
    """Add needed whitespace to the message."""
    whitespace = variables.CONSOLE_LINE_LENGTH - len(message)
    if whitespace > 0:
        message += " " * whitespace

    return message


def print_new(message: str) -> None:
    """Print a message to a new line."""
    print(add_whitespace_to_print(message))
    variables.CONSOLE_LINE_LENGTH = 0


def print_progress(message: str) -> None:
    """Check if an update should be printed."""
    now = time.time()

    if variables.NEXT_UPDATE <= now:
        variables.NEXT_UPDATE = now + variables.PRINT_UPDATE_INTERVAL
        print(add_whitespace_to_print(message), end="\r")
        variables.CONSOLE_LINE_LENGTH = len(message)


def get_console_separator() -> str:
    """Print a separator that goes through the entire width of the console."""
    return "-" * 100
