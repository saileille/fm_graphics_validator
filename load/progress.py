"""Load the progress."""
import pickle

from classes.progress import Progress


def load_progress() -> Progress:
    """Load progress."""
    files = Progress.get_file_data()
    files.sort(key=lambda f: f["modified"], reverse=True)

    for filedata in files:
        try:
            with open(filedata["name"], "rb") as file:
                return pickle.load(file)
        except (FileNotFoundError, pickle.UnpicklingError):
            pass

    return Progress()
