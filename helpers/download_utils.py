"""
This module provides utilities for handling file downloads with progress
tracking.
"""

import re
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 3
TASK_COLOR = 'cyan'

KB = 1024
MB = 1024 * KB

def remove_special_characters(input_string):
    """
    Removes special characters from the input string, keeping only letters,
    numbers, underscores, dashes, and dots.

    Args:
        input_string (str): The string from which to remove special characters.

    Returns:
        str: The cleaned string containing only letters and numbers.
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '', input_string)

def get_episode_filename(download_link):
    """
    Extract the file name from the provided episode download link.

    Args:
        download_link (str): The download link for the episode.

    Returns:
        str: The extracted file name, or None if the link is None or empty.
    """
    if download_link:
        try:
            filename = unquote(download_link.split('=')[-1])  # Original name
            return remove_special_characters(filename)        # Cleaned name

        except IndexError as indx_err:
            print(f"Error while extracting the file name: {indx_err}")

    return None

def get_chunk_size(file_size):
    """
    Determines the optimal chunk size based on the file size.

    Args:
        file_size (int): The size of the file in bytes.

    Returns:
        int: The optimal chunk size in bytes.
    """
    thresholds = [
        (50 * MB, 256 * KB),   # Less than 50 MB
        (100 * MB, 512 * KB),  # 50 MB to 100 MB
        (250 * MB, 2 * MB),    # 100 MB to 250 MB
    ]

    for threshold, chunk_size in thresholds:
        if file_size < threshold:
            return chunk_size

    return 4 * MB

def save_file_with_progress(response, final_path, task_info):
    """
    Saves a file to the specified path while tracking and updating progress.

    Args:
        response (requests.Response): The response object containing the file
                                      content to be downloaded.
        final_path (str): The path where the file will be saved.
        task_info (tuple): A tuple containing progress-related objects:
                           - job_progress: The progress tracker for the job.
                           - task: The specific task being tracked.
                           - overall_task: The overall task tracker.
    """
    (job_progress, task, overall_task) = task_info
    file_size = int(response.headers.get('content-length', -1))
    chunk_size = get_chunk_size(file_size)
    total_downloaded = 0

    with open(final_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_percentage = (total_downloaded / file_size) * 100
                job_progress.update(task, completed=progress_percentage)

    job_progress.update(task, completed=100, visible=False)
    job_progress.advance(overall_task)

def manage_running_tasks(futures, job_progress):
    """
    Manage the status of running tasks and update their progress.

    Args:
        futures (dict): A dictionary where keys are futures representing the
                        tasks that have been submitted for execution, and
                        values are the associated task identifiers in the
                        job progress tracking system.
        job_progress: An object responsible for tracking the progress of tasks,
                      providing methods to update and manage task visibility.
    """
    while futures:
        for future in list(futures.keys()):
            if future.running():
                task = futures.pop(future)
                job_progress.update(task, visible=True)

def run_in_parallel(func, items, job_progress, *args):
    """
    Execute a function in parallel for a list of items, updating progress in a
    job tracker.

    Args:
        func (callable): The function to be executed for each item in the
                         `items` list.
        items (iterable): A list of items to be processed by the `func`.
        job_progress: An object responsible for managing and displaying the
                      progress of tasks.
        *args: Additional positional arguments to be passed to the `func`.
    """
    num_items = len(items)
    futures = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        overall_task = job_progress.add_task(
            f"[{TASK_COLOR}]Progress", total=num_items, visible=True
        )

        for indx, item in enumerate(items):
            task = job_progress.add_task(
                f"[{TASK_COLOR}]Episode {indx + 1}/{num_items}",
                total=100, visible=False
            )
            task_info = (job_progress, task, overall_task)
            future = executor.submit(func, item, *args, task_info)
            futures[future] = task
            manage_running_tasks(futures, job_progress)
