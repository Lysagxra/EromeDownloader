"""
A module that provides functionality for managing and displaying live updates
in the terminal. It combines a progress table and a logger table into a
real-time display, allowing dynamic updates of both tables. The `LiveManager`
class handles the integration and refresh of the live view.
"""

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
            self.render_live_view(),
            refresh_per_second=refresh_per_second
        )

    def render_live_view(self):
        """
        Renders the combined live view of the progress table and the logger
        table.

        Returns:
            Group: A Group containing both the progress table and the log
                   panel.
        """
        return Group(
            self.progress_table,
            self.logger.render_log_panel()
        )

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
        """
        Logs an event and refreshes the live display.

        Args:
            event (str): The type of event.
            details (str): The event details.
        """
        self.logger.log(event, details)
        self.live.update(self.render_live_view())

    def start(self):
        """Start the live display."""
        self.live.start()

    def stop(self):
        """Stop the live display."""
        self.live.stop()
