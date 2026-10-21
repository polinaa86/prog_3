"""Read, merge, and write MIME application associations."""

from configparser import ConfigParser
from copy import deepcopy

SECTIONS = (
    "Default Applications",
    "Added Associations",
    "Removed Associations",
)


def read_associations(path: str) -> dict:
    """Read a mimeapps.list file into a nested dictionary."""
    config = ConfigParser(interpolation=None, strict=False)
    config.optionxform = str
    with open(path, "r", encoding="utf-8") as file:
        config.read_file(file)
    result = {}
    for section in config.sections():
        if section not in SECTIONS:
            continue
        result[section] = {}
        for mime_type, value in config.items(section):
            result[section][mime_type] = [
                item.strip() for item in value.split(";") if item.strip()
            ]
    return result


def merge_associations(old: dict, new: dict) -> dict:
    """Return a deep-copied merge with new MIME entries taking priority."""
    result = deepcopy(old)
    for section, mime_types in new.items():
        if section not in result:
            result[section] = {}
        for mime_type, applications in mime_types.items():
            result[section][mime_type] = deepcopy(applications)
    return result


def write_associations(associations: dict, path: str) -> None:
    """Write nonempty sections in the prescribed order."""
    with open(path, "w", encoding="utf-8") as file:
        first_section = True
        for section in SECTIONS:
            mime_types = associations.get(section, {})
            if not mime_types:
                continue
            if not first_section:
                file.write("\n")
            file.write(f"[{section}]\n")
            for mime_type, applications in mime_types.items():
                file.write(f"{mime_type}={';'.join(applications)}\n")
            first_section = False
