from flask import render_template, url_for, request, redirect, abort, jsonify
import os
from werkzeug.datastructures import FileStorage
from app import app
from app.utils import check_for_err, create_tmp, create_video, get_tmp_paths


@app.route("/", methods=["GET"])
def index():
    """Home page"""
    return render_template("index.html")


@app.route("/upload-images", methods=["POST"])
def upload():
    """Creates a video or redirects to the upload images page if user uploads their own images."""
    if request.method == "POST":
        if request.files:
            POST = request.form
            use_audio: bool = POST.get("use_audio") == "true"
            usage_rights = POST.get("usage_rights")
            use_images: bool = POST.get("use_images") == "true"
            transcript: FileStorage = request.files["transcript"]
            if use_audio:
                audio = request.files["audio"]
            else:
                audio = None
            is_error, error_msg = check_for_err(transcript, audio, use_audio)
            if is_error:
                return abort(400, description=error_msg)

            # creating tmp directory
            tmp_name = create_tmp()
            tmp_dir, images_dir, textpath, audiopath = get_tmp_paths(tmp_name)

            # saving files to tmp directory
            transcript.save(textpath)
            if use_audio:
                audio.save(audiopath)

            if use_images:
                word = ""
                is_image = False
                words = []
                num_images = 0
                with open(textpath, "r") as f:
                    for line in f:
                        for char in line:
                            if is_image:
                                word += char
                                if char == "]":
                                    # if image word just ended
                                    words.append([word, True])
                                    num_images += 1
                                    word = ""
                                    is_image = False
                            elif char == "[":
                                is_image = True
                                if word != "":
                                    words.append([word, False])
                                word = char
                            else:
                                if char == " ":
                                    if word != "":
                                        words.append([word, False])
                                        word = ""
                                else:
                                    word += char
                if word != "":
                    words.append([word, False])
                # checking if there's a hanging bracket
                if is_image:
                    return abort(
                        400, description="No closing bracket for image in transcript"
                    )
                return {"tmp_name": tmp_name, "words": words, "num_images": num_images}
            else:
                try:
                    video_name = create_video(
                        images_dir,
                        tmp_dir,
                        use_audio,
                        audiopath,
                        textpath,
                        usage_rights,
                    )
                except Exception as exc:
                    return abort(500, description=str(exc))
                return video_name


@app.route("/create-video", methods=["POST"])
def create():
    """Creates a video. Used after user uploads their own images."""
    if request.method == "POST":
        if request.files:
            POST = request.form
            use_audio = POST.get("use_audio") == "true"
            tmp_name = POST.get("tmp_name")
            tmp_dir, images_dir, textpath, audiopath = get_tmp_paths(tmp_name)
            try:
                video_name = create_video(
                    images_dir,
                    tmp_dir,
                    use_audio,
                    audiopath,
                    textpath,
                    "any",
                    True,
                    request.files,
                )
            except Exception as exc:
                return abort(500, description=str(exc))
            return video_name


@app.route("/show-video")
def show():
    """Displays video. Video to display is based on query string"""
    video_name = request.args.get("video_name")
    # if query string is invalid
    vid_location = os.path.join("app", "static", "videos", video_name + ".mp4")
    if video_name is None or not os.path.isfile(vid_location):
        abort(404)
    return render_template("show-video.html", video_name=video_name)


@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400
