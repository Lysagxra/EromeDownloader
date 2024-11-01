"""
This module provides utility functions for tracking download progress and
displaying logs using the Rich library. It includes features for creating a
progress bar, a formatted progress table for monitoring download status, and
a log table for displaying downloaded messages.
"""

from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn
)

TITLE_COLOR = "light_cyan3"

def create_progress_bar():
    """
    Creates and returns a progress bar for tracking download progress.

    Returns:
        Progress: A Progress object configured with relevant columns.
    """
    return Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
    )

def create_progress_table(overall_progress, job_progress):
    """
    Creates a formatted progress table for tracking the download.

    Parameters:
        overall_progress (str): A string representing the overall progress of
                                the download.
        job_progress (Progress): An instance of a progress tracking object that 
                                 manages the download progress of individual
                                 files.

    Returns:
        Table: A rich Table object containing a grid layout with two panels:
               one for overall progress and another for job-specific progress, 
               each with styled titles and borders.
    """
    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            overall_progress,
            title=f"[b {TITLE_COLOR}]Overall Progress",
            border_style="bright_blue",
            padding=(1, 1),
            width=40
        ),
        Panel.fit(
            job_progress,
            title=f"[b {TITLE_COLOR}]Post Progress",
            border_style="medium_purple",
            padding=(1, 1),
            width=40
        ),
    )
    return progress_table

def create_log_table(log_messages):
    """
    Creates a formatted log table to display downloaded messages.

    Parameters:
        log_messages (Progress): An instance of a progress tracking object.

    Returns:
        Table: A rich Table object containing the formatted log panel with 
               the specified log messages.
    """
    log_row = "\n".join([f"• {message}" for message in log_messages])
    log_table = Table.grid()
    log_table.add_row(
        Panel(
            log_row,
            title=f"[b {TITLE_COLOR}]Log Messages",
            border_style="grey35",
            padding=(1, 1),
            width=80
        )
    )
    return log_table
