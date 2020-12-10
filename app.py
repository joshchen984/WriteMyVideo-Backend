from flask import Flask, render_template, url_for, request, redirect, flash
from create_video import VideoCreator
import os
import shutil
import yaml
import oschmod
import string
import random
import logging
import traceback

logging.basicConfig(filename="logs/logs.log", level=logging.INFO)
app = Flask(__name__)
with open("config.yaml") as f:
    config = yaml.safe_load(f)

app.config['SECRET_KEY'] = config['SECRET_KEY']


@app.route("/", methods=["GET"])
def index():
    """Home page
    """
    return render_template("index.html")


@app.route('/create-video', methods=["POST"])
def create():
    if request.method == 'POST':
        if request.files:
            POST = request.form
            use_audio = POST.get('use_audio')
            usage_rights = POST.get("usage_rights")
            transcript = request.files['transcript']
            audio = request.files['audio']

            # allowed file extensions
            TRANSCRIPT_EXT = [".txt"]
            AUDIO_EXT = [".mp3"]

            # checking for possible errors
            if transcript.filename == '':
                # checking if transcript has been uploaded
                flash("Missing Transcript", 'warning')
                return redirect(url_for("index"))
            pre, ext = os.path.splitext(transcript.filename)
            if ext not in TRANSCRIPT_EXT:
                # checking if transcript has right file extension
                flash(f"Transcript cannot have a {ext} file extension", 'warning')
                return redirect(url_for("index"))
            if use_audio:
                if audio.filename == '':
                    # checking if audio has been uploaded
                    flash("Missing Audio File", 'warning')
                    return redirect(url_for("index"))
                pre, ext = os.path.splitext(audio.filename)
                if ext not in AUDIO_EXT:
                    # checking if audio has right file extension
                    flash(f"Audio cannot have a {ext} file extension", 'warning')
                    return redirect(url_for("index"))

            # deleting tmp directory then creating new tmp directory
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            images_dir = os.path.join(tmp_dir, "images")
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
            # sometimes there's a permission denied error so we use chmod
            oschmod.set_mode(os.getcwd(), 700)
            os.makedirs(images_dir, exist_ok=True)

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
                msg = traceback.format_exc()
                logging.error(msg)
                return redirect(url_for("error", error_msg=str(e)))

            # create webm file
            # pre, ext = os.path.splitext(videopath)
            # webm_video = pre + ".webm"
            # command = f"ffmpeg -i {videopath} {webm_video}"
            # subprocess.run(command, shell = True, env = {'PATH':ffmpeg_path})
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
    if video_name is None:
        return
    return render_template("show-video.html", video_name=video_name)


@app.route("/error")
def error():
    """Shows error page and displays error message
    """
    error_msg = request.args.get("error_msg")
    return render_template("error.html", error_msg=error_msg)


if __name__ == "__main__":
    app.run(debug=True)
