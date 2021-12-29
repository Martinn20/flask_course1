import sqlite3
import traceback

from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from models.user import UserModel
from blacklist import BLACKLIST
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from schemas.user import UserSchema
from marshmallow import ValidationError
from flask import make_response, render_template
from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel

user_schema = UserSchema()
class UserRegister(Resource):

    def post(self):
        try:
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username) or UserModel.find_by_email(user.email):
            return {"message": "User already exists!"}, 400

        try:
            user.save_to_db()
            confirmation_model = ConfirmationModel(user.id)
            confirmation_model.save_to_db()
            user.send_confirmation_email()
            return {"message": "Confirmation email sent"}, 201
        except MailgunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            user.delete_from_db()
            traceback.print_exc()
            return {"message": "Failed to create user"}, 500

class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User with id {user_id} it is not found!"}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User with id {user_id} it is not found!"}, 404
        user.delete_from_db()
        return {"Message": "User deleted!"}, 204


class UserLogin(Resource):

    @classmethod
    def post(cls):
        try:
            data = user_schema.load(request.get_json(), partial=("email",))
        except ValidationError as err:
            return err.messages, 400
        user = UserModel.find_by_username(data.username)

        if user and safe_str_cmp(user.password, data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200
            else:
                return {"message": "Email is not confirmed, please check your email! "+ user.username}, 400
        return {"message": "Invalid credentials"}, 401

class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User with id {user_id} it is not found!"}, 404
        user.activated = True
        user.save_to_db()
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("conformation_page.html", email=user.username), 200, headers)