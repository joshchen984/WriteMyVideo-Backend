import os
import string
import random
import shutil
from app.create_video import VideoCreator
from app.exceptions import FailedAlignmentError
from flask import url_for, redirect, flash


def create_tmp():
    """
    Creates tmp and images directory
    Returns:
        (tuple): (tmp_dir, images_dir)
    """
    # creating tmp directory
    tmp_name = get_filename(10)
    while os.path.isdir(f"tmp/{tmp_name}"):
        tmp_name = get_filename(10)
    tmp_dir = os.path.join(os.getcwd(), "tmp", tmp_name)
    images_dir = os.path.join(tmp_dir, "images")
    os.makedirs(images_dir)
    return tmp_dir, images_dir


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
            category (string): category for msg. e.g: 'warning'
    """
    # allowed file extensions
    TRANSCRIPT_EXT = [".txt"]
    AUDIO_EXT = [".mp3"]

    # checking for possible errors
    if transcript.filename == '':
        # checking if transcript has been uploaded
        return True, "Missing Transcript", 'warning'
    _, ext = os.path.splitext(transcript.filename)
    if ext not in TRANSCRIPT_EXT:
        # checking if transcript has right file extension
        return True, f"Transcript cannot have a {ext} file extension", 'warning'
    if use_audio:
        if audio.filename == '':
            # checking if audio has been uploaded
            return True, "Missing Audio File", 'warning'
        _, ext = os.path.splitext(audio.filename)
        if ext not in AUDIO_EXT:
            # checking if audio has right file extension
            return True, f"Audio cannot have a {ext} file extension", 'warning'
    return False, None, None


def get_filename(length):
    """Generates a random filename for a file

    Args:
        length: Length of generated filename

    Returns:
        string: filename without an extension
    """
    chars = string.ascii_letters
    filename = ''.join([random.choice(chars) for _ in range(length)])
    return filename


def create_video(images_dir, tmp_dir, use_audio, audiopath, textpath, usage_rights, use_images=False, images=None):
    video_name = get_filename(10)
    while os.path.isfile(f"app/static/videos/{video_name}.mp4"):
        video_name = get_filename(10)

    creator = VideoCreator(images_dir, tmp_dir, use_audio, audiopath, textpath, usage_rights,
                           f"app/static/videos/{video_name}.mp4", use_images, images)
    try:
        creator.create_video()
    except FailedAlignmentError:
        flash(
            "Couldn't align the audio with the script. Please try recording the audio again.")
        return redirect(url_for("index"))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("index"))
    finally:
        # deleting tmp directory after image has been created
        shutil.rmtree(tmp_dir)
    return video_name
