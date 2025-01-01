"""
A module that provides functionality for managing and displaying live updates
in the terminal. It combines a progress table and a logger table into a
real-time display, allowing dynamic updates of both tables. The `LiveManager`
class handles the integration and refresh of the live view.
"""

import time
import datetime

from rich.live import Live
from rich.console import Group

class LiveManager:
    """
    A class to manage a live display that combines a progress table and a
    logger table. It allows for real-time updates and refreshes of both
    progress and logs in a terminal.

    Args:
        progress_table (Table): The progress table instance to be displayed
                                live.
        logger (LoggerTable): The LoggerTable instance that handles the event
                              logs.
        refresh_per_second (int): The frequency at which the live display
                                  refreshes (default is 10).
    """

    def __init__(self, progress_manager, logger, refresh_per_second=10):
        self.progress_manager = progress_manager
        self.progress_table = self.progress_manager.create_progress_table()
        self.logger = logger
        self.live = Live(
            self._render_live_view(),
            refresh_per_second=refresh_per_second
        )

        self.start_time = time.time()
        self.update_log("Script started", "The script has started execution.")

    def add_overall_task(self, description, num_tasks):
        """Call ProgressManager to add an overall task."""
        self.progress_manager.add_overall_task(description, num_tasks)

    def add_task(self, current_task=0, total=100):
        """Call ProgressManager to add an individual task."""
        task_id = self.progress_manager.add_task(current_task, total)
        return task_id

    def update_task(self, task_id, completed=None, advance=0, visible=True):
        """Call ProgressManager to update an individual task."""
        self.progress_manager.update_task(task_id, completed, advance, visible)

    def update_log(self, event, details):
        """Logs an event and refreshes the live display."""
        self.logger.log(event, details)
        self.live.update(self._render_live_view())

    def start(self):
        """Start the live display."""
        self.live.start()

    def stop(self):
        """Stop the live display and log the execution time."""
        execution_time = self._compute_execution_time()

        # Log the execution time in hh:mm:ss format
        self.update_log(
            "Script ended",
            f"The script has finished execution. "
            f"Execution time: {execution_time}"
        )
        self.live.stop()

    # Private methods
    def _render_live_view(self):
        """
        Renders the combined live view of the progress table and the logger
        table.
        """
        return Group(
            self.progress_table,
            self.logger.render_log_panel()
        )

    def _compute_execution_time(self):
        """Compute and format the execution time of the script."""
        execution_time = time.time() - self.start_time
        time_delta = datetime.timedelta(seconds=execution_time)

        # Extract hours, minutes, and seconds from the timedelta object
        hours = time_delta.seconds // 3600
        minutes = (time_delta.seconds % 3600) // 60
        seconds = time_delta.seconds % 60

        return f"{hours:02} hrs {minutes:02} mins {seconds:02} secs"
