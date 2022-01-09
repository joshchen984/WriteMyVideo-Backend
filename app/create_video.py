import argparse
from gtts import gTTS
import os
import shutil
from google_images_download import google_images_download
import requests
from random import choice
import subprocess
from PIL import Image
import concurrent.futures
from werkzeug.utils import secure_filename


class ImageCreator:
    """
    Class used to create frames file. Also used to download images.
    """

    def __init__(self, images_dir, usage_rights, use_images=False, images=None):
        self.images_dir = images_dir
        self.usage_rights = usage_rights
        self.use_images = use_images
        if use_images:
            self.images = images

    def download_images(self, image_words: list):
        """Downloads images from google images

        Args:
            image_words: List of images to downloaded
        """
        if not self.use_images:
            response = google_images_download.googleimagesdownload()
            results = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i, search in enumerate(image_words):
                    # making image directory i because there can be multiple searches that have the same name
                    arguments = {"keywords": search, "limit": 5, "print_urls": False, "output_directory": self.images_dir,
                                 "image_directory": str(i), 'format': 'jpg', "chromedriver": "chromedriver.exe",
                                 'silent_mode': True}  # creating list of arguments

                    if self.usage_rights != "any":
                        arguments['usage_rights'] = self.usage_rights
                    # creating thread for image download
                    results.append(executor.submit(
                        response.download, arguments))
        else:
            num_images = len(image_words)
            for i in range(0, num_images):
                image_dir = os.path.join(self.images_dir, str(i))
                os.mkdir(image_dir)
                self.images[str(i)].save(os.path.join(
                    image_dir, secure_filename(self.images[str(i)].filename)))

    @classmethod
    def get_random_image(cls, image_dir):
        """Gets a random image from a directory

        Args:
            image_dir: Path to directory with images

        Returns:
            string: Path to chosen image
        """
        return os.path.join(image_dir, choice(os.listdir(image_dir)))

    @classmethod
    def convert_img(cls, image_path, new_ext='.jpg'):
        """Changes image to have another file extension

        Args:
            image_path: Path to image to change
            new_ext: New file extension for image. e.g: .jpg

        Returns:
            string: Path to changed image
        """
        pre, ext = os.path.splitext(image_path)
        im = Image.open(image_path)
        rgb_im = im.convert('RGB')
        os.remove(image_path)
        rgb_im.save(pre + new_ext)
        return pre + new_ext

    @classmethod
    def resize_img(cls, image_path, newsize=(1920, 1080)):
        """Resizes Image

        Args:
            image_path: Path to image to change
            newsize (tuple): Size to reshape image to
        """
        im = Image.open(image_path)
        im = im.resize(newsize)
        im.save(image_path)

    @classmethod
    def process_img(cls, image_path, newsize=(1920, 1080), new_ext='.jpg'):
        """Resizes and converts image to specified file extension

        Args:
            image_path: Path to image to change
            newsize (tuple): Size to reshape image to
            new_ext: New file extension for image. e.g: .jpg

        Returns:
            string: Path to changed image
        """
        newpath = cls.convert_img(image_path, new_ext)
        cls.resize_img(newpath, newsize)
        return newpath

    def write_frames(self, words, prev_words, tmp_dir, image_words):
        """Writes image paths and duration for how long images should appear for to a text file

        Args:
            words: Words with timestamps from gentle response
            prev_words: Indexes of the words before the image_words
            tmp_dir: Directory to save file
            image_words: Image search terms. Only used for error message
        """
        idx = 0
        prev_timestamp = 0
        timestamp = 0
        # writing frame timings to txt file
        with open(os.path.join(tmp_dir, "frames.txt"), 'w') as f:
            for i, word in enumerate(words):
                try:
                    timestamp = word['end']
                except Exception as inst:
                    print(type(inst))
                    print(inst)

                if idx + 1 < len(prev_words):
                    if i == prev_words[idx + 1]:
                        # choosing random image from the 5 images of search
                        try:
                            img = self.get_random_image(
                                os.path.join(self.images_dir, str(idx)))
                        except IndexError:
                            # if the downloader didn't download any images for certain image
                            raise ValueError(
                                f"No images downloaded for '{image_words[idx]}'")

                        newpath = self.process_img(img)
                        f.write(f"file '{newpath}'\n")
                        f.write(f"duration {timestamp - prev_timestamp}\n")
                        prev_timestamp = timestamp
                        idx += 1
                else:
                    # when program reaches last image word
                    break

            # writing last entry to txt file
            timestamp = words[-1]['end']
            try:
                img = self.get_random_image(
                    os.path.join(self.images_dir, str(idx)))
            except IndexError:
                # if the downloader didn't download any images for certain image
                raise ValueError(
                    f"No images downloaded for '{image_words[idx]}'")

            newpath = self.process_img(img)
            f.write(f"file '{newpath}'\n")
            f.write(f"duration {timestamp - prev_timestamp}\n")
            # Due to a quirk, the last image has to be specified twice - the 2nd time without any duration directive
            f.write(f"file '{newpath}'")


class VideoCreator:
    def __init__(self, images_dir, tmp_dir, use_audio, audiopath, txtpath, usage_rights, output_file, use_images=False, images=None):
        self.img_creator = ImageCreator(
            images_dir, usage_rights, use_images, images)
        self.tmp_dir = tmp_dir
        self.images_dir = images_dir
        self.use_audio = use_audio
        self.audiopath = audiopath
        self.txtpath = txtpath
        self.output_file = output_file

    def create_video(self):
        """Creates full video. Only function needed to call to create video

        """
        # the image search terms and the text without the image search terms
        image_words, prev_words, text = self.parse_transcript(self.txtpath)
        parsed_txt_path = os.path.join(self.tmp_dir, "parsed.txt")
        with open(parsed_txt_path, 'w', encoding='utf8') as f:
            f.write(text)

        if not self.use_audio:
            self.audiopath = os.path.join(self.tmp_dir, "audio.mp3")
            self.create_audio(text)

        self.img_creator.download_images(image_words)

        words = self.get_gentle_response(parsed_txt_path)

        self.img_creator.write_frames(
            words, prev_words, self.tmp_dir, image_words)

        # bring images together
        command = f"ffmpeg -safe 0 -y -f concat -i {os.path.join(self.tmp_dir, 'frames.txt')} {os.path.join(self.tmp_dir, 'video.mp4')}"
        subprocess.run(command, shell=True)
        # add audio
        command = f"ffmpeg -i {os.path.join(self.tmp_dir, 'video.mp4')} -i {self.audiopath} -c:v copy -c:a aac -y {self.output_file}"
        subprocess.run(command, shell=True)

    def create_audio(self, text):
        tts = gTTS(text)
        tts.save(self.audiopath)

    @classmethod
    def parse_transcript(cls, transcript_path: str):
        """Separates image words and spoken words
        Args:
            transcript_path: Path to transcript
        Returns:
            image_words: the image search terms
            prev_words: the indexes of the words that come before the image_words.
                        If it's the first image then the index is -1
            parsed_text: The transcript without the image words
        """

        def get_last_word(text):
            """text = "hello there person" --> 2
            Args:
                text (str): text to parse

            Returns:
                int: the index of last word
            """
            words = text.split()
            # returning index of last word
            return len(words) - 1

        # the image search terms
        image_words = []
        prev_words = []
        image_word = ""
        is_image = False
        # The text without the image search terms
        parsed_text = ""
        # adding to text and image_words
        with open(transcript_path, 'r') as f:
            for line in f:
                for char in line:
                    if is_image:
                        if char == ']':
                            # if image word just ended
                            prev_word = get_last_word(parsed_text)
                            prev_words.append(prev_word)
                            image_words.append(image_word)
                            image_word = ""
                            is_image = False
                        else:
                            image_word += char
                    elif char == '[':
                        is_image = True
                    else:
                        parsed_text += char
        # checking if there's a hanging bracket
        if is_image:
            msg = "No closing bracket for image in transcript"
            raise ValueError(msg)

        return image_words, prev_words, parsed_text

    def get_gentle_response(self, parsed_txt_path):
        """Returns response from gentle

        Args:
            parsed_txt_path (str): parsed txt path

        Returns:
            list: aligned words
        """
        files = {"transcript": open(
            parsed_txt_path, 'rb'), 'audio': open(self.audiopath, 'rb')}
        r = requests.post(
            "http://gentle:8765/transcriptions?async=false", files=files)
        gentle_json = r.json()
        words = gentle_json['words']
        return words
