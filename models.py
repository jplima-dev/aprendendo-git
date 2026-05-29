from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Morador(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)

    # obrigatório
    email = db.Column(db.String(120), nullable=False)

    telefone = db.Column(db.String(20))

    # obrigatório
    apartamento = db.Column(db.String(20), nullable=False)


class Aviso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)


class Ocorrencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(50), default='aberta')


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100))
    data = db.Column(db.String(50))
    morador = db.Column(db.String(120))


class Financeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    descricao = db.Column(db.String(200), nullable=False)

    valor = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(50), default='pendente')