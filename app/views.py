from app import app, db
from flask import render_template, url_for, request, redirect, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, UserForm


#Pagina Inicial
@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = LoginForm()

    # LOGIN
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        return render_template('homepage.html')

    return render_template('index.html', form=form)

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