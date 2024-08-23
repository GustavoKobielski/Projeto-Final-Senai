from app import app, db
from flask import render_template, send_from_directory, url_for, request, redirect, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import CadastrarSala, CadastroArmario, CadastroFerramenta, EditarInformacoes, LoginForm, UserForm, CadastrarSuporte
from app.models import User, Salas, Armario, Ferramentas, FerramentasSuporte
from datetime import datetime


from werkzeug.utils import secure_filename




import os




UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'gif', 'avif'}


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Pagina Inicial
@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = LoginForm()


    # LOGIN
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        return redirect(url_for('home'))


    return render_template('index.html', form=form, usuario=current_user)


@app.context_processor
def inject_user():
    return dict(current_user=current_user)


#############################################
######## CADASTRO/LOGIN SETUP ###############
#############################################


#Função de Cadastro
@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():
    form = UserForm()
    if form.validate_on_submit():
        user = form.save()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))
    return render_template('cadastro.html', form=form)


# Função de dar logout
@app.route('/sair/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


#############################################
######## PAGE HOMES #########################
#############################################


@app.route('/home/')
def home():
    qtd_sala = Salas.contar_salas()
    qtd_armario = Armario.contar_armarios()
    qtd_ferramenta = Ferramentas.contar_ferramentas()
    qtd_ferramenta_sup = FerramentasSuporte.contar_ferramentas_sup()


    return render_template('homepage.html', qtd_sala=qtd_sala,  qtd_armario=qtd_armario, qtd_ferramenta=qtd_ferramenta, qtd_ferramenta_sup=qtd_ferramenta_sup)


#############################################
######## PAGE SALAS #########################
#############################################


@app.route('/salas/', methods=['GET', 'POST'])
def salas():
    form = CadastrarSala()
    if form.validate_on_submit():
        file = request.files.get('foto_sala')  # Obtém o arquivo do request
        filename = None


        # Verifica se o arquivo é permitido e se tem um nome
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
           
            # Salva o arquivo no diretório de uploads
            file.save(file_path)
       
        # Salva os dados da sala, incluindo o nome do arquivo
        form.save(filename)
        return redirect(url_for('salas'))
   
    salas = Salas.query.all()
    return render_template('salas.html', salas=salas, form=form)


#############################################
######## PAGE ARMARIOS ######################
#############################################


@app.route('/armarios/<int:sala_id>', methods=['GET', 'POST'])
def armarios(sala_id):
    form = CadastroArmario()
    armarios = Armario.query.filter_by(sala_id=sala_id).all()

    if form.validate_on_submit():
        file = request.files.get('foto_armario')  # Obtém o arquivo do request
        filename = None


        # Verifica se o arquivo é permitido e se tem um nome
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
           
            # Salva o arquivo no diretório de uploads
            file.save(file_path)
       
        # Salva os dados da sala, incluindo o nome do arquivo
        form.save(sala_id=sala_id, filename=filename)
        return redirect(url_for('armarios', sala_id=sala_id))
    
    return render_template('armarios.html', armarios=armarios, form=form)


#############################################
######## PAGE FERRAMENTAS ###################
#############################################

@app.route('/ferramentas/<int:armario_id>', methods=['GET', 'POST'])
def ferramentas(armario_id):
    ferramentas = Ferramentas.query.filter_by(armario_id=armario_id).all()
    form = CadastroFerramenta()
    if form.validate_on_submit():
        file = request.files.get('foto_ferramenta')  # Obtém o arquivo do request
        filename = None


        # Verifica se o arquivo é permitido e se tem um nome
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
           
            # Salva o arquivo no diretório de uploads
            file.save(file_path)
       
        # Salva os dados da sala, incluindo o nome do arquivo
        form.save(armario_id=armario_id, filename=filename)
        return redirect(url_for('armarios', armario_id=armario_id))

    return render_template('ferramentas.html', ferramentas=ferramentas, form=form)



#############################################
######## PAGE FERRAMENTAS SUPORTE ###########
#############################################


@app.route('/ferramentas/suporte', methods=['GET', 'POST'])
def ferramentasSuporte():
    ferramentas = FerramentasSuporte.query.all()
    form = CadastrarSuporte()
    formInfo = CadastrarSuporte()
    if form.validate_on_submit():
        file = request.files.get('foto_ferramenta_sup')
        filename = None


        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)


            file.save(file_path)


        form.save(filename)
        return redirect(url_for('ferramentas'))
    return render_template('defeitoFerramentas.html', ferramentas=ferramentas, form=form, formInfo=formInfo)

#############################################
######## PAGE LOGS ##########################
#############################################


@app.route('/logs/')
def logs():
    return render_template('logs.html')


##### gerenciamento


#############################################
######## PAGE SALAS GERENCIAMENTO ###########
#############################################


@app.route('/gerenciamento/salas')
def gerenciamento_salas():
    return render_template('gerenciamentoSalas.html')


#############################################
######## PAGE PESSOAS GERENCIAMENTO ###########
#############################################


@app.route('/gerenciamento/pessoas')
def gerenciamento_pessoas():
    return render_template('gerenciamentoPessoas.html')




#############################################
######## PAGE PROFILE #######################
#############################################


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = EditarInformacoes(obj=current_user)
    if form.validate_on_submit():
        try:
            file = request.files.get('foto')  # Obtém o arquivo do request
            filename = None



            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)



                file.save(file_path)


            form.save(current_user, filename)


            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('editar_perfil'))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('profile.html', form=form)


#############################################
######## GOOGLE SETUP #######################
#############################################


from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='841818364820-eg98vp2chajm8vfnuku3tvsj5s91egbb.apps.googleusercontent.com',
    client_secret='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',
    authorize_params=None,
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    redirect_uri='http://localhost:5000/login/google/callback',
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'  # URL dos metadados do servidor do Google OAuth
)


@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri, prompt='select_account')


@app.route('/login/google/callback')
def authorize_google():
    token = google.authorize_access_token()
    print("Token de Acesso do Google:", token)


    # Verifique se o token foi obtido corretamente
    if 'access_token' in token:
        # Faça uma solicitação para obter as informações do usuário usando o token de acesso
        resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
        user_info = resp.json()


        # Verifique se as informações do usuário foram obtidas corretamente
        if user_info:
            # Verifique se o usuário já existe no banco de dados com base no e-mail fornecido pelo Google
            user = User.query.filter_by(email=user_info['email']).first()


            if not user:
                # Se o usuário não existir, crie um novo registro no banco de dados
                user = User(nome=user_info.get('given_name', ''),
                            email=user_info.get('email', ''))
                db.session.add(user)
                db.session.commit()


            # Faça login do usuário
            login_user(user, remember=True)


            # Redirecione o usuário para a página principal
            return redirect(url_for('homepage'))


    # Se houver algum problema, redirecione o usuário para uma página de erro ou para a página de login novamente
    return redirect(url_for('login_google'))
