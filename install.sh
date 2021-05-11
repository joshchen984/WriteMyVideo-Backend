pip install -r requirements.txt
docker run -p 8765:8765 --name gentle lowerquality/gentle
docker stop gentle
mkdir logs
touch logs/app.log
echo "SECRET_KEY: SOME_KEY" > config.yaml
mkdir static/videos