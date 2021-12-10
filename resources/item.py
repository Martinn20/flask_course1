from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("price", type=float, required=True)
    parser.add_argument("name", type=str, required=True)
    parser.add_argument("store_id", type=int, required=True)


    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"Message": "Item not found"}, 404

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'item': "item deleted!"}, 204
        return {"Message": "Item not found"}, 404

    def put(self, name):
        item = ItemModel.find_by_name(name)
        data = Item.parser.parse_args()

        if item is None:
                item = ItemModel(**data)
        else:
            item.price = data['price']

        item.save_to_db()
        return item.json(), 201


class ItemList(Resource):

    @jwt_required()
    def get(self):
        return {'items': [item.json() for item in ItemModel.query.all()]} # moze i so lambda

    def post(self):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(data['name'])
        if item:
            return {'message': f'Item with name {data["name"]} already exists!'}, 400

        item = ItemModel(data['name'], data['price'], data["store_id"])
        try:
            item.save_to_db()
        except:
            {"message": "An error occured inserting the item"}, 500
        return item.json(), 201