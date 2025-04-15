import json
import time
import redis
import psycopg2
from psycopg2 import pool
import logging

# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conexão com Redis (fila)
redis_host = "redis-service.dev.svc.cluster.local"
redis_port = 6379
redis_queue = "votos"

# Tentativas de reconexão ao Redis
def connect_redis():
    while True:
        try:
            r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            r.ping()  # Testa a conexão
            logger.info("Conectado ao Redis")
            return r
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Erro ao conectar ao Redis: {e}, tentando novamente...")
            time.sleep(5)

# Conexão com PostgreSQL com pool
def connect_postgres():
    try:
        pg_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,  # Mínimo e máximo de conexões no pool
            host="postgres-service.dev.svc.cluster.local",
            port=5432,
            dbname="votacao",
            user="postgres",
            password="postgres"
        )
        if pg_pool:
            logger.info("Conectado ao PostgreSQL")
        return pg_pool
    except Exception as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise

# Tentar conectar ao Redis e PostgreSQL
r = connect_redis()
pg_pool = connect_postgres()

# Se a tabela não existe, ela é criada aqui
with pg_pool.getconn() as pg_conn:
    cursor = pg_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votos (
            id SERIAL PRIMARY KEY,
            opcao VARCHAR(100) NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    pg_conn.commit()

logger.info("Worker rodando... aguardando votos.")

while True:
    try:
        # Espera o voto chegar na fila Redis
        _, voto_json = r.blpop(redis_queue)
        voto = json.loads(voto_json)
        opcao = voto["opcao"]

        # Insere o voto no banco
        with pg_pool.getconn() as pg_conn:
            cursor = pg_conn.cursor()
            cursor.execute("INSERT INTO votos (opcao) VALUES (%s)", (opcao,))
            pg_conn.commit()
            logger.info(f"Voto recebido e registrado: {opcao}")

    except Exception as e:
        logger.error(f"Erro ao processar voto: {e}")
        time.sleep(1)
