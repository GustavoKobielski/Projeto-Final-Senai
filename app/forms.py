from flask_wtf import FlaskForm
from app import db, bcrypt,app
from wtforms import StringField, SubmitField, PasswordField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError

from app.models import User, Salas, FerramentasSuporte


# Cadastro do Usuario
class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()]) 
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confimar senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar')

    def validate_email(self, email):
        if '@edu.sc.senai.br' not in email.data:
            raise ValidationError('O e-mail deve ser do domínio @edu.sesisenai.org.br!')
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

    def save(self, filename=None):
        suporte = FerramentasSuporte(
            nome_ferramenta=self.nome_ferramenta_sup.data,
            sala_ferramenta=self.sala_ferramenta_sup.data,
            defeito_ferramenta=self.defeito_ferramenta_sup.data,
            data_ocorrido=self.data_ocorrido_sup.data,
            ocorrido_ferramenta=self.ocorrido_ferramenta_sup.data,
            foto_ferramenta=filename
        )
        db.session.add(suporte)
        db.session.commit()
        return suporte
    

class EditarInformacoes(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha_atual = PasswordField('Senha Atual', validators=[Optional()])
    nova_senha = PasswordField('Nova Senha', validators=[Optional(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Nova Senha', validators=[Optional(), EqualTo('nova_senha', message='As senhas devem corresponder.')])
    foto = FileField('Foto de Perfil', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'jfif', 'gif'], 'Somente imagens são permitidas.')])
    submit = SubmitField('Salvar Alterações')

    def save(self, user, filename=None):
        # Atualiza as informações do usuário
        user.nome = self.nome.data
        user.email = self.email.data

        # Verifica se a senha atual foi fornecida e se é válida
        if self.senha_atual.data:
            if not bcrypt.check_password_hash(user.senha, self.senha_atual.data):
                raise ValueError('Senha atual incorreta.')
            if self.nova_senha.data:
                user.senha = bcrypt.generate_password_hash(self.nova_senha.data).decode('utf-8')

        if filename:
            user.foto = filename

        db.session.commit()
        return user
        