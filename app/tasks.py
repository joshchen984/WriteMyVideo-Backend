from app import create_app
from app.create_video import VideoCreator
import sys
import shutil


app = create_app()
app.app_context().push()


def create_video_user_images(
    video_name, images_dir, tmp_dir, use_audio, audiopath, textpath
):
    """Creates a video."""
    app.logger.info("Started create_video_user_images task")
    try:
        creator = VideoCreator(
            images_dir=images_dir,
            tmp_dir=tmp_dir,
            use_audio=use_audio,
            audiopath=audiopath,
            txtpath=textpath,
            usage_rights="any",
            output_file=f"app/static/videos/{video_name}.mp4",
            use_images=True,
        )
        creator.create_video()
        return video_name
    except:
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())
    finally:
        # deleting tmp directory after image has been created
        shutil.rmtree(tmp_dir)
