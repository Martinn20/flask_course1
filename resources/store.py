from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.store import StoreModel


class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True)

    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"Message": "Item not found"}, 404

    def post(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {"Message": "Item with this name alredy exists!"}, 400

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": "Error inserting store to db!"}, 500
        return store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        return {'item': store}, 204


class StoreList(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.query.all()]}
