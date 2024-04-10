"""Progress class."""
import datetime
import json
import os
import pickle
import shutil
from pathlib import Path

import logger
from classes import path
from load import loader


class Progress:
    """Progress class."""

    @staticmethod
    def delete_progress() -> None:
        """Delete the saved progress."""
        shutil.rmtree("progress", ignore_errors=True)

    @staticmethod
    def get_file_data() -> list[dict]:
        """Get the data of the saved progress files."""
        files = [{"name": "progress/1.pcl", "modified": 0.0}, {"name": "progress/2.pcl", "modified": 0.0}]
        for file in files:
            if os.path.exists(file["name"]):
                file["modified"] = os.path.getmtime(file["name"])

        return files

    @staticmethod
    def load_graphics_paths() -> dict[str, path.Path]:
        """Load the graphics paths."""
        paths = {}

        with open("settings/graphics_locations.txt", encoding="utf-8") as file:
            path_list = loader.remove_comments(file.read()).split("\n")

        for path_string in path_list:
            path_string = path_string.strip()
            if not path_string:
                continue

            if not os.path.isdir(path_string):
                logger.log("info", f"{path_string} is not an existing directory and will be ignored.")
            else:
                paths[path_string] = path.Path(path_string)

        return paths

    @staticmethod
    def load_image_file_extensions() -> set[str]:
        """Load image file extensions."""
        image_file_extensions = set()
        with open("settings/image_file_extensions.txt", encoding="utf-8") as file:
            extension_list = loader.remove_comments(file.read()).split("\n")

        for extension in extension_list:
            extension = extension.strip()
            if extension:
                image_file_extensions.add(extension)

        return image_file_extensions

    @staticmethod
    def load_valid_to_paths() -> set[str]:
        """Load valid to-paths."""
        valid_to_paths = set()
        with open("settings/valid_to_paths.txt", encoding="utf-8") as file:
            path_list = loader.remove_comments(file.read()).split("\n")

        for path_string in path_list:
            path_string = path_string.strip()
            if path_string:
                valid_to_paths.add(path_string)

        return valid_to_paths

    @staticmethod
    def load_config_formatting() -> dict:
        """Load config formatting."""
        with open("settings/config_formatting.json", encoding="utf-8") as file:
            config_format = json.load(file)

        if type(config_format["indent"]) is int:
            config_format["indent"] = " " * config_format["indent"]

        return config_format

    @staticmethod
    def load_ignored_files() -> set:
        """Load ignored files list."""
        ignored_files = set()
        with open("settings/ignore_file_names.txt", encoding="utf-8") as file:
            namelist = loader.remove_comments(file.read()).split("\n")

        for name in namelist:
            name = name.strip()
            if name:
                ignored_files.add(name)

        return ignored_files

    def __init__(self) -> None:
        """Initialize object."""
        self.paths = Progress.load_graphics_paths()
        self.image_file_extensions = Progress.load_image_file_extensions()
        self.valid_to_paths = Progress.load_valid_to_paths()
        self.config_format = Progress.load_config_formatting()
        self.ignored_file_names = Progress.load_ignored_files()
        self.log = {"critical": "", "important": "", "warning": "", "info": ""}
        self.save_interval = 10  # How many seconds should pass between two saves.
        self.next_save = 0  # When the next save should happen, as seconds since the epoch.

    def process_graphics_locations(self) -> None:
        """Go through the graphics locations."""
        for path_object in self.paths.values():
            if not path_object.anomaly_files_identified:
                path_object.process()

    def is_image_file(self, filepath) -> bool:
        """Return true if the filepath has a recognised image file type. Otherwise, return False."""
        file_ext = os.path.splitext(filepath)[1].casefold()[1:]
        for ext in self.image_file_extensions:
            if file_ext == ext.casefold():
                return True

        return False

    def check_save(self) -> None:
        """Check if progress should be saved."""
        """if time.time() >= self.next_save:
            self.save()
            self.next_save = time.time() + self.save_interval
            print("Saved", end="\r")"""
        return

    def save(self) -> None:
        """Save the progress."""
        files = Progress.get_file_data()
        files.sort(key=lambda f: f["modified"])
        os.makedirs("progress", exist_ok=True)
        with open(files[0]["name"], "wb") as file:
            pickle.dump(self, file)

    def save_log(self) -> None:
        """Save the log."""
        Path("logs").mkdir(parents=True, exist_ok=True)

        log_string = ""
        if self.log["critical"]:
            log_string += (f"{logger.get_console_separator()}\nCRITICAL\n{logger.get_console_separator()}\n"
                           f"{self.log['critical']}")

        if self.log["important"]:
            log_string += (f"{logger.get_console_separator()}\nIMPORTANT\n{logger.get_console_separator()}\n"
                           f"{self.log['important']}")

        if self.log['warning']:
            log_string += (f"{logger.get_console_separator()}\nWARNING\n{logger.get_console_separator()}\n"
                           f"{self.log['warning']}")

        if self.log['info']:
            log_string += (f"{logger.get_console_separator()}\nINFO\n{logger.get_console_separator()}\n"
                           f"{self.log['info']}")

        filename = str(datetime.datetime.now()).replace(":", ".")
        with open(f"logs/{filename}.txt", "w", encoding="utf-8") as file:
            file.write(log_string)
