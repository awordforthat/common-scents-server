from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


# set up M2M tables
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


class Category(db.Model):
    """Represents a label that can be applied to a group of scents across any number of houses."""

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<Category {self.name}>"

    def __str__(self):
        return self.name


class Note(db.Model):
    """Represents a scent note. Can be labeled with sub-classifications."""

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    # subcategories

    def __repr__(self):
        return f"<Note {self.name}>"


class Tag(db.Model):
    """Represents a subjective quality that can be associated with a scent."""

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"


class Scent(db.Model):
    """Represents a single scent in a House's lineup."""

    __table_args__ = (
        db.UniqueConstraint("slug", "house_id", name="unique_scent_house"),
    )
    id = Column(Integer, primary_key=True)
    slug = Column(String(80), nullable=False)
    name = Column(String(80))
    categories = relationship(
        "Category", secondary=scents_to_categories, backref="scents", lazy="select"
    )
    notes = relationship(
        "Note", secondary=scents_to_notes, backref="notes", lazy="select"
    )
    tags = relationship("Tag", secondary=scents_to_tags, backref="tags", lazy="select")
    discontinued = Column(Boolean, default=False)
    house_id = Column(Integer, ForeignKey("house.id"))
    # collection
    # formats

    def __repr__(self):
        return f"<Scent {self.name}>: {' ,'.join([str(category) for category  in self.categories])}"


class House(db.Model):
    """Represents a perfume house, or a producer of scents."""

    id = Column(Integer, primary_key=True)
    slug = Column(String(80), unique=True, nullable=False)  # name, slugified
    name = Column(String(80))  # human readable name
    link = Column(String(255), unique=True)
    scents = relationship(
        "Scent", backref="house", lazy="select", cascade="all, delete"
    )
    # abbreviations
    # collections

    def __repr__(self):
        return f"<House {self.name}>"


class HouseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = House


class ScentSchema(SQLAlchemyAutoSchema):
    house = fields.Nested(HouseSchema)

    class Meta:
        model = Scent
