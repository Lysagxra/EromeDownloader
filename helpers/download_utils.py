"""
This module provides utilities for handling file downloads with progress
tracking.
"""

from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 3

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
        (1 * MB, 4 * KB),     # Less than 1 MB
        (10 * MB, 16 * KB),   # 1 MB to 10 MB
        (100 * MB, 64 * KB),  # 10 MB to 100 MB
    ]

    for threshold, chunk_size in thresholds:
        if file_size < threshold:
            return chunk_size

    return 128 * KB

def save_file_with_progress(response, download_path, task, live_manager):
    """
    Saves the content of a response to a file while tracking and updating
    download progress.

    Args:
        response (requests.Response): The HTTP response containing the content
                                      to be downloaded.
        download_path (str): The local file path where the content should be
                             saved.
        task (int): The task ID used to track and report progress of the
                    download.
        live_manager (LiveManager): An object responsible for managing and
                                    tracking the progress of live tasks.
    """
    file_size = int(response.headers.get("content-length", -1))
    chunk_size=get_chunk_size(file_size)
    total_downloaded = 0

    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_percentage = (total_downloaded / file_size) * 100
                live_manager.update_task(task, completed=progress_percentage)

def run_in_parallel(func, items, live_manager, identifier, *args):
    """
    Executes a function in parallel for a list of items, using multiple worker
    threads.

    Args:
        func (callable): The function to execute in parallel for each item. It
                         will be passed the current item, task ID, and the live
                         manager along with any additional arguments.
        items (iterable): An iterable containing the items to process in
                          parallel.
        live_manager (LiveManager): An object responsible for managing and
                                    tracking the progress of live tasks.
        identifier (str): A unique identifier used to track the overall task's
                          progress in the live manager.
        *args: Additional arguments passed to `func` for each execution.
    """
    num_items = len(items)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        live_manager.add_overall_task(identifier, num_items)

        for current_task, item in enumerate(items):
            task_id = live_manager.add_task(current_task=current_task)
            executor.submit(func, item, task_id, live_manager, *args)
