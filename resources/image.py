from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import os
from libs import image_helper
from schemas.image import ImageSchema

image_schema = ImageSchema()

class ImageUpload(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"message": f"Image uploaded {basename}"}, 201
        except UploadNotAllowed:
            extention = image_helper.get_extension(data["image"])
            return {"message": f"Image extention not allowed {data['image']}"}, 400

class Image(Resource):
    @classmethod
    @jwt_required()
    def get(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "Ilegal file name"}, 400
        try:
            return send_file(image_helper.get_path(folder, filename))
        except FileNotFoundError:
            return {"message": f"File with filename {filename} is not found"}, 404

    @classmethod
    @jwt_required()
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "Ilegal file name"}, 400
        try:
            os.remove(image_helper.get_path(folder, filename))
            return {"message": f"Image {filename} removed successfuly"}
        except FileNotFoundError:
            return {"message": f"File with filename {filename} is not found"}, 404
        except:
            traceback.print_exc()
            return {"message": "Image remove failed"}, 500


class AvatarUpload(Resource):
    @classmethod
    @jwt_required()
    def put(cls):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        filename = f"user_{user_id}"
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": "Avatar remove failed"}, 500
        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(data["image"], folder=folder, name=avatar)
            basename = image_helper.get_basename(avatar_path)
            return {"message": f"Avatar {avatar} uploaded!"}
        except:
            extension = image_helper.get_extension(data["image"])
            return {"message": f"This extention {extension} is not allowed"}


class Avatar(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id: int, ):
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {"message": "Avatar not found"}, 404