from app import app, db
<<<<<<< HEAD

from flask_cors import CORS

from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='react/build', template_folder='react/build')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/some_endpoint', methods=['GET'])
def some_endpoint():
    pass

if __name__ == "__main__":
    app.run(debug=True)
=======
from flask import render_template, url_for, request, redirect, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, UserForm


#Pagina Inicial
@app.route('/', methods=['GET', 'POST'])
def homepage():
    usuario = 'Mateus'
    idade = 17

    form = LoginForm()

    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))

    context = {
        'usuario': usuario,
        'idade': idade
    }
    return render_template('index.html', context=context, form=form)

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
>>>>>>> Feature/pagina-login
