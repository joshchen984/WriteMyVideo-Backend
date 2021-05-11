pip install -r requirements.txt
docker run -p 8765:8765 --name gentle lowerquality/gentle
docker stop gentle