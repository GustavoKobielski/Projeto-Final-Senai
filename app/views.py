from app import app, db, socketio
from flask import render_template, send_from_directory, url_for, request, redirect, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import CadastrarSala, CadastroArmario, CadastroFerramenta, EditarInformacoes, LoginForm, UserForm, CadastrarSuporte
from app.models import User, Salas, Armario, Ferramentas, FerramentasSuporte, Message, Group, GroupUser, GroupMessage
from datetime import datetime
from flask_socketio import join_room, leave_room, emit

from werkzeug.utils import secure_filename
import os
import base64
import uuid

# Sistema de uploads
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'gif', 'avif', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/salas/<filename>')
def serve_salas_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'salas'), filename)

@app.route('/uploads/armarios/<filename>')
def serve_armario_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'armarios'), filename)

@app.route('/uploads/ferramentas/<filename>')
def serve_ferramentas_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'ferramentas'), filename)

def get_unique_filename(folder_path, filename):
    """
    Gera um nome de arquivo único para evitar a sobreposição.
    """
    base, ext = os.path.splitext(filename)
    new_filename = filename
    counter = 1

    while os.path.exists(os.path.join(folder_path, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1

    return new_filename



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#############################################
######## LOGIN PAGE #########################
#############################################
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

# HOMEPAGE
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

# FUNÇÃO DA PAGINA DE SALAS
@app.route('/salas/', methods=['GET', 'POST'])
def salas():
    form = CadastrarSala()
    if form.validate_on_submit():
        file = request.files.get('foto_sala')  # Obtém o arquivo do request
        filename = None

        # Verifica se o arquivo é permitido e se tem um nome
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'salas')
            unique_filename = get_unique_filename(folder_path, filename)
            file_path = os.path.join(folder_path, unique_filename)

            # Certifica-se de que o diretório existe
            os.makedirs(folder_path, exist_ok=True)
            file.save(file_path)

        # Salva os dados da sala, incluindo o nome do arquivo
        sala = Salas(
            nome_sala=form.nome_sala.data,
            capacidade_armario=form.capacidade_armario.data,
            foto_sala=unique_filename if filename else None
        )
        db.session.add(sala)
        db.session.commit()

        return redirect(url_for('salas'))

    salas = Salas.query.all()
    armarios_por_sala = {}
    for sala in salas:
        armarios_por_sala[sala.id_salas] = Armario.contar_armarios_na_sala(sala.id_salas)
    return render_template('salas.html', salas=salas, form=form, armarios_por_sala=armarios_por_sala)


#############################################
######## PAGE ARMARIOS ######################
#############################################

# FUNÇÃO DA PAGINA DE ARMARIOS
@app.route('/armarios/<int:sala_id>', methods=['GET', 'POST'])
def armarios(sala_id):
    form = CadastroArmario()
    armarios = Armario.query.filter_by(sala_id=sala_id).all()
    sala = Salas.query.get_or_404(sala_id)

    if form.validate_on_submit():
        file = request.files.get('foto_armario')
        filename = None

        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'armarios')
            unique_filename = get_unique_filename(folder_path, filename)
            file_path = os.path.join(folder_path, unique_filename)

            # Certifica-se de que o diretório existe
            os.makedirs(folder_path, exist_ok=True)
            file.save(file_path)

        form.save(sala_id=sala_id, filename=unique_filename if filename else None)
        return redirect(url_for('armarios', sala_id=sala_id))

    ferramentas_por_armario = {armario.id_armario: Ferramentas.contar_ferramentas_no_armario(armario.id_armario) for armario in armarios}

    return render_template('armarios.html', sala=sala, armarios=armarios, form=form, ferramentas_por_armario=ferramentas_por_armario)


#############################################
######## PAGE FERRAMENTAS ###################
#############################################

# FUNCAO DA PAGINA DE FERRAMENTAS
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
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ferramentas')
            unique_filename = get_unique_filename(folder_path, filename)
            file_path = os.path.join(folder_path, unique_filename)

            # Certifica-se de que o diretório existe
            os.makedirs(folder_path, exist_ok=True)
            file.save(file_path)

        # Salva os dados da ferramenta, incluindo o nome do arquivo
        form.save(armario_id=armario_id, filename=unique_filename if filename else None)
        return redirect(url_for('ferramentas', armario_id=armario_id))

    return render_template('ferramentas.html', ferramentas=ferramentas, form=form)


#############################################
######## PAGE FERRAMENTAS SUPORTE ###########
#############################################

# FUNCAO DA PAGINA DE FERRAMENTAS SUPORTE
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
        return redirect(url_for('ferramentasSuporte'))
    return render_template('defeitoFerramentas.html', ferramentas=ferramentas, form=form, formInfo=formInfo)

#############################################
######## PAGE LOGS ##########################
#############################################

# FUNCAO DA PAGINA DE LOGS
@app.route('/logs/')
def logs():
    return render_template('logs.html')

#############################################
######## PAGE SALAS GERENCIAMENTO ###########
#############################################

# FUNCAO DA PAGINA DE GERENCIAMENTO DE SALAS
@app.route('/gerenciamento/salas')
def gerenciamento_salas():
    salas = Salas.query.all()
    armarios_por_sala = {}
    for sala in salas:
        armarios_por_sala[sala.id_salas] = Armario.contar_armarios_na_sala(sala.id_salas)
    return render_template('gerenciamentoSalas.html',salas=salas, armarios_por_sala=armarios_por_sala)

#############################################
######## PAGE PESSOAS GERENCIAMENTO #########
#############################################

# FUNCAO DA PAGINA DE GERENCIAMENTO DE PESSOAS
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

            # Verifique se o usuário já tem uma foto de perfil
            if current_user.foto:
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'perfil', current_user.foto)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)  # Exclui o arquivo antigo

            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'perfil')
                unique_filename = get_unique_filename(folder_path, filename)
                file_path = os.path.join(folder_path, unique_filename)

                # Certifica-se de que o diretório existe
                os.makedirs(folder_path, exist_ok=True)
                file.save(file_path)

            # Atualiza a foto do perfil no banco de dados
            form.save(current_user, filename if filename else current_user.foto)

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


#############################################
######## CHATTTTTTTTTTTTTTT #################
#############################################

#############################################
######## CHATTTTTTTTTTTTTTT #################
#############################################

@app.route('/chat')
@login_required
def chat():
    users = User.query.filter(User.id != current_user.id).all()
    groups = Group.query.join(GroupUser).filter(GroupUser.user_id == current_user.id).all()
    return render_template('chat.html', users=users, groups=groups, current_user=current_user)

@socketio.on('send_message')
def handle_message(data):
    try:
        recipient_id = data['to']
        sender_id = current_user.id
        message_content = data['content']
        current_time = datetime.now()

        file_data = data.get('file')
        file_name = None

        if file_data:
            original_file_name = secure_filename(file_data['filename'])
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chat')

            # Garante que o nome do arquivo é único
            file_name = get_unique_filename(folder_path, original_file_name)
            file_path = os.path.join(folder_path, file_name)

            # Certifica-se de que o diretório existe
            os.makedirs(folder_path, exist_ok=True)
            
            # Decodifica os dados base64 e salva o arquivo
            file_data_decoded = base64.b64decode(file_data['data'])
            with open(file_path, 'wb') as f:
                f.write(file_data_decoded)

        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=message_content,
            timestamp=current_time,
            viewed_by=[],
            file_path=file_name  # Salva apenas o nome do arquivo no banco de dados
        )
        db.session.add(message)
        db.session.commit()

        # Obtém informações do remetente e do destinatário
        sender = User.query.get(sender_id)
        recipient = User.query.get(recipient_id)
        
        # Cria URLs para as fotos
        sender_photo_url = url_for('static', filename='uploads/perfil/' + sender.foto) if sender.foto else url_for('static', filename='imgs/defaultPeople.png')
        recipient_photo_url = url_for('static', filename='uploads/perfil/' + recipient.foto) if recipient.foto else url_for('static', filename='imgs/defaultPeople.png')

        # Emite a mensagem para o destinatário
        emit('message_received', {
            'content': message.content,
            'from_name': sender.nome,
            'time': message.timestamp.strftime('%H:%M'),
            'message_id': message.id,
            'from_id': sender_id,
            'from_foto': sender_photo_url,
            'file_url': url_for('static', filename='uploads/chat/' + message.file_path) if message.file_path else None
        }, room=recipient_id)

        # Emite a mensagem para o remetente
        emit('message_received', {
            'content': message.content,
            'from_name': sender.nome,
            'time': message.timestamp.strftime('%H:%M'),
            'message_id': message.id,
            'from_foto': sender_photo_url,
            'file_url': url_for('static', filename='uploads/chat/' + message.file_path) if message.file_path else None
        }, room=sender_id)

        # Marca a mensagem como visualizada se o chat estiver aberto
        if data.get('chat_type') == 'user' and data.get('chat_open', False):
            message.viewed_by.append(recipient_id)
            db.session.commit()

            # Emite o status de visualização para o remetente
            emit('message_viewed', {
                'message_id': message.id,
                'viewed_by': message.viewed_by
            }, room=sender_id)

    except Exception as e:
        print(f"Erro ao salvar a mensagem: {e}")
        db.session.rollback()

@socketio.on('load_messages')
def load_messages(data):
    recipient_id = data['to']
    sender_id = current_user.id
    messages = Message.query.filter(
        ((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id)) |
        ((Message.sender_id == recipient_id) & (Message.recipient_id == sender_id))
    ).all()

    messages_data = []
    for message in messages:
        sender = User.query.get(message.sender_id)
        if sender.foto:
            sender_photo_url = url_for('static', filename='uploads/perfil/' + sender.foto)
        else:
            sender_photo_url = url_for('static', filename='imgs/defaultPeople.png')
        
        if current_user.id == recipient_id and current_user.id not in message.viewed_by:
            message.viewed_by.append(current_user.id)
            db.session.commit()

        messages_data.append({
            'content': message.content,
            'from_name': sender.nome,
            'to': message.recipient_id,
            'time': message.timestamp.strftime('%H:%M'),
            'message_id': message.id,
            'from_foto': sender_photo_url,
            'viewed_by': message.viewed_by,
            'file_url': url_for('static', filename='uploads/chat/' + message.file_path) if message.file_path else None
        })  
        print("kk: ",message.file_path)


    emit('messages_loaded', {'messages': messages_data}, room=current_user.id)



@socketio.on('mark_message_as_viewed')
def mark_message_as_viewed(data):
    message_id = data['message_id']
    message = Message.query.get(message_id)
    
    if message and current_user.id not in message.viewed_by:
        message.viewed_by.append(current_user.id)
        db.session.commit()
        
        # Emit viewed status to the recipient
        emit('message_viewed', {
            'message_id': message.id,
            'viewed_by': message.viewed_by
        }, room=message.recipient_id)
 
@socketio.on('get_last_active')
def handle_last_active(data):
    user_id = data['user_id']
    user = User.query.get(user_id)
    
    if user and user.ultimo_visto:
        now = datetime.now()
        minutes_ago = int((now - user.ultimo_visto).total_seconds() // 60)
        
        if minutes_ago < 1:
            time_display = "Online"
        elif minutes_ago < 60:
            time_display = f"{minutes_ago} minuto(s) atrás"
        else:
            hours_ago = minutes_ago // 60
            time_display = f"{hours_ago} hora(s) atrás"
        
        emit('last_active', {'user_id': user_id, 'last_active': time_display})

@socketio.on('connect')
def handle_connect():
    current_user.ultimo_visto = datetime.now()
    db.session.commit()
    join_room(current_user.id)

@socketio.on('disconnect')
def handle_disconnect():
    current_user.ultimo_visto = datetime.now()
    db.session.commit()
    leave_room(current_user.id)

@socketio.on('create_group')
def handle_create_group(data):
    group_name = data['name']
    user_ids = data['users']

    if not group_name or not user_ids:
        return

    # Criar o grupo
    group = Group(name=group_name)
    db.session.add(group)
    db.session.commit()

    # Adicionar os usuários ao grupo
    for user_id in user_ids:
        group_user = GroupUser(group_id=group.id, user_id=user_id)
        db.session.add(group_user)

    db.session.commit()


    socketio.emit('group_created', {'group_id': group.id, 'group_name': group_name}, room=None)

@socketio.on('load_group_messages')
def load_group_messages(data):
    group_id = data['group_id']
    messages = GroupMessage.query.filter_by(group_id=group_id).all()

    messages_data = []
    for message in messages:
        sender = User.query.get(message.sender_id)
        messages_data.append({
            'content': message.content,
            'from_name': sender.nome,
            'time': message.timestamp.strftime('%H:%M')
        })

    emit('group_messages_loaded', {'messages': messages_data}, room=current_user.id)

@socketio.on('send_group_message')
def handle_group_message(data):
    try:
        group_id = data.get('to')
        if group_id is None:
            raise ValueError("Group ID is missing")

        sender_id = current_user.id
        message_content = data.get('content')
        if message_content is None:
            raise ValueError("Message content is missing")

        current_time = datetime.now()
        group_message = GroupMessage(
            group_id=group_id,
            sender_id=sender_id,
            content=message_content,
            timestamp=current_time
        )
        db.session.add(group_message)
        db.session.commit()

        # Emitir mensagem para todos os membros do grupo
        group_users = GroupUser.query.filter_by(group_id=group_id).all()
        for group_user in group_users:
            emit('group_message', {
                'content': group_message.content,
                'from_name': current_user.nome,
                'time': group_message.timestamp.strftime('%H:%M')
            }, room=group_user.user_id, broadcast=False)

    except Exception as e:
        print(f"Error saving group message: {e}")
        db.session.rollback()

@socketio.on('leave_group')
def handle_leave_group(data):
    try:
        group_id = data['group_id']
        user_id = current_user.id

        # Remover o usuário do grupo
        group_user = GroupUser.query.filter_by(group_id=group_id, user_id=user_id).first()
        if group_user:
            db.session.delete(group_user)
            db.session.commit()

        # Emitir evento para atualizar a lista de grupos
        emit('group_left', {'group_id': group_id}, room=user_id)
    except Exception as e:
        print(f"Error leaving group: {e}")
        db.session.rollback()

def get_last_active_display(user):
    if not user.ultimo_visto:
        return "Desconhecido"

    now = datetime.now()
    minutes_ago = int((now - user.ultimo_visto).total_seconds() // 60)
    
    if minutes_ago < 1:
        return "Online"
    elif minutes_ago < 60:
        return f"{minutes_ago} minuto(s) atrás"
    else:
        hours_ago = minutes_ago // 60
        return f"{hours_ago} hora(s) atrás"
    