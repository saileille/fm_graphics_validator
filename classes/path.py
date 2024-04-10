"""Path class."""
import os

import logger
import validator
import variables
from classes.config import Config


class Path:
    """Path class."""

    @property
    def config_images(self) -> set[str]:
        """Get all config images of the path."""
        if self.__config_images is not None:
            return self.__config_images

        self.__config_images = set()
        for config in self.config_files.values():
            self.__config_images.update(config.config_images)

        return self.__config_images

    def __init__(self, name: str) -> None:
        """Initialize object."""
        self.name = name
        self.config_files = {}
        self.other_files = set()
        self.files_found = False
        self.configs_validated = False
        self.anomaly_files_identified = False

        self.__config_images = None

    def process(self) -> None:
        """Go through a single graphics location."""
        logger.print_new(f"Searching for files in {self.name} and sub-directories...")

        if not self.files_found:
            self.find_files()
        logger.print_new(
                f"{len(self.config_files.keys()):,} config files and {len(self.other_files):,} other files found.")

        if not self.configs_validated:
            self.validate_configs()
        config_count = len(self.config_files.keys())
        logger.print_new(f"{config_count:,} / {config_count:,} config files processed...")

        if not self.anomaly_files_identified:
            self.find_anomaly_files()

    def find_files(self) -> None:
        """Find all files within the path."""
        for root, _, files in os.walk(self.name):
            for filename in files:
                if filename in variables.PROGRESS.ignored_file_names:
                    continue

                logger.print_progress(
                        f"{len(self.config_files.keys()):,} config files and {len(self.other_files):,} other files "
                        f"found.")

                filepath = os.path.join(root, filename)
                if filename == "config.xml":
                    self.config_files[filepath] = Config(filepath)
                else:
                    self.other_files.add(filepath)

        self.files_found = True
        variables.PROGRESS.check_save()

    def validate_configs(self) -> None:
        """Validate the config files inside the path."""
        config_files = len(self.config_files.keys())
        config_progress = 0
        for config in self.config_files.values():
            logger.print_progress(f"{config_progress:,} / {config_files:,} config files processed...")
            if not config.validated:
                config.validate(f"{config_progress} / {config_files}")
            config_progress += 1

        self.configs_validated = True
        variables.PROGRESS.check_save()

    def find_anomaly_files(self) -> None:
        """Find files that are not images or are not in config data."""
        filelist = sorted(list(self.other_files))
        for filepath in filelist:
            if not variables.PROGRESS.is_image_file(filepath):
                if not validator.has_flag("IGNORE_NON-IMAGE_FILES", filepath):
                    logger.log("warning", f"{filepath}: The file is not a recognised image.")

            elif not validator.has_flag("IGNORE_MISSING_RECORDS", filepath) and not self.has_file_record(filepath):
                logger.log("warning", f"{filepath}: No config record exists for the file.")

        self.anomaly_files_identified = True
        variables.PROGRESS.check_save()

    def has_file_record(self, filepath: str) -> bool:
        """Check if the file has a config record."""
        path_without_extension = os.path.splitext(filepath)[0]
        return path_without_extension in self.config_images
