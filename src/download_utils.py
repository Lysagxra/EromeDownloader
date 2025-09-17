"""Utilities for handling file downloads with progress tracking."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from requests import Response

from src.managers.live_manager import LiveManager

from .config import LARGE_FILE_CHUNK_SIZE, MAX_WORKERS, THRESHOLDS


def get_chunk_size(file_size: int) -> int:
    """Determine the optimal chunk size based on the file size."""
    for threshold, chunk_size in THRESHOLDS:
        if file_size < threshold:
            return chunk_size

    return LARGE_FILE_CHUNK_SIZE


def save_file_with_progress(
    response: Response,
    download_path: str,
    task: int,
    live_manager: LiveManager,
) -> None:
    """Save the content of a response to a file while tracking download progress."""
    file_size = int(response.headers.get("content-length", -1))
    chunk_size = get_chunk_size(file_size)
    total_downloaded = 0

    with Path(download_path).open("wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_percentage = (total_downloaded / file_size) * 100
                live_manager.update_task(task, completed=progress_percentage)


def manage_running_tasks(futures: dict, live_manager: LiveManager) -> None:
    """Manage the status of running tasks and update their progress."""
    while futures:
        for future in list(futures.keys()):
            if future.running():
                task_id = futures.pop(future)
                live_manager.update_task(task_id, visible=True)


def run_in_parallel(
    func: callable,
    items: list,
    live_manager: LiveManager,
    identifier: str,
    *args: tuple,
) -> None:
    """Execute a function in parallel for a list of items, using multiple workers."""
    num_items = len(items)
    futures = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        live_manager.add_overall_task(identifier, num_items)

        for current_task, item in enumerate(items):
            task_id = live_manager.add_task(current_task=current_task)
            future = executor.submit(func, item, task_id, live_manager, *args)
            futures[future] = task_id
            manage_running_tasks(futures, live_manager)
