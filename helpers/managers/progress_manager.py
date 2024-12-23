"""
This module provides utility functions for tracking download progress and
displaying logs using the Rich library. It includes features for creating a
progress bar, a formatted progress table for monitoring download status, and
a log table for displaying downloaded messages.
"""

from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

class ProgressManager:
    """
    Manages progress bars for multiple tasks with an overall progress bar.

    Attributes:
        item_description (str): Description of the individual tasks.
        color (str): The color used for task descriptions in the progress bar.
        overall_progress (Progress): Progress bar for overall task completion.
        task_progress (Progress): Progress bar for tracking individual tasks.
        overall_task (TaskID): ID of the overall progress task.
        num_tasks (int): Total number of tasks to be tracked.
    """

    def __init__(self, task_name, item_description, color="light_cyan3"):
        self.task_name = task_name
        self.item_description = item_description
        self.color = color
        self.overall_progress = self.create_progress_bar()
        self.task_progress = self.create_progress_bar()
        self.overall_task = 0
        self.num_tasks = 0

    @staticmethod
    def adjust_description(description, max_length=8):
        """
        Truncates a string to a specified maximum length, adding an ellipsis if
        truncated.
        """
        return (
            description[:max_length] + "..." if len(description) > max_length
            else description
        )

    @staticmethod
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

    def add_overall_task(self, description, num_tasks):
        """
        Adds an overall progress task with a given description and total tasks.
        """
        self.num_tasks = num_tasks
        overall_description = self.adjust_description(description)
        self.overall_task = self.overall_progress.add_task(
            f"[{self.color}]{overall_description}",
            total=num_tasks, completed=0
        )

    def add_task(self, current_task=0, total=100):
        """
        Adds an individual task to the task progress bar.
        """
        task_description = (
            f"[{self.color}]{self.item_description} "
            f"{current_task + 1}/{self.num_tasks}"
        )
        return self.task_progress.add_task(task_description, total=total)

    def update_task(self, task_id, completed=None, advance=0, visible=True):
        """
        Updates the progress of an individual task and the overall progress.
        """
        if completed is not None:
            self.task_progress.update(
                task_id, completed=completed, visible=visible
            )
        else:
            self.task_progress.update(
                task_id, advance=advance, visible=visible
            )

        # Update the overall progress bar and remove the task progress bar
        # when a task is finished
        if self.task_progress.tasks[task_id].finished:
            self.overall_progress.advance(self.overall_task)
            self.task_progress.update(task_id, visible=False)

    def create_progress_table(self):
        """
        Creates a formatted progress table for tracking the download.
        """
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
