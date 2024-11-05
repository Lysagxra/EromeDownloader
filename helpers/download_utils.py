"""
This module provides utilities for handling file downloads with progress
tracking.
"""

from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 5
TASK_COLOR = 'light_cyan3'

KB = 1024
MB = 1024 * KB

def get_chunk_size(file_size):
    """
    Determines the optimal chunk size based on the file size.

    Args:
        file_size (int): The size of the file in bytes.

    Returns:
        int: The optimal chunk size in bytes.
    """
    thresholds = [
        (MB, 4 * KB),        # Less than 1 MB
        (10 * MB, 16 * KB),  # Less than 10 MB
        (100 * MB, 64 * KB), # Less than 100 MB
    ]

    for threshold, chunk_size in thresholds:
        if file_size < threshold:
            return chunk_size

    return 128 * KB

def save_file_with_progress(response, download_path, task_info):
    """
    Handles the HTTP response for a file download.

    Args:
        response (Response): The HTTP response object containing the file data.
        download_path (str): The local file path where the content should be
                             saved.
        task_info (tuple): A tuple containing progress-related objects.
    """
    (job_progress, task, overall_progress, overall_task) = task_info
    file_size = int(response.headers.get("content-length", -1))
    chunk_size=get_chunk_size(file_size)
    total_downloaded = 0

    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_percentage = (total_downloaded / file_size) * 100
                job_progress.update(task, completed=progress_percentage)

    job_progress.update(task, completed=100, visible=False)
    overall_progress.advance(overall_task)

def manage_running_tasks(futures, job_progress):
    """
    Monitors and manages the status of running tasks.

    Args:
        futures (dict): A dictionary where keys are futures representing 
                        asynchronous tasks and values are task information 
                        to be used for progress updates.
        job_progress: An object responsible for updating the progress of 
                      tasks based on their current status.
    """
    while futures:
        for future in list(futures.keys()):
            if future.running():
                task = futures.pop(future)
                job_progress.update(task, visible=True)

def run_in_parallel(func, items, progress_info, identifier, *args):
    """
    Execute a function in parallel for a list of items, updating progress in a
    job tracker.

    Args:
        func (callable): The function to be executed for each item in the
                         `items` list.
        items (iterable): A list of items to be processed by the `func`.
        progress_info: A tuple containing informations about the current job.
        identifier (str): An identifier for the overall task.
        *args: Additional positional arguments to be passed to the `func`.
    """
    (job_progress, overall_progress) = progress_info

    num_items = len(items)
    futures = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        overall_task = overall_progress.add_task(
            f"[{TASK_COLOR}]{identifier}", total=num_items
        )
        for indx, item in enumerate(items):
            task = job_progress.add_task(
                f"[{TASK_COLOR}]File {indx + 1}/{num_items}",
                total=100, visible=False
            )
            future = executor.submit(
                func, item, *args,
                (job_progress, task, overall_progress, overall_task)
            )
            futures[future] = task
            manage_running_tasks(futures, job_progress)
