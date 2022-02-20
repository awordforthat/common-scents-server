import pandas as pd
from flask import request
from flask_restful import Resource, fields
from slugify import slugify

from models import Scent, ScentSchema, House, db

resource_fields = {"id": fields.Integer, "name": fields.String}
ALLOWED_UPLOAD_EXTENSIONS = ["csv"]
HEADER_SPACE = (
    10  # number of rows to check before we discard the file as having no header
)

COLUMN_SYNONYMS = {
    "house": ("house", "houses", "brand", "brands", "house name", "company"),
    "scent": ("scent", "scents", "scent name", "name", "names"),
    "description": ("description", "descriptions", "notes", "scent notes"),
    "size": ("size", "sizes"),
    "format": ("format", "type"),
}


def get_related_by_id(obj, property_name, id):
    relation = getattr(obj.__class__, property_name)  # in example: User.addresses
    related_class = relation.property.argument  # in example: Address
    return db.session.query(related_class).filter(relation.any(id=id)).first()


def error(message, code=None):
    return {"error": message}, code or 400


def file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def allowed_file(filename):
    return "." in filename and file_extension(filename) in ALLOWED_UPLOAD_EXTENSIONS


class ModelView(Resource):
    def __init__(self, model, schema):
        self.model = model
        self.schema = schema
        self.query = self.model.query.get_or_404

    def get(self, *args, **kwargs):
        return self.schema.dump(self.query(*args, **kwargs))


class ModelListView(ModelView):
    def __init__(self, *args, **kwargs):
        super(ModelListView, self).__init__(*args, **kwargs)
        self.query = self.model.query.all


class ScentView(ModelView):
    def __init__(self):
        super(ScentView, self).__init__(Scent, ScentSchema())


class ScentList(ModelListView):
    def __init__(self):
        super(ScentList, self).__init__(Scent, ScentSchema(many=True))


class BatchUploadView(Resource):
    def post(self, *args, **kwargs):
        db.drop_all()
        db.create_all()
        spreadsheet = request.files.get("file")
        if not spreadsheet:
            return error("No spreadsheet attached!")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if spreadsheet.filename == "":
            return error("Empty file uploaded!")
        if spreadsheet and allowed_file(spreadsheet.filename):
            filestream = spreadsheet.stream
            filestream.seek(0)
            # first, try and find the header row
            has_house = False
            has_scent = False
            header_index = None
            for i in range(HEADER_SPACE):
                line = filestream.readline().decode("utf-8").split(",")
                for cell in line:
                    if str.lower(str(cell)) in COLUMN_SYNONYMS["house"]:
                        has_house = True
                    if str.lower(str(cell)) in COLUMN_SYNONYMS["scent"]:
                        has_scent = True
                if has_house and has_scent:
                    header_index = i
                    break

            if header_index is None:
                return error(
                    f"Did not find a header row in the first {HEADER_SPACE} rows. Make sure your spreadsheet \
                has a header row that contains one of {COLUMN_SYNONYMS['house']} and one of {COLUMN_SYNONYMS['scent']}."
                )
            filestream.seek(0)
            # next, import the data frame, starting from the header
            df = pd.DataFrame(
                pd.read_csv(
                    filestream, skiprows=None if header_index == 0 else header_index
                )
            ).dropna(how="all")
            # standardize column names
            for column_name in df.columns.values:
                for key, values in COLUMN_SYNONYMS.items():
                    if str.lower(column_name) in values:
                        df.rename(columns={column_name: key}, inplace=True)

            # drop columns that aren't relevant
            df = df[
                list(set(COLUMN_SYNONYMS.keys()).intersection(set(df.columns.values)))
            ]

            # iterate over the rows, creating records as necessary (see docstring)
            # TODO: incorporate house synonyms
            house_name = None
            log = []
            for index, row in df.iterrows():
                row_house = df["house"][index]
                if pd.isnull(row_house):
                    row["house"] = house_name
                house_name = house_name if pd.isnull(row_house) else row_house
                house = House.query.filter_by(slug=slugify(house_name)).first()
                if not house:
                    house = House(slug=slugify(row["house"]), name=row["house"])
                    db.session.add(house)
                    log.append(
                        (f"Added house {house_name} with slug {slugify(house_name)}")
                    )

                scent_name = df["scent"][index]
                scent_slug = slugify(scent_name)
                scent = Scent.query.filter_by(slug=scent_slug).first()
                if not scent:
                    db.session.add(Scent(house=house, name=df["scent"][index], slug=scent_slug,
                        description=df["description"][index] if "description" in df.columns else None))
                    log.append(
                        (f"Added scent {scent_name} to house {house_name}")
                    )
            db.session.commit()
            return log
           
        else:
            return error(
                f"File upload type '{file_extension(spreadsheet.filename)}' not allowed. Please only upload '{', '.join(ALLOWED_UPLOAD_EXTENSIONS)}' files"
            )


def setup_routes(api):
    api.add_resource(ScentView, "/scents/<id>")
    api.add_resource(ScentList, "/scents")
    api.add_resource(BatchUploadView, "/upload")
