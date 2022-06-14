from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
from app import views
