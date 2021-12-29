from requests import Response, post
from flask import request, url_for
from db import db
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel

class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    confirmation = db.relationship("ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def most_recent_confirmation(self):
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        link = request.url_root[0:-1] + url_for("confirmation", confirmation_id=self.most_recent_confirmation.id)
        print(link)
        return Mailgun.send_email(
            email=[self.email],
            subject="Registration confirmation",
            text=f"Please click {link} to confirm your registration",
            html=f"<html>Please click {link} to confirm your registration</html>"
        )

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(username=email).first()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()


