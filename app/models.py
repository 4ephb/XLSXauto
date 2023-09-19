from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, lm

class TNVD(db.Model):
    __tablename__ = 'tnvd_names'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    number = db.Column(db.Integer)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(name, password):
        user = User(name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.name)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
