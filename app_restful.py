from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, Avatar, AvatarUpload
from libs.image_helper import IMAGE_SET
import os
from blacklist import BLACKLIST
from ma import ma
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(app, 10 * 1024 * 1024)
configure_uploads(app, IMAGE_SET)
api = Api(app)

# jwt = JWT(app, authenticate, identity)
jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_headers, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"message": "The token has expired"}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"message": f"The token is invalid, Error: {error}"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"message": f"Request does not contain access token, Error: {error}"}, 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return {"message": f"The token is not fresh."}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"message": f"The token has been revoked"}, 401


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")




if __name__ == '__main__':
    from db import db
    db.init_app(app)
    ma.init_app(app)
    app.run(debug=True)
