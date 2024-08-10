from app import app, db
from flask import render_template, url_for, request, redirect, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, UserForm
from app.models import User


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
    return render_template('homepage.html')

#############################################
######## PAGE SALAS #########################
#############################################

@app.route('/salas/')
def salas():
    return render_template('salas.html')


#############################################
######## PAGE ARMARIOS ######################
#############################################

@app.route('/armarios/')
def armarios():
    return render_template('armarios.html')

#############################################
######## PAGE FERRAMENTAS ###################
#############################################

@app.route('/ferramentas/')
def ferramentas():
    return render_template('defeitoFerramentas.html')

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
    return render_template('gerenciamento_salas.html')

#############################################
######## PAGE PESSOAS GERENCIAMENTO ###########
#############################################

@app.route('/gerenciamento/pessoas')
def gerenciamento_pessoas():
    return render_template('gerenciamento_pessoas.html')

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