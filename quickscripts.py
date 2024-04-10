"""Functions for generating a config file."""
import os
import re

import logger


def generate(folder: str, destination: str) -> None:
    """Generate a config file."""
    logger.print_new(f"Generating a config file for {folder}...")
    ids = set()
    filepath = os.path.join(folder, "config.xml")
    for _, _, files in os.walk(folder):
        for filename in files:
            logger.print_progress(f"{len(ids):,} files found.")
            name = os.path.splitext(filename)[0]
            try:
                ids.add(int(name))
            except ValueError:
                continue

    logger.print_new(f"{len(ids):,} files found.")

    string = ('<record>\n\t<boolean id="preload" value="false"/>\n\t<boolean id="amap" value="false"/>\n\t<list '
              'id="maps">')

    progress = 0
    for record_id in ids:
        logger.print_progress(f"{progress:,} / {len(ids):,} records created.")
        string += f'\n\t\t<record from="{record_id}" to="{destination}"/>'.replace("{id}", str(record_id))
        progress += 1

    logger.print_new(f"{progress:,} / {len(ids):,} records created.")
    string += "\n\t</list>\n</record>"

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(string)


def rename_or_delete(delete_list: set, old_name: str, new_name: str) -> bool:
    """
    Rename the file if the new name does not already exist, otherwise set for deletion.

    Return True if file was renamed, False if file was set for deletion.
    """
    if not os.path.exists(new_name):
        os.rename(old_name, new_name)
        return True

    delete_list.add(old_name)
    return False


def convert_to_id(delete_list: set, full_path: str) -> bool:
    """Convert filename to ID. Return True if file was renamed."""
    (folder, filename) = os.path.split(full_path)
    (name, ext) = os.path.splitext(filename)
    match = re.fullmatch(r"(?P<id>[0-9]+).*", name)
    if not match:
        return False

    new_path = os.path.join(folder, match.group("id") + ext)
    if new_path == full_path:
        return False

    return rename_or_delete(delete_list, full_path, new_path)


def delete_imageoptims(directory: str) -> None:
    """Try to convert imageoptim file names to ID file names. If not successful, will remove the file."""
    logger.print_new(f"Renaming and deleting imageoptims in {directory}...")
    delete_files = set()
    renamed = 0
    progress = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            logger.print_progress(f"{progress:,} processed, {renamed:,} renamed, {len(delete_files):,} to be deleted.")

            progress += 1
            match = re.fullmatch(r"\.(?P<id>[0-9]+)~imageoptim\.png", filename)
            if not match:
                continue

            was_renamed = rename_or_delete(delete_files, os.path.join(root, filename),
                                           os.path.join(root, f"{match.group('id')}.png"))

            if was_renamed:
                renamed += 1

    logger.print_new(f"{progress:,} processed, {renamed:,} renamed, {len(delete_files):,} to be deleted.")
    deleted = 0
    total = len(delete_files)
    for file in delete_files:
        logger.print_progress(f"{deleted:,} / {total:,} deleted.")
        os.remove(file)

        deleted += 1


def delete_non_id_files(directory: str) -> None:
    """Try to rename all files to have ID as a name. If not possible, delete."""
    logger.print_new(f"Renaming and deleting non-ID files in {directory}...")
    delete_list = set()
    renamed = 0
    progress = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            logger.print_progress(f"{progress:,} processed, {renamed:,} renamed, {len(delete_list):,} to be deleted.")

            progress += 1
            if convert_to_id(delete_list, str(os.path.join(root, filename))):
                renamed += 1

    logger.print_new(f"{progress:,} processed, {renamed:,} renamed, {len(delete_list):,} to be deleted.")
    deleted = 0
    total = len(delete_list)
    for file in delete_list:
        logger.print_progress(f"{deleted:,} / {total:,} deleted.")
        os.remove(file)

        deleted += 1


if __name__ == "__main__":
    data = {
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Steel Logos\Clubs\Normal\Normal":
            "graphics/pictures/club/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Steel Logos\Clubs\Normal\Small":
            "graphics/pictures/club/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Steel "
        r"Logos\Competitions\Normal\Normal": "graphics/pictures/comp/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Steel "
        r"Logos\Competitions\Normal\Small": "graphics/pictures/comp/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Stone Logos\Clubs\Normal\Normal":
            "graphics/pictures/club/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Stone Logos\Clubs\Normal\Small":
            "graphics/pictures/club/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Stone "
        r"Logos\Competitions\Normal\Normal": "graphics/pictures/comp/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Stone "
        r"Logos\Competitions\Normal\Small": "graphics/pictures/comp/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Vapour Logos\Clubs\Normal\Normal":
            "graphics/pictures/club/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Vapour Logos\Clubs\Normal\Small":
            "graphics/pictures/club/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Vapour "
        r"Logos\Competitions\Normal\Normal": "graphics/pictures/comp/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMG Vapour "
        r"Logos\Competitions\Normal\Small": "graphics/pictures/comp/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMV Logos\Clubs\Normal\Normal":
            "graphics/pictures/club/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMV Logos\Clubs\Normal\Small":
            "graphics/pictures/club/{id}/icon",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMV Logos\Competitions\Normal\Normal":
            "graphics/pictures/comp/{id}/logo",
        r"E:\Tiedostot\football manager\Football Manager 2024\graphics\logos\FMV Logos\Competitions\Normal\Small":
            "graphics/pictures/comp/{id}/icon",
    }
    for key, value in data.items():
        generate(key, value)
