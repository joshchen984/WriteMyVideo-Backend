from app import app
from flask import render_template, url_for, request, redirect, flash, abort
from create_video import VideoCreator
import os
from app.utils import check_for_err, get_filename, create_tmp
import shutil


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

            is_error, error_msg, category = check_for_err(
                transcript, audio, use_audio)
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
                flash(str(e), "warning")
                return redirect(url_for("index"))
            finally:
                # deleting tmp directory after image has been created
                shutil.rmtree(tmp_dir)

            return redirect(url_for('show', video_name=video_name))


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
