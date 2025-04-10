from flask import Flask, request, jsonify
import requests
from collections import defaultdict
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

votos = defaultdict(int)

RECAPTCHA_SECRET = 'SUA_SECRET_KEY'

def verificar_recaptcha(token):
    resposta = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        'secret': RECAPTCHA_SECRET,
        'response': token
    })
    resultado = resposta.json()
    return resultado.get("success", False)

@app.route('/votar', methods=['POST'])
def votar():
    data = request.json
    opcao = data.get("opcao")
    token = data.get("token")

    if not verificar_recaptcha(token):
        return jsonify({"mensagem": "Verificação falhou. Tente novamente."}), 400

    if opcao not in ['opcao1', 'opcao2']:
        return jsonify({"mensagem": "Opção inválida"}), 400

    votos[opcao] += 1
    return jsonify({"mensagem": f"Voto computado para {opcao}!"})

@app.route('/resultados', methods=['GET'])
def resultados():
    return jsonify(dict(votos))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
