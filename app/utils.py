import os
import string
import random
import shutil
from typing import Callable
from app.create_video import VideoCreator
from app.exceptions import FailedAlignmentError
from flask import current_app
from app import app

def create_tmp():
    """
    Creates tmp and images directory

    Returns:
        (str): tmp directory name
    """
    # creating tmp directory
    tmp_name = get_filename(10)
    while os.path.isdir(f"tmp/{tmp_name}"):
        tmp_name = get_filename(10)
    tmp_dir = os.path.join(os.getcwd(), "tmp", tmp_name)
    images_dir = os.path.join(tmp_dir, "images")
    os.makedirs(images_dir)
    return tmp_name


def get_tmp_paths(tmp_name: str):
    """
    Returns path of tmp and images directory

    Returns:
        (tuple): (tmp_dir, images_dir, textpath, audiopath)
    """
    tmp_dir = os.path.join(os.getcwd(), "tmp", tmp_name)
    images_dir = os.path.join(tmp_dir, "images")
    textpath = os.path.join(tmp_dir, "text.txt")
    audiopath = os.path.join(tmp_dir, "audio.mp3")

    return tmp_dir, images_dir, textpath, audiopath


def check_for_err(transcript, audio, use_audio):
    """Checks for errors in POST request

    Args:
        transcript:
        audio:
        use_audio:

    Returns:
        (tuple): tuple containing:
            is_error (bool): If code found an error
            msg (string): Error message.
    """
    # allowed file extensions
    TRANSCRIPT_EXT = [".txt"]
    AUDIO_EXT = [".mp3"]

    # checking for possible errors
    if transcript.filename == "":
        # checking if transcript has been uploaded
        return True, "Missing Transcript"
    _, ext = os.path.splitext(transcript.filename)
    if ext not in TRANSCRIPT_EXT:
        # checking if transcript has right file extension
        return True, f"Transcript cannot have a {ext} file extension"
    if use_audio:
        if audio.filename == "":
            # checking if audio has been uploaded
            return True, "Missing Audio File"
        _, ext = os.path.splitext(audio.filename)
        if ext not in AUDIO_EXT:
            # checking if audio has right file extension
            return True, f"Audio cannot have a {ext} file extension"
    return False, None


def get_filename(length):
    """Generates a random filename for a file

    Args:
        length: Length of generated filename

    Returns:
        string: filename without an extension
    """
    chars = string.ascii_letters
    filename = "".join([random.choice(chars) for _ in range(length)])
    return filename


def get_video_name():
    """Generates a unique video name"""
    video_name = get_filename(10)
    while os.path.isfile(f"app/static/videos/{video_name}.mp4"):
        video_name = get_filename(10)
    return video_name


def create_video(
    video_name,
    images_dir,
    tmp_dir,
    use_audio,
    audiopath,
    textpath,
    usage_rights,
    use_images=False,
    images=None,
):
    """Creates a video."""

    creator = VideoCreator(
        images_dir,
        tmp_dir,
        use_audio,
        audiopath,
        textpath,
        usage_rights,
        f"app/static/videos/{video_name}.mp4",
        use_images,
        images,
    )
    try:
        creator.create_full_video()
    except FailedAlignmentError as exc:
        raise Exception(
            "Couldn't align the audio with the script. Please try recording the audio again."
        ) from exc
    finally:
        # deleting tmp directory after image has been created
        shutil.rmtree(tmp_dir)


def run_task(function: Callable, *args, **kwargs):
    """Queue task

    Args:
        function (Callable): Function to queue
        *args: args to pass to function
        **kwargs: kwargs to pass to function
    """
    app.logger.info(f'Task named "{function.__name__}" queued')
    current_app.task_queue.enqueue(function, *args, **kwargs)
