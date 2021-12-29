from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.store import StoreModel
from ma import ma
from schemas.store import StoreSchema
store_schema = StoreSchema()

class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True)

    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200
        return {"Message": "Item not found"}, 404

    @classmethod
    def post(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return {"Message": "Item with this name alredy exists!"}, 400

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": "Error inserting store to db!"}, 500
        return store_schema.dump(), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        return {'item': store}, 204


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {'stores': [store_schema.dump(store) for store in StoreModel.find_all()]}
