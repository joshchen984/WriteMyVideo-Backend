from flask import Flask, render_template, url_for, request, redirect, flash, abort
from create_video import VideoCreator
import os
import yaml
import string
import shutil
import random
import logging
import logging.handlers as handlers

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = handlers.TimedRotatingFileHandler("logs/app.log", when="W0", backupCount=4)
formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

app = Flask(__name__)
with open("config.yaml") as f:
    config = yaml.safe_load(f)

app.config['SECRET_KEY'] = config['SECRET_KEY']


@app.route("/", methods=["GET"])
def index():
    """Home page
    """
    return render_template("index.html")


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
    pre, ext = os.path.splitext(transcript.filename)
    if ext not in TRANSCRIPT_EXT:
        # checking if transcript has right file extension
        return True, f"Transcript cannot have a {ext} file extension", 'warning'
    if use_audio:
        if audio.filename == '':
            # checking if audio has been uploaded
            return True, "Missing Audio File", 'warning'
        pre, ext = os.path.splitext(audio.filename)
        if ext not in AUDIO_EXT:
            # checking if audio has right file extension
            return True, f"Audio cannot have a {ext} file extension", 'warning'
    return False, None, None


@app.route('/create-video', methods=["POST"])
def create():
    if request.method == 'POST':
        if request.files:
            POST = request.form
            use_audio = POST.get('use_audio')
            usage_rights = POST.get("usage_rights")
            transcript = request.files['transcript']
            audio = request.files['audio']

            is_error, error_msg, category = check_for_err(transcript, audio, use_audio)
            if is_error:
                flash(error_msg, category)
                return redirect(url_for("index"))

            # creating tmp directory
            tmp_dir, images_dir = create_tmp()

            # saving files to tmp directory
            textpath = os.path.join(tmp_dir, 'text.txt')
            transcript.save(textpath)
            audiopath = os.path.join(tmp_dir, "audio.mp3")
            if use_audio:
                audio.save(audiopath)

            video_name = get_filename(10)
            while os.path.isfile(f"static/videos/{video_name}.mp4"):
                video_name = get_filename(10)

            creator = VideoCreator(images_dir, tmp_dir, use_audio, audiopath, textpath, usage_rights,
                                   f"static/videos/{video_name}.mp4")
            try:
                creator.create_video()
            except ValueError as e:
                logger.warning(str(e))
                flash(str(e), "warning")
                return redirect(url_for("index"))
            finally:
                # deleting tmp directory after image has been created
                shutil.rmtree(tmp_dir)

            return redirect(url_for('show', video_name=video_name))


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


@app.route("/show-video")
def show():
    """Displays video. Video to display is based on query string
    """
    video_name = request.args.get("video_name")
    # if query string is invalid
    vid_location = os.path.join("static", "videos", video_name + '.mp4')
    if video_name is None or not os.path.isfile(vid_location):
        abort(404)
    return render_template("show-video.html", video_name=video_name)


# @app.route("/error", methods = ["POST"])
# def error():
#     """Shows error page and displays error message
#     """
#     if request.method == "POST":
#         error_msg = request.args.get("error_msg")
#         return render_template("error.html", error_msg=error_msg)


if __name__ == "__main__":
    app.run(debug=True)
