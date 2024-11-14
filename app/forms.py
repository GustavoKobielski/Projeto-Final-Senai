from flask_wtf import FlaskForm
from app import db, bcrypt,app
from wtforms import StringField, SubmitField, PasswordField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError

from app.models import Armario, Ferramentas, User, Salas, FerramentasSuporte


# Cadastro do Usuario
class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confimar senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar')


    def validate_email(self, email):
        
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Usuário já cadastrado com esse e-mail!')


    def save(self):
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))
        user = User(
            nome = self.nome.data,
            email = self.email.data,
            senha = senha
        )
        db.session.add(user)
        db.session.commit()
        return user
   


# Login do Usuario
class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Login')


    def login(self):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.senha, self.senha.data.encode('utf-8')):
                    return user
            else:
                    raise Exception('Senha Incorreta!!!')
        else:
            raise Exception('Usuario nao encontrado')
       


class CadastrarSala(FlaskForm):
    nome_sala = StringField('Nome da Sala', validators=[DataRequired()])
    capacidade_armario = StringField('Quantos armários tem a sala', validators=[DataRequired()])
    foto_sala = FileField('Foto da Sala')
    btnSubmit = SubmitField('Cadastrar')


    def save(self, filename=None):
        sala = Salas(
            nome_sala=self.nome_sala.data,
            capacidade_armario=self.capacidade_armario.data,
            foto_sala=filename  # Recebe o nome do arquivo aqui
        )
        db.session.add(sala)
        db.session.commit()
        return sala


class CadastrarSuporte(FlaskForm):
    nome_ferramenta_sup = StringField("Nome da Ferramenta", validators=[DataRequired()])
    sala_ferramenta_sup = StringField("Sala que está", validators=[DataRequired()])
    defeito_ferramenta_sup = StringField("Defeito da ferramenta", validators=[DataRequired()])
    data_ocorrido_sup = StringField("Data", validators=[DataRequired()])
    ocorrido_ferramenta_sup = StringField("Ocorrido", validators=[DataRequired()])
    foto_ferramenta_sup = FileField('Foto')
    btnSubmit = SubmitField('Cadastrar')

    def save(self, filename=None, numero=None):
        suporte = FerramentasSuporte(
            numero=numero,
            nome_ferramenta_sup=self.nome_ferramenta_sup.data,
            sala_ferramenta_sup=self.sala_ferramenta_sup.data,
            defeito_ferramenta_sup=self.defeito_ferramenta_sup.data,
            data_ocorrido_sup=self.data_ocorrido_sup.data,
            ocorrido_ferramenta_sup=self.ocorrido_ferramenta_sup.data,
            foto_ferramenta_sup=filename
        )
        db.session.add(suporte)
        db.session.commit()
        return suporte
    
class EditarInformacoes(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha_atual = PasswordField('Senha Atual', validators=[Optional()])
    nova_senha = PasswordField('Nova Senha', validators=[Optional(), Length(min=6)])
    foto = FileField('Foto de Perfil', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'jfif', 'gif'], 'Somente imagens são permitidas.')])
    submit = SubmitField('Salvar Alterações')

    def save(self, user, filename=None):
        # Verifica se a senha atual foi fornecida e é válida antes de qualquer alteração
        if self.senha_atual.data:
            print("Senha atual fornecida:", self.senha_atual.data)
            if not bcrypt.check_password_hash(user.senha, self.senha_atual.data):
                print("Senha atual incorreta")
                raise ValueError('Senha atual incorreta.')  # Interrompe o processo se a senha for incorreta

            # Atualiza o nome e o email após a verificação da senha
            user.nome = self.nome.data
            user.email = self.email.data
            print("Nome e email atualizados:", user.nome, user.email)

            # Processa nova senha, se fornecida
            if self.nova_senha.data:
                print("Nova senha fornecida:", self.nova_senha.data)
                user.senha = bcrypt.generate_password_hash(self.nova_senha.data).decode('utf-8')
            else:
                print("Nenhuma nova senha fornecida")

            # Atualiza a foto do usuário somente se um novo arquivo foi enviado
            if filename:
                print("Atualizando foto para o arquivo:", filename)
                user.foto = filename

            # Commite as mudanças no banco de dados
            db.session.commit()
            print("Informações salvas com sucesso")
            return user
        else:
            raise ValueError("Senha atual não fornecida.")
    

class CadastroArmario(FlaskForm):
    numero = StringField("Numero do Armario", validators=[DataRequired()])
    capacidade_ferramentas = StringField('Quantas ferramentas tem a sala', validators=[DataRequired()])
    foto_armario = FileField('Foto do Armario')
    btnSubmit = SubmitField('Cadastrar')


    def save(self, sala_id, filename=None):
        armario = Armario(
            numero=self.numero.data,
            capacidade_ferramentas=self.capacidade_ferramentas.data,
            foto_armario=filename,
            sala_id=sala_id
        )
        db.session.add(armario)
        db.session.commit()
        return armario

class CadastroFerramenta(FlaskForm):
    nome_ferramenta = StringField("Nome das ferramentas", validators=[DataRequired()])
    total_ferramenta = StringField('Quantas ferramentas tem total', validators=[DataRequired()])
    foto_ferramenta = FileField('Foto do Armario')
    btnSubmit = SubmitField('Cadastrar')


    def save(self, armario_id, filename=None, numero=None):
        ferramentas = Ferramentas(
            numero=numero,
            nome_ferramenta=self.nome_ferramenta.data,
            total_ferramenta=self.total_ferramenta.data,
            foto_ferramenta=filename,
            armario_id=armario_id
        )
        db.session.add(ferramentas)
        db.session.commit()
        return ferramentas
    

class ScanearForm(FlaskForm):
    numero_scan = StringField("Clique aqui e scaneie o código de barras", validators=[DataRequired()])
    btnSubmit = SubmitField('Procurar')