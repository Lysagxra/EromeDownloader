"""Module that provides functionality for managing and displaying live updates.

It combines a progress table and a logger table into a real-time display, allowing
dynamic updates of both tables. The `LiveManager` class handles the integration and
refresh of the live view.
"""
from __future__ import annotations

import datetime
import time
from typing import TYPE_CHECKING

from rich.console import Group
from rich.live import Live

if TYPE_CHECKING:
    from .log_manager import LoggerTable
    from .progress_manager import ProgressManager


class LiveManager:
    """Class to manage a live display that combines a progress table and a logger table.

    It allows for real-time updates and refreshes of both progress and logs in a
    terminal.
    """

    def __init__(
        self,
        progress_manager: ProgressManager,
        logger: LoggerTable,
        refresh_per_second: int = 10,
    ) -> None:
        """Initialize the progress manager and logger, and set up the live view."""
        self.progress_manager = progress_manager
        self.progress_table = self.progress_manager.create_progress_table()
        self.logger = logger
        self.live = Live(
            self._render_live_view(), refresh_per_second=refresh_per_second,
        )

        self.start_time = time.time()
        self.update_log("Script started", "The script has started execution.")

    def add_overall_task(self, description: str, num_tasks: int) -> None:
        """Call ProgressManager to add an overall task."""
        self.progress_manager.add_overall_task(description, num_tasks)

    def add_task(self, current_task: int = 0, total: int = 100) -> int:
        """Call ProgressManager to add an individual task."""
        return self.progress_manager.add_task(current_task, total)

    def update_task(
        self,
        task_id: int,
        completed: int | None = None,
        advance: int = 0,
        *,
        visible: bool = True,
    ) -> None:
        """Call ProgressManager to update an individual task."""
        self.progress_manager.update_task(task_id, completed, advance, visible=visible)

    def update_log(self, event: str, details: str) -> None:
        """Log an event and refreshes the live display."""
        self.logger.log(event, details)
        self.live.update(self._render_live_view())

    def start(self) -> None:
        """Start the live display."""
        self.live.start()

    def stop(self) -> None:
        """Stop the live display and log the execution time."""
        execution_time = self._compute_execution_time()

        # Log the execution time in hh:mm:ss format
        self.update_log(
            "Script ended",
            f"The script has finished execution. Execution time: {execution_time}",
        )
        self.live.stop()

    # Private methods
    def _render_live_view(self) -> Group:
        """Render the combined live view of the progress table and the logger table."""
        return Group(self.progress_table, self.logger.render_log_panel())

    def _compute_execution_time(self) -> str:
        """Compute and format the execution time of the script."""
        execution_time = time.time() - self.start_time
        time_delta = datetime.timedelta(seconds=execution_time)

        # Extract hours, minutes, and seconds from the timedelta object
        hours = time_delta.seconds // 3600
        minutes = (time_delta.seconds % 3600) // 60
        seconds = time_delta.seconds % 60

        return f"{hours:02} hrs {minutes:02} mins {seconds:02} secs"
