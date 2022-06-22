from app import app


if __name__ == "__main__":
    # Only for debugging while developing
    app.logger.info("Running in debug mode")
    app.run(host="0.0.0.0", debug=True, port=80)
