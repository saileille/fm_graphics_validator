"""Global variables of the program."""

# Progress variables.
PROGRESS = None

# Print update variables.
NEXT_UPDATE = 0  # Seconds since the epoch.
PRINT_UPDATE_INTERVAL = 1  # Seconds between print updates.

# Flags.
FLAGS = {}
VALID_FLAGS = {"CONVERT_UTF-8-BOM", "DELETE_DUPLICATE_RECORDS", "DELETE_RECORDS_WITH_MISSING_IMAGE",
               "IGNORE_MISSING_IMAGES", "IGNORE_MISSING_RECORDS", "IGNORE_MULTI_USE_IMAGES", "IGNORE_NON-IMAGE_FILES",
               "IGNORE_NON-MATCHING_IDS", "REFORMAT_CONFIG_FILES"}

CONSOLE_LINE_LENGTH = 0  # Used for replacing old prints with whitespace.
