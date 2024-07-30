from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False,default="Individuo Indigente")
    email = db.Column(db.String, nullable=False)
    senha = db.Column(db.String, nullable=False)
    adm = db.Column(db.Boolean, default=False)








