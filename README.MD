# Text2Video
## (Installation Instructions are Confusing. Working on Putting this on the Internet)
<hr>
Text2Video's purpose is to help people create videos quickly and easily by simply typing out the video’s script and a description of images to include in the video.

![](images/demo.gif)

## Usage
Just upload a script and an optional audio file of you saying the script<br>
To start the server run this in the terminal
~~~
docker start gentle
python app.py
~~~
To stop the server open the same terminal and press CTRL-C. After that run
~~~
docker stop gentle
~~~

For instructions on how to use Text2Video check out this [tutorial](https://www.youtube.com/watch?v=o5VlCaXgN6w).

## Installation
This has only been tested on Windows 10.
~~~
git clone https://github.com/joshchen984/Text2Video.git
cd Text2Video
./install.sh
~~~
Must install [ffmpeg](https://www.ffmpeg.org/download.html#build-windows) and add it to PATH

## Requirements
Python 3.6 or up

Docker
[How to install](https://www.youtube.com/watch?v=5nX8U8Fz5S0)

## Acknowledgments
This was inspired by Carykh's [Youtube Video Creator](https://www.youtube.com/watch?v=Jr9sptoLvJU&t=64s).
