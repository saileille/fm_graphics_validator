"""Config class."""
import re

import logger
import validator
import variables
from classes.config_record import ConfigRecord


class Config:
    """Config file class."""

    @staticmethod
    def remove_comments(string: str) -> str:
        """Remove comments from the config."""
        return re.sub("<!--.*?-->", "", string, flags=re.DOTALL).strip()

    @property
    def config_images(self) -> set[str]:
        """Get all images that have a config record."""
        images = set()
        for record in self.records:
            images.add(record.from_record_path)

        return images

    @property
    def original_string(self) -> str:
        """Get original string."""
        return self.__original_string

    def __init__(self, directory: str) -> None:
        """Initialize object."""
        self.directory = directory
        self.__original_string = None
        self.config_string = None
        self.booleans = {"preload": None, "amap": None}
        self.records = []
        self.validated = False

    def __str__(self) -> str:
        """Get the config file as a string."""
        indent = variables.PROGRESS.config_format["indent"]
        string = "<record>\n"
        boolean_values = {True: "true", False: "false", None: "none"}
        for key, value in self.booleans.items():
            if value is None:
                continue
            string += f'{indent}<boolean id="{key}" value="{boolean_values[value]}"/>\n'

        string += f'{indent}<list id="maps">\n'
        record_list = sorted(self.records, key=lambda obj: (obj.from_record, obj.to_record))
        for record in record_list:
            string += f'{indent * 2}<record from="{record.from_record}" to="{record.to_record}"/>\n'

        string += f"{indent}</list>\n</record>"
        return string

    def config_has_destination(self, to_record: str) -> bool:
        """Check if the config file has a specific destination."""
        for record in self.records:
            if to_record == record.to_record:
                return True

        return False

    def config_has_source(self, from_record: str) -> bool:
        """Check if the config file has a specific source."""
        for record in self.records:
            if from_record == record.from_record:
                return True

        return False

    def config_has_record(self, from_record: str, to_record: str) -> bool:
        """Check if the config file has a specific record."""
        for record in self.records:
            if from_record == record.from_record and to_record == record.to_record:
                return True

        return False

    def load(self) -> bool:
        """Load the config file."""
        try:
            with open(self.directory, encoding="utf-8") as file:
                self.__original_string = file.read()
        except UnicodeDecodeError:
            logger.log("critical",
                       f"{self.directory}: Failed to load the config file. Make sure the file encoding is UTF-8.")
            return False

        self.config_string = self.original_string
        return True

    def save(self) -> None:
        """Save the config file."""
        with open(self.directory, "w", encoding="utf-8") as file:
            file.write(self.config_string)

    def validate(self, config_progress) -> None:
        """Validate a single config file."""
        if not self.load():
            return
        if not self.convert_bom():
            return
        if not self.parse(config_progress):
            return

        record_progress = 0
        total_records = len(self.records)
        index = 0

        flags = {
            "DELETE_RECORDS_WITH_MISSING_IMAGE": validator.has_flag("DELETE_RECORDS_WITH_MISSING_IMAGE",
                                                                    self.directory),
            "IGNORE_MISSING_IMAGES": validator.has_flag("IGNORE_MISSING_IMAGES", self.directory),
            "IGNORE_NON-MATCHING_IDS": validator.has_flag("IGNORE_NON-MATCHING_IDS", self.directory)
        }

        while index < len(self.records):
            record = self.records[index]
            logger.print_progress(
                    f"{config_progress} config files, {record_progress:,} / {total_records:,} records processed.")
            if not record.validated:
                index = record.validate(index, flags)

            record_progress += 1

        self.validated = True
        if validator.has_flag("REFORMAT_CONFIG_FILES", self.directory):
            self.config_string = str(self)

        if self.original_string != self.config_string:
            self.save()
            logger.log("info", f"{self.directory}: The changes made to the config file have been saved.")
        variables.PROGRESS.check_save()

    def parse(self, config_progress: int) -> bool:
        """Parse a string of config."""
        string = Config.remove_comments(self.config_string)

        string = self.validate_record_element(string)
        if string is None:
            return False

        string = self.validate_booleans(string)
        string = self.validate_maps(string)
        if string is None:
            return False

        flags = {
            "DELETE_DUPLICATE_RECORDS": validator.has_flag("DELETE_DUPLICATE_RECORDS", self.directory),
            "IGNORE_MULTI_USE_IMAGES": validator.has_flag("IGNORE_MULTI_USE_IMAGES", self.directory)
        }
        record_progress = 0
        while True:
            logger.print_progress(f"{config_progress} config files, {record_progress:,} records parsed.")
            string = string.strip()
            if not string:
                break

            match = re.fullmatch(r'(?P<record><\s*record\s+from\s*=\s*"(?P<source>[^"]*)"\s+to\s*=\s*"(?P<destination>['
                                 r'^"]*)"\s*/\s*>\s*)(?P<rest>.*)', string, re.DOTALL)

            if not match:
                logger.log("critical", f"{self.directory}: Something wrong in record "
                                       f"starting from:\n{logger.get_beginning_of_string(string, 100)}\n"
                                       f"{logger.get_console_separator()}")
                return False

            if self.config_has_record(match.group("source"), match.group("destination")):
                if flags["DELETE_DUPLICATE_RECORDS"]:
                    self.config_string = self.config_string.replace(match.group("record"), "")
                    logger.log("info", f'{self.directory}: Record from="'
                                       f'{match.group("source")}" to="{match.group("destination")}" already detected '
                                       f'in the config file. Deleted.')
                else:
                    logger.log("warning", f'{self.directory}: Record from="'
                                          f'{match.group("source")}" to="{match.group("destination")}" appears '
                                          f'multiple times in the config file.')

            else:
                if self.config_has_destination(match.group("destination")):
                    logger.log("warning", f"{self.directory}: "
                                          f"{match.group('destination')} appears multiple times in the config.")

                if not flags["IGNORE_MULTI_USE_IMAGES"] and self.config_has_source(match.group("source")):
                    logger.log("warning", f"{self.directory}: {match.group('source')} "
                                          f"is used multiple times in the config.")

                self.records.append(ConfigRecord(self, match.group("source"), match.group("destination")))
            string = match.group("rest")
            record_progress += 1

        return True

    def convert_bom(self) -> bool:
        """Convert UTF-8-BOM files to UTF-8."""
        if self.config_string[0] != "﻿":
            return True

        if not validator.has_flag("CONVERT_UTF-8-BOM", self.directory):
            logger.log("critical",
                       "File encoding is UTF-8-BOM. You must convert the file to UTF-8 to validate it. (To do this "
                       "automatically, use the flag 'CONVERT_UTF-8-BOM'.")

            return False

        logger.log("info", f"{self.directory}: File encoding is UTF-8-BOM. Saving as UTF-8...")
        self.config_string = self.config_string[1:]
        self.save()
        return True

    def validate_record_element(self, string: str) -> str | None:
        """Validate the record element."""
        match = re.fullmatch(r"<\s*record\s*>(?P<everything>.*)<\s*/\s*record\s*>", string, re.DOTALL)
        if not match:
            logger.log("critical", f"{self.directory}: Config file's contents must be "
                                   f"inside a <record> tag. Make sure that there is nothing before or after the "
                                   f"record tags.\n"
                                   f"{string}\n{logger.get_console_separator()}")
            return None

        return match.group("everything")

    def validate_booleans(self, string: str) -> str:
        """Validate the boolean tags."""
        while True:
            string = string.strip()
            match = re.fullmatch(
                    r'<\s*boolean\s+id\s*=\s*"(?P<id>[^"]*)"\s+value\s*=\s*"(?P<value>[^"]*)"\s*/\s*>(?P<rest>.*)',
                    string, re.DOTALL)
            if not match:
                return string

            self.validate_boolean(match.group("id"), match.group("value"))
            string = match.group("rest")

    def validate_boolean(self, bool_id: str, value: str) -> None:
        """Validate a single boolean tag."""
        valid_values = {"true": True, "false": False}

        if bool_id not in self.booleans:
            logger.log("important", f'{self.directory}: Boolean id="{bool_id}" value="'
                                    f'{value}" does not have a valid ID.')
            return

        if value not in valid_values:
            logger.log("important", f'{self.directory}: Boolean id="{bool_id}" value="'
                                    f'{value}" does not have a valid value.')
            return

        if self.booleans[bool_id] is not None:
            logger.log("warning", f'{self.directory}: Boolean id="{bool_id}" value="'
                                  f'{value}" has already been defined.')
            return

        self.booleans[bool_id] = valid_values[value]

    def validate_maps(self, string: str) -> str | None:
        """Validate maps list."""
        match = re.fullmatch(r'<\s*list\s+id\s*=\s*"maps"\s*>(?P<everything>.*)<\s*/\s*list\s*>', string, re.DOTALL)
        if not match:
            logger.log("critical", f"{self.directory}: Config file's list tag is not "
                                   f"correct.\n"
                                   f"{logger.get_beginning_of_string(string, 100)}\n{logger.get_console_separator()}")
            return None

        return match.group("everything")

    def get_config_string_line_char(self, string: str) -> str:
        """Get the starting line and char of a substring in a config string."""
        comment_regex = r"(?:<!--.*?-->)*"
        pattern = re.escape(string[0])
        for char in string[1:]:
            pattern += comment_regex
            pattern += re.escape(char)

        match = re.search(pattern, self.config_string, re.DOTALL)
        valid_string = self.config_string[:match.start()]
        lines = get_lines(valid_string)
        chars = get_chars_in_last_line(valid_string)

        return f"[{lines:,}:{chars:,}]"


def get_lines(string: str) -> int:
    """Get the number of lines in a string."""
    return string.count("\n") + 1


def get_chars_in_last_line(string: str) -> int:
    """Get the number of characters after the last line in string."""
    last_line = string.split("\n")[-1]
    return len(last_line)
