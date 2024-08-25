from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from flask import url_for

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False, default="Indivíduo Indigente")
    email = db.Column(db.String, nullable=False)
    senha = db.Column(db.String, nullable=True)
    adm = db.Column(db.Boolean, default=False)
    foto = db.Column(db.String, nullable=True)

    def puxar_nome(self):
        return self.nome

    def obter_foto(self):
        if self.foto:
            return url_for('static', filename='uploads/' + self.foto)
        else:
            return url_for('static', filename='default.png')


class Salas(db.Model):
    id_salas = db.Column(db.Integer, primary_key=True)
    nome_sala = db.Column(db.String, nullable=False, default="Sala Indigente")
    capacidade_armario = db.Column(db.Integer, nullable=False, default=0)
    foto_sala = db.Column(db.String, nullable=True)


    def contar_salas():
        return Salas.query.count()

class Armario(db.Model):
    id_armario = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, default=1)
    capacidade_ferramentas = db.Column(db.Integer, nullable=False, default=0)
    foto_armario = db.Column(db.String, nullable=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id_salas'), nullable=False)

    def contar_armarios_na_sala(sala_id):
        return Armario.query.filter_by(sala_id=sala_id).count()
    
    def contar_armarios():
        return Armario.query.count()

class Ferramentas(db.Model):
    id_ferramentas = db.Column(db.Integer, primary_key=True)
    nome_ferramenta = db.Column(db.String, nullable=False)
    total_ferramenta = db.Column(db.Integer, nullable=False, default=0)
    foto_ferramenta = db.Column(db.String, nullable=True)
    armario_id = db.Column(db.Integer, db.ForeignKey('armario.id_armario'), nullable=False)  # Corrigido para 'armario'
    
    def contar_ferramentas():
        return Ferramentas.query.count()

    def contar_ferramentas_no_armario(armario_id):
        return Ferramentas.query.filter_by(armario_id=armario_id).count()

class FerramentasSuporte(db.Model):
    id_ferramentas_sup = db.Column(db.Integer, primary_key=True)
    nome_ferramenta_sup = db.Column(db.String, nullable=False)
    sala_ferramenta_sup = db.Column(db.String, nullable=False, default="Sala Indigente")
    defeito_ferramenta_sup = db.Column(db.String, nullable=False)
    data_ocorrido_sup = db.Column(db.String, nullable=False)
    ocorrido_ferramenta_sup = db.Column(db.String, nullable=False)
    foto_ferramenta_sup = db.Column(db.String, nullable=True)


    def contar_ferramentas_sup():
        return FerramentasSuporte.query.count()