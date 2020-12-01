from flask import Flask, render_template, url_for, request, redirect, flash
from create_video import VideoCreator
import os
import shutil
import subprocess
import yaml
import oschmod
import hashlib
app = Flask(__name__)

with open("config.yaml") as f:
    config = yaml.safe_load(f)

app.config['SECRET_KEY'] = config['SECRET_KEY']

@app.route("/", methods = ["GET", "POST"])
def index():
    if(request.method == "POST"):
        userDetails = request.form
        return 'successful'

    return render_template("index.html")

@app.route('/create-video', methods = ["POST"])
def create():
    if request.method == 'POST':
        if request.files:
            POST = request.form
            use_audio = POST.get('use_audio')
            usage_rights = POST.get("usage_rights")
            transcript = request.files['transcript']
            audio = request.files['audio']

            #allowed file extensions
            TRANSCRIPT_EXT = [".txt"]
            AUDIO_EXT = [".mp3"]

            if transcript.filename == '':
                #checking if transcript has been uploaded
                flash("Missing Transcript", 'warning')
                return redirect(url_for("index"))
            pre, ext = os.path.splitext(transcript.filename)
            if ext not in TRANSCRIPT_EXT:
                #checking if transcript has right file extension
                flash(f"Transcript cannot have a {ext} file extension", 'warning')
                return redirect(url_for("index"))
            if use_audio:
                if audio.filename == '':
                    #checking if audio has been uploaded
                    flash("Missing Audio File", 'warning')
                    return redirect(url_for("index"))
                pre, ext = os.path.splitext(audio.filename)
                if ext not in AUDIO_EXT:
                    #checking if audio has right file extension
                    flash(f"Audio cannot have a {ext} file extension", 'warning')
                    return redirect(url_for("index"))

            #deleting tmp directory then creating new tmp directory
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            images_dir = os.path.join(tmp_dir,"images")
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors = True)
            #sometimes there's a permission denied error so we use chmod
            oschmod.set_mode(os.getcwd(), 700)
            os.makedirs(images_dir, exist_ok = True)

            textpath = os.path.join(tmp_dir, 'text.txt')
            transcript.save(textpath)

            audiopath = os.path.join(tmp_dir, "audio.mp3")
            if use_audio:
                audio.save(audiopath)

            creator = VideoCreator(images_dir, tmp_dir, use_audio, audiopath, textpath, usage_rights, "static/videos/full_video.mp4")
            creator.create_video()

            #create webm file
            # pre, ext = os.path.splitext(videopath)
            # webm_video = pre + ".webm"
            # command = f"ffmpeg -i {videopath} {webm_video}"
            # subprocess.run(command, shell = True, env = {'PATH':ffmpeg_path})
            return redirect(url_for('show'))

@app.route("/show-video")
def show():
    return render_template("show-video.html")

if(__name__ == "__main__"):
    app.run(debug = True)
