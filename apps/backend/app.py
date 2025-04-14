from flask import Flask, request, jsonify
from collections import defaultdict
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

app = Flask(__name__)
CORS(app)

# Configuração para o PrometheusMetrics agrupar métricas por endpoint e status HTTP
metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info('app_info', 'Informações do app de votação', version='1.0.0')

# Métrica personalizada para regra de negócio: contadores de votos
votos_gracyanne = Counter('votos_gracyanne_total', 'Total de votos para Gracyanne Barbosa')
votos_belo = Counter('votos_belo_total', 'Total de votos para Belo')
votos_invalidos = Counter('votos_invalidos_total', 'Total de votos com opção inválida')

# Armazenamento simples dos votos (não persistente)
# Essa etapa será modificada para poder persistir os votos em um DB simples
votos = defaultdict(int)

@app.route('/votar', methods=['POST'])
def votar():
    data = request.json
    opcao = data.get("opcao")

    if opcao not in ['Gracyanne Barbosa', 'Belo']:
        votos_invalidos.inc()
        return jsonify({"mensagem": "Opção inválida"}), 400

    votos[opcao] += 1
    if opcao == 'Gracyanne Barbosa':
        votos_gracyanne.inc()
    elif opcao == 'Belo':
        votos_belo.inc()

    return jsonify({"mensagem": f"Voto computado para {opcao}!"})

@app.route('/resultados', methods=['GET'])
def resultados():
    return jsonify(dict(votos))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
