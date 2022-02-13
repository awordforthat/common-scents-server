import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize
from flask_cors import CORS
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PW')}@{os.environ.get('DATABASE_URL')}/{os.environ.get('DATABASE_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
CORS(app)
fs_mixin = FlaskSerialize(db)

scents_to_categories = Table(
    "scents_categories",
    db.metadata,
    Column("scent_id", Integer, ForeignKey("scent.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True),
)

scents_to_notes = Table(
    "scents_notes",
    db.metadata,
    Column("scent_id", Integer, ForeignKey("scent.id"), primary_key=True),
    Column("note_id", Integer, ForeignKey("note.id"), primary_key=True),
)

scents_to_tags = Table(
    "scents_tags",
    db.metadata,
    Column("scent_id", Integer, ForeignKey("scent.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class House(db.Model, fs_mixin):
    """Represents a perfume house, or a producer of scents."""

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    scents = relationship("Scent", backref="house", lazy="select")
    link = Column(String(255), unique=True)
    # abbreviations
    # collections

    # serializer fields
    __fs_create_fields__ = __fs_update_fields__ = ["id", "name"]

    def __repr__(self):
        return f"<House {self.name}>"


class Scent(db.Model, fs_mixin):
    """Represents a single scent in a House's lineup."""

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    house_id = Column(Integer, ForeignKey("house.id"))
    categories = relationship(
        "Category", secondary=scents_to_categories, backref="scents", lazy="select"
    )
    notes = relationship(
        "Note", secondary=scents_to_notes, backref="notes", lazy="select"
    )
    tags = relationship("Tag", secondary=scents_to_tags, backref="tags", lazy="select")
    discontinued = Column(Boolean, default=False)

    # serializer fields
    __fs_create_fields__ = __fs_update_fields__ = [
        "id",
        "name",
        "house_id",
        "categories",
        "notes",
    ]

    # collection
    # formats

    def __repr__(self):
        return f"<Scent {self.name}>: {' ,'.join([str(category) for category  in self.categories])}"


class Category(db.Model):
    """Represents a label that can be applied to a group of scents across any number of houses."""

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    # serializer fields
    __fs_create_fields__ = __fs_update_fields__ = ["id", "name"]

    def __repr__(self):
        return f"<Category {self.name}>"

    def __str__(self):
        return self.name


class Note(db.Model):
    """Represents a scent note. Can be labeled with sub-classifications."""

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    # subcategories

    # serializer fields
    __fs_create_fields__ = __fs_update_fields__ = ["id", "name"]

    def __repr__(self):
        return f"<Note {self.name}>"


class Tag(db.Model):
    """Represents a subjective quality that can be associated with a scent."""

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)

    # serializer fields
    __fs_create_fields__ = __fs_update_fields__ = ["id", "name"]

    def __repr__(self):
        return f"<Tag {self.name}>"


@app.cli.command("initdb")
def initdb():
    db.drop_all()
    db.create_all()
    print("Initialized db")


@app.cli.command("bootstrap")
def bootstrap():
    db.drop_all()
    db.create_all()

    aquatic = Category(name="aquatic")
    citrus = Category(name="citrus")
    woody = Category(name="woody")

    seaweed = Note(name="seaweed")
    leaves = Note(name="leaves")

    alkemia = House(name="Alkemia")
    enigma = Scent(name="Acadia", house=alkemia, categories=[aquatic], notes=[seaweed])

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

    print(Scent.query.all())


@app.route("/")
def hello_world():
    """Says hello"""

    return render_template("index.html")


@app.route("/scents/", methods=["GET"])
def getScents():
    return Scent.fs_get_delete_put_post()


if __name__ == "__main__":
    app.run(debug=os.environ.get("DEBUG"))
