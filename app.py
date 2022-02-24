import os, logging, click
from venv import create

from flask import Flask, current_app
from flask.cli import FlaskGroup
from flask_restful import Api
from flask_cors import CORS


def create_app():
    logging.getLogger("flask_cors").level = logging.DEBUG
    app = Flask(__name__)
    development = os.environ.get("FLASK_ENV") != "production"
    db_user = os.environ.get(f"{'DEV_' if development else ''}DATABASE_USER")
    db_pw = os.environ.get(f"{'DEV_' if development else ''}DATABASE_PW")
    db_url = os.environ.get(f"{'DEV_' if development else ''}DATABASE_URL")
    print(db_url)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql://{db_user}:{db_pw}@{db_url}/{os.environ.get('DATABASE_NAME')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CORS_HEADERS"] = "Content-Type"
    app.config["CORS_ORIGINS"] = "*"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000

    from models import db
    db.init_app(app)
    api = Api(app)
    CORS(app)

    from views import setup_routes
    setup_routes(api)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.environ.get("DEBUG"))
    
