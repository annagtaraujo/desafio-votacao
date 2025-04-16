from flask import Flask, request, jsonify
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
import redis
import os
import json

app = Flask(__name__)
CORS(app)

# Métricas personalizadas de votos para o Prometheus
metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info('app_info', 'Informações do app de votação', version='1.0.0')

votos_gracyanne = Counter('votos_gracyanne_total', 'Total de votos para Gracyanne Barbosa')
votos_belo = Counter('votos_belo_total', 'Total de votos para Belo')
votos_invalidos = Counter('votos_invalidos_total', 'Total de votos com opção inválida')

# Conexão com o Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True
    )
    # Testa a conexão
    redis_client.ping()
except redis.exceptions.ConnectionError as e:
    app.logger.error(f"Erro ao conectar ao Redis: {e}")
    redis_client = None  # ou raise SystemExit para falhar na inicialização

@app.route('/votar', methods=['POST'])
def votar():
    data = request.json
    opcao = data.get("opcao")

    if opcao not in ['Gracyanne Barbosa', 'Belo']:
        votos_invalidos.inc()
        return jsonify({"mensagem": "Opção inválida"}), 400

    if not redis_client:
        return jsonify({"mensagem": "Erro interno: Redis indisponível"}), 500

    try:
        redis_client.rpush("votos", json.dumps({"opcao": opcao}))
    except redis.exceptions.RedisError as e:
        app.logger.error(f"Erro ao enviar voto para Redis: {e}")
        return jsonify({"mensagem": "Erro ao registrar voto"}), 500

    # Alimenta as métricas
    if opcao == 'Gracyanne Barbosa':
        votos_gracyanne.inc()
    elif opcao == 'Belo':
        votos_belo.inc()

    return jsonify({"mensagem": f"Voto computado para {opcao}!"})

@app.route('/health', methods=['GET'])
def health():
    status = "ok" if redis_client and redis_client.ping() else "degraded"
    return jsonify({"status": status}), 200 if status == "ok" else 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
