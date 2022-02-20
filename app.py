import os, logging, click
from venv import create

from flask import Flask, current_app
from flask.cli import FlaskGroup
from flask_restful import Api
from flask_cors import CORS


def create_app():
    logging.getLogger("flask_cors").level = logging.DEBUG
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PW')}@{os.environ.get('DATABASE_URL')}/{os.environ.get('DATABASE_NAME')}"
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
    
