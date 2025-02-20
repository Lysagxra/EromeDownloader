"""Module that provides utility functions for file input and output operations.

It includes methods to read the contents of a file and to write content to a file, with
optional support for clearing the file.
"""

from pathlib import Path


def read_file(filename: str) -> list[str]:
    """Read the contents of a file and returns a list of its lines."""
    with Path(filename).open("r", encoding="utf-8") as file:
        return file.read().splitlines()


def write_file(filename: str, content: str = "") -> None:
    """Write content to a specified file.

    If content is not provided, the file is cleared.
    """
    with Path(filename).open("w", encoding="utf-8") as file:
        file.write(content)
