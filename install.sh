pip install -r requirements.txt
docker run -p 8765:8765 --name gentle lowerquality/gentle
docker stop gentle
python -m pip install git+https://github.com/Joeclinton1/google-images-download.git