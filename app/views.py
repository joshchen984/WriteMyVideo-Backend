from flask import request, abort, jsonify
from werkzeug.datastructures import FileStorage
from app import app
from app.utils import (
    check_for_err,
    create_tmp,
    create_video,
    get_tmp_paths,
    get_video_name,
    run_task,
)
from app.tasks import create_video_user_images, create_video_no_images
from app.create_video import VideoCreator
import traceback


@app.route("/", methods=["GET"])
def index():
    return "hi"


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
                # Create video by downloading Google images
                try:
                    video_name = get_video_name()
                    video_creator = VideoCreator(
                        images_dir=images_dir,
                        tmp_dir=tmp_dir,
                        use_audio=use_audio,
                        audiopath=audiopath,
                        txtpath=textpath,
                        usage_rights=usage_rights,
                        output_file=f"app/static/videos/{video_name}.mp4",
                    )
                    video_creator.create_setup_files()
                    run_task(
                        create_video_no_images,
                        video_name=video_name,
                        images_dir=images_dir,
                        tmp_dir=tmp_dir,
                        use_audio=use_audio,
                        audiopath=audiopath,
                        textpath=textpath,
                        usage_rights=usage_rights,
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
                video_name = get_video_name()
                video_creator = VideoCreator(
                    images_dir=images_dir,
                    tmp_dir=tmp_dir,
                    use_audio=use_audio,
                    audiopath=audiopath,
                    txtpath=textpath,
                    usage_rights="any",
                    output_file=f"app/static/videos/{video_name}.mp4",
                    use_images=True,
                    images=request.files,
                )
                video_creator.create_setup_files()
                run_task(
                    create_video_user_images,
                    video_name=video_name,
                    images_dir=images_dir,
                    tmp_dir=tmp_dir,
                    use_audio=use_audio,
                    audiopath=audiopath,
                    textpath=textpath,
                )
            except Exception as exc:
                app.logger.error(traceback.format_exc())
                return abort(500, description=str(exc))
            return video_name
    return abort(400)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400
