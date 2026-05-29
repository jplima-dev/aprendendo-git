from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from models import db, Morador, Aviso, Ocorrencia, Reserva, Financeiro

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///condominio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


# ============================
# MORADORES
# ============================

@app.route('/api/moradores', methods=['GET', 'POST'])
def moradores():

    if request.method == 'POST':
        data = request.json

        # CAMPOS OBRIGATÓRIOS
        if not data.get('nome') or not data.get('email') or not data.get('apartamento'):
            return jsonify({
                'message': 'Nome, email e apartamento são obrigatórios'
            }), 400

        morador = Morador(
            nome=data['nome'],
            email=data['email'],
            telefone=data.get('telefone'),
            apartamento=data['apartamento']
        )

        db.session.add(morador)
        db.session.commit()

        return jsonify({
            'message': 'Morador cadastrado com sucesso'
        }), 201

    moradores = Morador.query.all()

    return jsonify([
        {
            'id': m.id,
            'nome': m.nome,
            'email': m.email,
            'telefone': m.telefone,
            'apartamento': m.apartamento
        }
        for m in moradores
    ])


@app.route('/api/moradores/<int:id>', methods=['GET'])
def buscar_morador(id):

    morador = Morador.query.get_or_404(id)

    return jsonify({
        'id': morador.id,
        'nome': morador.nome,
        'email': morador.email,
        'telefone': morador.telefone,
        'apartamento': morador.apartamento
    })


@app.route('/api/moradores/<int:id>', methods=['PUT'])
def atualizar_morador(id):

    morador = Morador.query.get_or_404(id)
    data = request.json

    if not data.get('nome') or not data.get('email') or not data.get('apartamento'):
        return jsonify({
            'message': 'Nome, email e apartamento são obrigatórios'
        }), 400

    morador.nome = data['nome']
    morador.email = data['email']
    morador.telefone = data.get('telefone')
    morador.apartamento = data['apartamento']

    db.session.commit()

    return jsonify({
        'message': 'Morador atualizado com sucesso'
    })


@app.route('/api/moradores/<int:id>', methods=['DELETE'])
def deletar_morador(id):

    morador = Morador.query.get_or_404(id)

    db.session.delete(morador)
    db.session.commit()

    return jsonify({
        'message': 'Morador removido com sucesso'
    })


# ============================
# AVISOS
# ============================

@app.route('/api/avisos', methods=['GET', 'POST'])
def avisos():

    if request.method == 'POST':
        data = request.json

        aviso = Aviso(
            titulo=data['titulo'],
            descricao=data['descricao']
        )

        db.session.add(aviso)
        db.session.commit()

        return jsonify({
            'message': 'Aviso publicado'
        })

    avisos = Aviso.query.all()

    return jsonify([
        {
            'id': a.id,
            'titulo': a.titulo,
            'descricao': a.descricao
        }
        for a in avisos
    ])


# ============================
# FINANCEIRO / ALUGUEL
# ============================

@app.route('/api/financeiro', methods=['GET', 'POST'])
def financeiro():

    if request.method == 'POST':
        data = request.json

        aluguel = Financeiro(
            apartamento=data['apartamento'],
            valor=data['valor'],
            vencimento=data['vencimento']
        )

        db.session.add(aluguel)
        db.session.commit()

        return jsonify({
            'message': 'Aluguel cadastrado com sucesso'
        }), 201

    registros = Financeiro.query.all()

    return jsonify([
        {
            'id': f.id,
            'apartamento': f.apartamento,
            'valor': f.valor,
            'vencimento': f.vencimento
        }
        for f in registros
    ])


# EDITAR ALUGUEL
@app.route('/api/financeiro/<int:id>', methods=['PUT'])
def editar_aluguel(id):

    aluguel = Financeiro.query.get_or_404(id)
    data = request.json

    aluguel.apartamento = data.get('apartamento', aluguel.apartamento)
    aluguel.valor = data.get('valor', aluguel.valor)
    aluguel.vencimento = data.get('vencimento', aluguel.vencimento)

    db.session.commit()

    return jsonify({
        'message': 'Aluguel atualizado com sucesso'
    })


# EXCLUIR ALUGUEL
@app.route('/api/financeiro/<int:id>', methods=['DELETE'])
def deletar_aluguel(id):

    aluguel = Financeiro.query.get_or_404(id)

    db.session.delete(aluguel)
    db.session.commit()

    return jsonify({
        'message': 'Aluguel removido com sucesso'
    })


if __name__ == '__main__':
    app.run(debug=True)