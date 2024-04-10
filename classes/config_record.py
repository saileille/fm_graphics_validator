"""ConfigRecord class."""
import os.path
import re

import logger
import variables


class ConfigRecord:
    """Config record class."""

    @property
    def from_record_path(self) -> str:
        """Get the absolute path of the source record."""
        return os.path.normpath(os.path.join(self.directory, self.from_record))

    def __init__(self, config, from_record: str, to_record: str) -> None:
        """Initialize object."""
        self.config = config
        self.directory = os.path.dirname(self.config.directory)
        self.from_record = from_record
        self.to_record = to_record
        self.destination_type = None
        self.validated = False

    def __eq__(self, other) -> bool:
        """Compare two ConfigRecord objects."""
        if type(other) is not ConfigRecord:
            return False

        return (
                self.directory == other.directory and self.from_record == other.from_record and self.to_record ==
                other.to_record and self.destination_type == other.destination_type)

    def validate(self, index: int, flags: dict[str, bool]) -> int:
        """Validate the record."""
        files = self.get_amount_of_files()
        if files == 0:
            if flags["DELETE_RECORDS_WITH_MISSING_IMAGE"]:
                self.delete_record(index)
                logger.log("info",
                           f'{self.config.directory}: Record from="{self.from_record}" to="{self.to_record}" did not '
                           f'have an image file and has been deleted.')
                index -= 1

            elif not flags["IGNORE_MISSING_IMAGES"]:
                logger.log("warning",
                           f'{self.config.directory}: Record from="{self.from_record}" to="{self.to_record}" does not '
                           f'have an image file.')
        elif files > 1:
            logger.log("warning",
                       f'{self.config.directory}: Record from="{self.from_record}" to="{self.to_record} has {files} '
                       f'matching image files.')

        if not self.validate_to_path():
            logger.log("important",
                       f'{self.config.directory}: Record from="{self.from_record}" to="{self.to_record}" has an '
                       f'invalid to-path.')

        elif not self.validate_destination_id():
            logger.log("important",
                       f'{self.config.directory}: Record from="{self.from_record}" to="{self.to_record}" has an '
                       f'invalid ID in to-path.')

        elif not flags["IGNORE_NON-MATCHING_IDS"] and not self.validate_image_id():
            logger.log("warning",
                       f'{self.config.directory}: Record from="{self.from_record}" to="{self.to_record}" has '
                       f'non-matching IDs in image file and destination.')

        self.validated = True
        variables.PROGRESS.check_save()
        return index + 1

    def delete_record(self, index: int) -> None:
        """Delete the record from config."""
        regex = r'<\s*record\s+from\s*=\s*"' + re.escape(self.from_record) + r'"\s+to\s*=\s*"' + re.escape(
                self.to_record) + r'"\s*/\s*>\s*'
        self.config.config_string = re.sub(regex, "", self.config.config_string)

        del self.config.records[index]

    def get_amount_of_files(self) -> int:
        """Get the amount of files the record points to. Should be 1."""
        found_files = 0
        for extension in variables.PROGRESS.image_file_extensions:
            if os.path.exists(f"{self.from_record_path}.{extension}"):
                found_files += 1

        return found_files

    def validate_to_path(self) -> bool:
        """Validate the to-path of a record."""
        if self.to_record in variables.PROGRESS.valid_to_paths:
            self.destination_type = self.to_record
            return True

        for path in variables.PROGRESS.valid_to_paths:
            regex_path = path.replace("{id}", r"[^/]+")
            if re.fullmatch(regex_path, self.to_record):
                self.destination_type = path
                return True

        return False

    def validate_destination_id(self) -> bool:
        """Validate the ID of a to-path in record."""
        self.destination_type = self.destination_type.replace("{id}", r"[0-9]+")
        return bool(re.fullmatch(self.destination_type, self.to_record))

    def validate_image_id(self) -> bool:
        """Check the from-record, and if the image has number for a name, make sure it matches with the config ID."""
        match = re.search(r"(?:^|/)(?P<id>\d+)$", self.from_record)
        if not match:
            return True
        from_id = int(match.group("id"))

        match = re.search(r"\D*(?P<id>\d+)\D*", self.to_record)
        if not match:
            return True
        to_id = int(match.group("id"))

        return from_id == to_id
