from flask import Flask
from flask_cors import CORS
import os
from redis import Redis
import rq
import logging


def create_app():
    """Creates configured app"""
    app = Flask(__name__)
    CORS(
        app,
        supports_credentials=True,
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.redis = Redis(host='redis-host', port=6379)
    app.task_queue = rq.Queue("video-tasks", connection=app.redis)
    app.logger.setLevel(logging.DEBUG)
    return app


app = create_app()
from app import views
