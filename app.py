import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PW')}@{os.environ.get('DATABASE_URL')}/{os.environ.get('DATABASE_NAME')}"
db = SQLAlchemy(app)

print(app.config["SQLALCHEMY_DATABASE_URI"])


class House(db.Model):
    id = Column(Integer, primary_key=True)
    name = db.Column(String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<House {self.name}>"


class Scent(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<Scent {self.name}>"


@app.route("/")
def hello_world():
    """Says hello"""

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=os.environ.get("DEBUG"))
