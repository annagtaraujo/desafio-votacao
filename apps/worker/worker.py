import os
import json
import time
import redis
import psycopg2
from psycopg2 import pool
import logging

# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lê variáveis de ambiente
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_queue = os.environ.get("REDIS_QUEUE", "votos")

pg_host = os.environ.get("PGHOST", "localhost")
pg_port = int(os.environ.get("PGPORT", 5432))
pg_dbname = os.environ.get("PGDATABASE", "votacao")
pg_user = os.environ.get("PGUSER", "postgres")
pg_password = os.environ.get("PGPASSWORD", "postgres")

# Conexão com Redis (fila)
def connect_redis():
    while True:
        try:
            r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            r.ping()
            logger.info("Conectado ao Redis")
            return r
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Erro ao conectar ao Redis: {e}, tentando novamente...")
            time.sleep(5)

# Conexão com PostgreSQL com pool
def connect_postgres():
    try:
        pg_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=pg_host,
            port=pg_port,
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password
        )
        if pg_pool:
            logger.info("Conectado ao PostgreSQL")
        return pg_pool
    except Exception as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise

r = connect_redis()
pg_pool = connect_postgres()

# Cria a tabela se necessário
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
        _, voto_json = r.blpop(redis_queue)
        voto = json.loads(voto_json)
        opcao = voto["opcao"]

        with pg_pool.getconn() as pg_conn:
            cursor = pg_conn.cursor()
            cursor.execute("INSERT INTO votos (opcao) VALUES (%s)", (opcao,))
            pg_conn.commit()
            logger.info(f"Voto recebido e registrado: {opcao}")

    except Exception as e:
        logger.error(f"Erro ao processar voto: {e}")
        time.sleep(1)
