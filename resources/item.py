from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.item import ItemModel
from flask_jwt_extended import get_jwt
from flask import request
from marshmallow import ValidationError
from schemas.item import ItemSchema

item_schema = ItemSchema()
list_item_schema = ItemSchema(many=True)
class Item(Resource):

    @classmethod
    @jwt_required()
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item)
        return {"Message": "Item not found"}, 404

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        identity = get_jwt()
        if not identity["is_admin"]:
            return {"message": "Admin privilege required!"}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'item': "item deleted!"}, 204
        return {"Message": "Item not found"}, 404

    @classmethod
    def put(cls, name: str):
        item = ItemModel.find_by_name(name)
        item_json = request.get_json()
        if item is None:
            item_json["name"] = name
            try:
                item = item_schema.load(item_json)
            except ValidationError as err:
                return err.messages, 400
        else:
            item.price = item_json['price']

        item.save_to_db()
        return item.json(), 201

    @classmethod
    @jwt_required(fresh=True)
    def post(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return {'message': f'Item with name {name} already exists!'}, 400

        item_json = request.get_json()
        item_json["name"] = name
        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400
        try:
            item.save_to_db()
        except :
            {"message": "An error occured inserting the item"}, 500
        return item_schema.dump(item), 201


class ItemList(Resource):

    @classmethod
    @jwt_required(optional=True)
    def get(cls):
        user_id = get_jwt_identity()
        items = [item_schema.dump(item) for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {
            "items": [item["name"] for item in items],
            "message": "More data available when logged in."
        }, 200
