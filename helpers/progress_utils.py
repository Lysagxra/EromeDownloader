"""
This module provides utility functions for tracking download progress
using the Rich library. It includes features for creating a progress bar
and a formatted progress table specifically designed for monitoring
the download status of current taks.
"""

from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn
)

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
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        "•",
        TimeRemainingColumn()
    )

def create_progress_table(title, job_progress):
    """
    Creates a formatted progress table for tracking the download status of
    the current task.

    Parameters:
        title (str): The name of the task for which the progress is being
                     displayed.
        job_progress (Progress): An instance of a progress tracking object that
                                 manages the download progress.

    Returns:
        Table: A Rich Table object containing the progress panel for the
               specified task.
    """
    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            job_progress,
            title=f"[b]{title}",
            border_style="red",
            padding=(1, 1)
        )
    )
    return progress_table
