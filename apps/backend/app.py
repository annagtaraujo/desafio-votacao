from flask import Flask, request, jsonify
from collections import defaultdict
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

votos = defaultdict(int)

@app.route('/votar', methods=['POST'])
def votar():
    data = request.json
    opcao = data.get("opcao")

    if opcao not in ['opcao1', 'opcao2']:
        return jsonify({"mensagem": "Opção inválida"}), 400

    votos[opcao] += 1
    return jsonify({"mensagem": f"Voto computado para {opcao}!"})

@app.route('/resultados', methods=['GET'])
def resultados():
    return jsonify(dict(votos))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
