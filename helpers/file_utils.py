"""
This module provides utility functions for file input and output operations. It 
includes methods to read the contents of a file and to write content to a file, 
with optional support for clearing the file.
"""

def read_file(filename):
    """
    Reads the contents of a file and returns a list of its lines.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        list: A list of lines from the file, with newline characters removed.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

def write_file(filename, content=''):
    """
    Writes content to a specified file. If content is not provided, the file is
    cleared.

    Args:
        filename (str): The path to the file to be written to.
        content (str, optional): The content to write to the file. Defaults to
                                 an empty string, which clears the file.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
