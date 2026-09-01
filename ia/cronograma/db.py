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


# ============================================================
# Mapeamento de dias de trabalho -> dias da semana permitidos
# (Python: weekday() -> segunda=0 ... domingo=6)
# ============================================================
DIAS_TRABALHO_MAP = {
    "seg-sex": range(0, 5),   # segunda a sexta
    "seg-sab": range(0, 6),   # segunda a sábado
}


def _dia_permitido(dias_trabalho, data):
    """Retorna True se `data` cair dentro do intervalo de dias_trabalho do funcionário."""
    dias_permitidos = DIAS_TRABALHO_MAP.get(dias_trabalho, range(0, 5))
    return data.weekday() in dias_permitidos


def buscar_trechos_pendentes():
    """
    Busca trechos que precisam de poda (status amarelo ou vermelho),
    usando sempre a previsão MAIS RECENTE por trecho (caso existam várias ao longo do tempo).

    Retorna: lista de dicts, já ordenada por prioridade
             (vermelho antes de amarelo, e dentro de cada status, prazo mais próximo primeiro).
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT trecho_id, km_inicio, km_fim, localizacao, extensao_m,
               latitude, longitude, nivel_urgencia, prazo_limite
        FROM (
            SELECT DISTINCT ON (p.trecho_id)
                t.id AS trecho_id, t.km_inicio, t.km_fim, t.localizacao, t.extensao_m,
                t.latitude, t.longitude, p.nivel_urgencia, p.prazo_limite, p.data_previsao
            FROM previsao_urgencia p
            JOIN trechos t ON t.id = p.trecho_id
            ORDER BY p.trecho_id, p.data_previsao DESC
        ) mais_recente
        WHERE nivel_urgencia IN ('amarelo', 'vermelho')
        ORDER BY
            CASE nivel_urgencia WHEN 'vermelho' THEN 0 WHEN 'amarelo' THEN 1 END,
            prazo_limite ASC
        """
    )
    colunas = [desc[0] for desc in cursor.description]
    resultado = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    cursor.close()
    conn.close()
    return resultado


def buscar_funcionarios_disponiveis(data):
    """
    Busca todos os funcionários e filtra (em Python) quem está disponível na `data` informada,
    com base no campo dias_trabalho. Feriados/exceções não são considerados por enquanto.

    Retorna: lista de dicts com os funcionários disponíveis naquele dia.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome, turno_inicio, turno_fim, dias_trabalho,
               localizacao_base, latitude_base, longitude_base, velocidade_poda_m_por_hora
        FROM funcionarios
        """
    )
    colunas = [desc[0] for desc in cursor.description]
    todos = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    cursor.close()
    conn.close()

    disponiveis = [f for f in todos if _dia_permitido(f["dias_trabalho"], data)]
    return disponiveis


def salvar_cronograma(alocacoes, data):
    """
    Salva o cronograma sugerido para uma data específica.
    Sobrescreve: apaga qualquer cronograma já existente para essa data antes de inserir o novo
    (decisão do grupo, pra facilitar testes iterativos do algoritmo sem acumular lixo).

    Recebe: lista de dicts no formato
        {trecho_id, funcionario_id, horario_inicio, horario_fim, ordem_no_trajeto}
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cronograma_sugerido WHERE data_agendada = %s", (data,))

    for a in alocacoes:
        cursor.execute(
            """
            INSERT INTO cronograma_sugerido
                (trecho_id, funcionario_id, data_agendada, horario_inicio, horario_fim, ordem_no_trajeto)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (a["trecho_id"], a["funcionario_id"], data,
             a["horario_inicio"], a["horario_fim"], a["ordem_no_trajeto"]),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Cronograma de {data} salvo: {len(alocacoes)} alocações.")