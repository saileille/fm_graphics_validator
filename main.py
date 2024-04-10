"""The launcher file."""
import variables
from load import loader, progress


def run() -> None:
    """Run the program."""
    variables.PROGRESS = progress.load_progress()
    loader.load_flags()

    variables.PROGRESS.process_graphics_locations()
    variables.PROGRESS.save_log()
    variables.PROGRESS.delete_progress()


if __name__ == "__main__":
    run()
