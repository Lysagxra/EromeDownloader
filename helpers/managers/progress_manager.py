"""
This module provides a `ProgressManager` class for tracking and displaying the
progress of multiple tasks with an overall progress bar. It uses the Rich
library to create dynamic, formatted progress bars and tables for monitoring
task completion.
"""

from collections import deque
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn
)

class ProgressManager:
    """
    Manages and tracks the progress of multiple tasks, displaying individual
    progress bars for each task alongside an overall progress bar.

    Args:
        task_name (str): The name of the task to be displayed in the progress
                         bar.
        item_description (str): A description of the individual items being
                                processed.
        color (str): The color used for displaying progress bars. Default is
                     "light_cyan3".
        overall_buffer_size (int): The maximum number of completed tasks to
                                   store in the buffer for overall progress.
                                   Default is 5.
    """

    def __init__(
        self, task_name, item_description,
        color="light_cyan3", overall_buffer_size=5
    ):
        self.task_name = task_name
        self.item_description = item_description
        self.color = color
        self.overall_progress = create_progress_bar()
        self.task_progress = create_progress_bar()
        self.num_tasks = 0
        self.overall_buffer = deque(maxlen=overall_buffer_size)

    def add_overall_task(self, description, num_tasks):
        """
        Adds an overall progress task with a given description and total tasks.
        """
        self.num_tasks = num_tasks
        overall_description = adjust_description(description)
        self.overall_progress.add_task(
            f"[{self.color}]{overall_description}",
            total=num_tasks,
            completed=0
        )

    def add_task(self, current_task=0, total=100):
        """Adds an individual task to the task progress bar."""
        task_description = (
            f"[{self.color}]{self.item_description} "
            f"{current_task + 1}/{self.num_tasks}"
        )
        return self.task_progress.add_task(task_description, total=total)

    def update_task(self, task_id, completed=None, advance=0, visible=True):
        """
        Updates the progress of an individual task and the overall progress.
        """
        self.task_progress.update(
            task_id,
            completed=completed if completed is not None else None,
            advance=advance if completed is None else None,
            visible=visible
        )
        self._update_overall_task(task_id)

    def create_progress_table(self):
        """Creates a formatted progress table for tracking the download."""
        progress_table = Table.grid()
        progress_table.add_row(
            Panel.fit(
                self.overall_progress,
                title=f"[bold {self.color}]Overall Progress",
                border_style="bright_blue",
                padding=(1, 1),
                width=40
            ),
            Panel.fit(
                self.task_progress,
                title=f"[bold {self.color}]{self.task_name} Progress",
                border_style="medium_purple",
                padding=(1, 1),
                width=40
            )
        )
        return progress_table

    # Private methods
    def _update_overall_task(self, task_id):
        """
        Advances the overall progress when a task is finished and removes old
        tasks from the buffer if necessary.
        """
        # Access the latest task dynamically
        current_overall_task = self.overall_progress.tasks[-1]

        # If the task is finished, remove it and update the overall progress
        if self.task_progress.tasks[task_id].finished:
            self.overall_progress.advance(current_overall_task.id)
            self.task_progress.update(task_id, visible=False)

        # Track completed overall tasks
        if current_overall_task.finished:
            self.overall_buffer.append(current_overall_task)

        # Cleanup completed overall tasks
        self._cleanup_completed_overall_tasks()

    def _cleanup_completed_overall_tasks(self):
        """
        Removes the oldest completed overall task from the buffer and progress
        bar if the number of visible tasks exceeds `max_visible_overall`.
        """
        if len(self.overall_buffer) == self.overall_buffer.maxlen:
            completed_overall_id = self.overall_buffer.popleft().id
            self.overall_progress.remove_task(completed_overall_id)

def adjust_description(description, max_length=8):
    """
    Truncates a string to a specified maximum length, adding an ellipsis if
    truncated.
    """
    return (
        description[:max_length] + "..." if len(description) > max_length
        else description
    )

def create_progress_bar(columns=None):
    """
    Creates and returns a progress bar for tracking download progress.
    """
    if columns is None:
        columns = [
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
        ]
    return Progress("{task.description}", *columns)
