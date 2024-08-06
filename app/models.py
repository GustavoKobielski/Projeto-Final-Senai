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
    senha = db.Column(db.String, nullable=True)
    adm = db.Column(db.Boolean, default=False)
    foto = db.Column(db.String,nullable=True)


class Salas(db.Model, UserMixin):
    id_salas = db.Column(db.Integer, primary_key=True)
    nome_sala = db.Column(db.String, nullable=False,default="Sala Indigente")
    capacidade_armario = db.Column(db.Integer,nullable=False,default=0)
    foto_sala = db.Column(db.String, nullable=True)

    def contar_salas():
        return Salas.query.count()

class Armario(db.Model, UserMixin):
    id_armario = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer,default=1)
    capacidade_ferramentas = db.Column(db.Integer,nullable=False,default=0)
    foto_armario = db.Column(db.String,nullable=True)

    def contar_armarios():
        return Armario.query.count()

class Ferramentas(db.Model, UserMixin):
    id_ferramentas = db.Column(db.Integer, primary_key=True)
    nome_ferramenta = db.Column(db.String, nullable=False)
    total_ferramenta = db.Column(db.Integer,nullable=False,default=0)
    foto_ferramenta = db.Column(db.String,nullable=True)

    def contar_ferramentas():
        return Ferramentas.query.count()


class FerramentasSuporte(db.Model, UserMixin):
    id_ferramentas_sup = db.Column(db.Integer, primary_key=True)
    nome_ferramenta_sup = db.Column(db.String, nullable=False)
    sala_ferramenta_sup = db.Column(db.String, nullable=False,default="Sala Indigente")
    defeito_ferramenta_sup = db.Column(db.String, nullable=False)
    data_ocorrido_sup = db.Column(db.String, nullable=False)
    ocorrido_ferramenta_sup = db.Column(db.String,nullable=False)
    foto_ferramenta_sup = db.Column(db.String,nullable=True)

    def contar_ferramentas_sup():
        return FerramentasSuporte.query.count()