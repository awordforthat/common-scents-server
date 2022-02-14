import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PW')}@{os.environ.get('DATABASE_URL')}/{os.environ.get('DATABASE_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()
ma = Marshmallow(app)
CORS(app)

# import these so that everything is initialized
from server.models import Scent, Category, House, Tag, Note
import server.routes

# now initialize the database and create the app context
db.init_app(app)
app.app_context().push()


@app.cli.command("initdb")
def initdb():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Initialized db")


@app.cli.command("bootstrap")
def bootstrap():
    with app.app_context():
        db.drop_all()
        db.create_all()

        aquatic = Category(name="aquatic")
        citrus = Category(name="citrus")
        woody = Category(name="woody")

        seaweed = Note(name="seaweed")
        leaves = Note(name="leaves")

        alkemia = House(name="Alkemia")
        enigma = Scent(
            name="Acadia", house=alkemia, categories=[aquatic], notes=[seaweed]
        )

        solstice = House(name="Solstice Scents")
        foxcroft = Scent(
            name="Foxcroft", house=solstice, categories=[woody], notes=[leaves]
        )

        db.session.add(alkemia)
        db.session.add(enigma)
        db.session.add(solstice)
        db.session.add(foxcroft)
        db.session.add(aquatic)
        db.session.add(citrus)
        db.session.add(woody)
        db.session.add(seaweed)
        db.session.add(leaves)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=os.environ.get("DEBUG"))
