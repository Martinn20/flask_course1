from typing import List

from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    items = db.relationship("ItemModel", lazy='dynamic')

    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls) -> List:
        return cls.query.all()
