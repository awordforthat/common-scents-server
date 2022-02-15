import functools
from flask import abort
from flask_restful import Resource, fields
from flask_cors import cross_origin

from models import Scent, ScentSchema
from flask_restful import Api

resource_fields = {"id": fields.Integer, "name": fields.String}


def get_or_404(model, id):
    instance = model.query.get(id)
    if instance:
        return instance
    abort(404, f"{model.__name__} instance with id {id} was not found")


class ModelView(Resource):
    def __init__(self, model, schema):
        self.model = model
        self.schema = schema
        self.query = functools.partial(get_or_404, self.model)

    @cross_origin
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


def setup_routes(api):
    api.add_resource(ScentView, "/scents/<id>")
    api.add_resource(ScentList, "/scents")
