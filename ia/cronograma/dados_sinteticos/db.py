"""
db.py — Conexão com o banco (Supabase/PostgreSQL)

Todos os scripts de geração de dados e, futuramente, o scheduler,
importam a função conectar() daqui em vez de duplicar a lógica de conexão.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """
    Retorna uma conexão psycopg2 aberta, usando a variável de ambiente DATABASE_URL.
    Lança erro claro se a variável não estiver configurada (evita esquecimento silencioso).
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não encontrada. Copie .env.example para .env "
            "e preencha com a connection string do Supabase."
        )
    return psycopg2.connect(database_url)