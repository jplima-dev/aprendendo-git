from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session
)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

import pymysql

app = Flask(__name__)

# ======================= #
# == CONFIGURAÇÕES ====== #
# ======================= #

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/caderno_online'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ================= #
# == MODELS ======= #
# ================= #

class Aluno(db.Model):
    __tablename__ = 'alunos'

    id_alu = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    num_chamada = db.Column(db.Integer, nullable=False)
    advertencia = db.Column(db.Integer, default=0)
    observacoes = db.Column(db.Text)

    sala_id = db.Column(
        db.Integer,
        db.ForeignKey('salas.id_sala'),
        nullable=False
    )

    def __repr__(self):
        return f'nome={self.nome}'


class Sala(db.Model):
    __tablename__ = 'salas'

    id_sala = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(50),
        nullable=False
    )

    anotacao = db.Column(
        db.Text
    )

    alunos = db.relationship(
        'Aluno',
        backref='sala',
        lazy=True
    )

    tarefas = db.relationship(
        'Tarefas',
        backref='sala',
        lazy=True
    )

    def __repr__(self):
        return f'nome={self.nome}'


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usu = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default='Viewer')

    def __repr__(self):
        return f'nome={self.nome}'


class Tarefas(db.Model):
    __tablename__ = 'tarefas'

    id_tarefa = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(255))

    sala_id = db.Column(
        db.Integer,
        db.ForeignKey('salas.id_sala'),
        nullable=False
    )

    def __repr__(self):
        return f'nome={self.nome}'
    

class ObservacaoAluno(db.Model):
    __tablename__ = 'observacoes_aluno'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id_alu'), nullable=False)


# ======================== #
# == FUNÇÕES AUXILIARES == #
# ======================== #

def usuario_logado():
    return 'usuario_id' in session

def usuario_admin():
    return session.get('usuario_role') == 'Admin'


def usuario_assistant():
    return session.get('usuario_role') == 'Assistant'


def usuario_viewer():
    return session.get('usuario_role') == 'Viewer'


def usuario_staff():
    return session.get('usuario_role') in ['Admin', 'Assistant']

# ====================== #
# == ROTAS PRINCIPAIS == #
# ====================== #

@app.route('/')
def index():

    if usuario_logado():
        return redirect(url_for('home'))

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        nome = request.form.get('nome')
        senha = request.form.get('senha')

        user = Usuario.query.filter_by(nome=nome).first()

        if user and check_password_hash(user.senha, senha):

            session['usuario_id'] = user.id_usu
            session['usuario_nome'] = user.nome
            session['usuario_role'] = user.role

            return redirect(url_for('home'))

        return render_template(
            'login.html',
            erro='Usuário ou senha inválidos'
        )

    return render_template('login.html')


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():

    if request.method == 'POST':

        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template(
                'registrar.html',
                erro='Preencha todos os campos'
            )

        usuario_existente = Usuario.query.filter_by(nome=nome).first()

        if usuario_existente:
            return render_template(
                'registrar.html',
                erro='Usuário já existe'
            )

        novo_usuario = Usuario(
            nome=nome,
            senha=generate_password_hash(senha),
            role='Viewer'
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('registrar.html')


@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))


@app.route('/home')
def home():

    if not usuario_logado():
        return redirect(url_for('login'))

    alunos = Aluno.query.all()
    salas = Sala.query.all()
    tarefas = Tarefas.query.all()

    return render_template(
        'dashboard.html',
        alunos=alunos,
        salas=salas,
        tarefas=tarefas
    )


# ================== #
# == PAGINA ALUNOS = #
# ================== #


@app.route('/alunos/criar', methods=['POST'])
def criar_aluno():

    # precisa estar logado
    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN
    if not usuario_admin():
        return redirect(url_for('home'))

    nome = request.form.get('nome')
    num_chamada = request.form.get('num_chamada')
    sala_id = request.form.get('sala_id')

    if not sala_id:
        return "Sala não enviada", 400

    novo_aluno = Aluno(
        nome=nome,
        num_chamada=int(num_chamada),
        sala_id=int(sala_id)
    )

    db.session.add(novo_aluno)
    db.session.commit()

    return redirect(url_for('abrir_sala', id=sala_id))


@app.route('/alunos/<int:id>/observacao', methods=['POST'])
def adicionar_observacao(id):

    # precisa estar logado
    if not usuario_logado():
        return redirect(url_for('login'))

    # ADMIN e ASSISTANT podem adicionar observações
    if not usuario_staff():
        return redirect(url_for('home'))

    aluno = Aluno.query.get_or_404(id)

    texto = request.form.get('texto')

    if not texto:
        return redirect(url_for('abrir_sala', id=aluno.sala_id))

    # cria observação
    obs = ObservacaoAluno(
        texto=texto,
        aluno_id=aluno.id_alu
    )

    db.session.add(obs)

    # aumenta advertência
    aluno.advertencia = (aluno.advertencia or 0) + 1

    db.session.commit()

    return redirect(url_for('abrir_sala', id=aluno.sala_id))


@app.route('/alunos/deletar/<int:id>')
def deletar_aluno(id):

    # precisa estar logado
    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN pode deletar
    if not usuario_admin():
        return redirect(url_for('home'))

    aluno = Aluno.query.get_or_404(id)

    sala_id = aluno.sala_id

    db.session.delete(aluno)
    db.session.commit()

    return redirect(url_for('abrir_sala', id=sala_id))


# ================= #
# == PAGINA SALAS = #
# ================= #

@app.route('/salas')
def salas():

    if not usuario_logado():
        return redirect(url_for('login'))

    return redirect(url_for('home'))


@app.route('/salas/criar', methods=['POST'])
def criar_sala():

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('home'))

    nome = request.form.get('nome')

    if not nome:
        return redirect(url_for('home'))

    nova_sala = Sala(nome=nome)

    db.session.add(nova_sala)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/salas/<int:id>')
def abrir_sala(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    sala = Sala.query.get_or_404(id)

    tarefas = Tarefas.query.filter_by(sala_id=id).all()
    alunos = Aluno.query.filter_by(sala_id=id).all()

    # VIEWER só pode ver
    # ASSISTENT pode adicionar tarefa/observação
    # ADMIN acesso total

    return render_template(
        'sala.html',
        sala=sala,
        tarefas=tarefas,
        alunos=alunos
    )


@app.route('/salas/<int:id>/anotacao', methods=['POST'])
def editar_anotacao_sala(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('abrir_sala', id=id))

    sala = Sala.query.get_or_404(id)

    sala.anotacao = request.form.get('anotacao')

    db.session.commit()

    return redirect(url_for('abrir_sala', id=id))


@app.route('/salas/deletar/<int:id>')
def deletar_sala(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('home'))

    sala = Sala.query.get_or_404(id)

    db.session.delete(sala)
    db.session.commit()

    return redirect(url_for('home'))

# ==================== #
# == PAGINA TAREFAS == #
# ==================== #

@app.route('/tarefas/criar', methods=['POST'])
def criar_tarefa():

    if not usuario_logado():
        return redirect(url_for('login'))

    # ADMIN e ASSISTENT podem criar tarefa
    if session.get('usuario_role') not in ['Admin', 'Assistente']:
        return redirect(url_for('home'))

    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    sala_id = request.form.get('sala_id')

    if not sala_id:
        return "Sala não enviada", 400

    if not nome:
        return redirect(url_for('abrir_sala', id=sala_id))

    nova_tarefa = Tarefas(
        nome=nome,
        descricao=descricao,
        sala_id=int(sala_id)
    )

    db.session.add(nova_tarefa)
    db.session.commit()

    return redirect(url_for('abrir_sala', id=sala_id))


@app.route('/tarefas/<int:id>/editar', methods=['POST'])
def editar_tarefa(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    # ADMIN e ASSISTENT podem editar
    if session.get('usuario_role') not in ['Admin', 'Assistente']:
        return redirect(url_for('home'))

    tarefa = Tarefas.query.get_or_404(id)

    nome = request.form.get('nome')
    descricao = request.form.get('descricao')

    if nome:
        tarefa.nome = nome

    tarefa.descricao = descricao

    db.session.commit()

    return redirect(url_for('abrir_sala', id=tarefa.sala_id))


@app.route('/tarefas/deletar/<int:id>')
def deletar_tarefa(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN pode deletar
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('home'))

    tarefa = Tarefas.query.get_or_404(id)

    sala_id = tarefa.sala_id

    db.session.delete(tarefa)
    db.session.commit()

    return redirect(url_for('abrir_sala', id=sala_id))

# ====================== #
# == PAGINA USUARIOS === #
# ====================== #

@app.route('/usuarios')
def usuarios():

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN pode acessar
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('home'))

    usuarios = Usuario.query.all()

    return render_template(
        'usuarios.html',
        usuarios=usuarios
    )


@app.route('/usuarios/deletar/<int:id>')
def deletar_usuario(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN pode deletar
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('home'))

    usuario = Usuario.query.get_or_404(id)

    # impede deletar a si mesmo
    if usuario.id_user == session.get('usuario_id'):
        return redirect(url_for('usuarios'))

    db.session.delete(usuario)
    db.session.commit()

    return redirect(url_for('usuarios'))


@app.route('/usuarios/<int:id>/editar_role', methods=['POST'])
def editar_role_usuario(id):

    if not usuario_logado():
        return redirect(url_for('login'))

    # SOMENTE ADMIN
    if session.get('usuario_role') != 'Admin':
        return redirect(url_for('home'))

    usuario = Usuario.query.get_or_404(id)

    nova_role = request.form.get('role')

    # roles válidas
    roles_validas = ['Admin', 'Assistente', 'Viewer']

    if nova_role not in roles_validas:
        return redirect(url_for('usuarios'))

    usuario.role = nova_role

    db.session.commit()

    return redirect(url_for('usuarios'))

# ================= #
# == EXECUÇÃO ===== #
# ================= #

if __name__ == '__main__':
    app.run(debug=True)