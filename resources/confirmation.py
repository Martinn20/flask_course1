import traceback

from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from time import time
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"Message": f"Confirmation with id {confirmation_id} is not found!"}, 404
        if confirmation.expired:
            return {"Message": f"Confirmation with id {confirmation_id} is expired."}, 400
        if confirmation.confirmed:
            return {"Message": f"Confirmation {confirmation_id} is already confirmed."}, 404

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("conformation_page.html", email=confirmation.user.email), 200, headers)


class ConfirmationByUser(Resource):
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User with id {user_id} it is not found!"}, 404

        return (
            {
            "current_time": int(time()),
            "confirmations": [confirmation_schema.dump(each)
            for each in user.confirmation.order_by(ConfirmationModel.expire_at)]
        },
        200
        )

    def post(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Message": f"User with id {user_id} it is not found!"}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": "User is already confirmed"}, 400
                confirmation.force_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "Resend successful"}, 200
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": "resend failed"}, 500
