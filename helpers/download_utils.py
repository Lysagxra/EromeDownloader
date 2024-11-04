"""
This module provides utilities for handling file downloads with progress
tracking.
"""

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

    return 256 * KB

def save_file_with_progress(response, download_path, task_info):
    """
    Handles the HTTP response for a file download.

    Args:
        response (Response): The HTTP response object containing the file data.
        download_path (str): The local file path where the content should be
                             saved.

    Returns:
        None: The function performs file writing and does not return a value.

    Raises:
        IOError: If there is an issue writing to the specified download path.
    """
    (job_progress, task, overall_progress, overall_task) = task_info
    file_size = int(response.headers.get("content-length", -1))
    total_downloaded = 0

    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=get_chunk_size(file_size)):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_percentage = (total_downloaded / file_size) * 100
                job_progress.update(task, completed=progress_percentage)

    job_progress.update(task, completed=100, visible=False)
    overall_progress.advance(overall_task)
