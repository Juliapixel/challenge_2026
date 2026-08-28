"""
gerar_dados_fake_temporarios.py — PLACEHOLDER, NÃO É DADO REAL DO PROJETO

⚠️  Este script existe só para você conseguir TESTAR o algoritmo guloso
    antes dos dados reais estarem prontos:
    - `trechos`         -> vai ser preenchido pelo colega responsável pelo trecho da rodovia
    - `previsao_urgencia` -> vai ser preenchido pelo colega do modelo de ML (previsão de poda)

    Quando os dados reais chegarem:
    1. Rode no Supabase: TRUNCATE TABLE previsao_urgencia, trechos CASCADE;
    2. Pare de rodar este script.

Escopo simulado: Rodoanel Mário Covas (SP-021), Trecho Oeste, km 0-29,
região Osasco / Taboão da Serra (mesma faixa usada nas obras reais de manutenção).
"""
import random
from datetime import date, timedelta
from db import conectar

N_TRECHOS_FAKE = 15
KM_TOTAL = 29  # km 0 ao km 29, faixa real de manutenção do SP-021 Trecho Oeste

# Pontos aproximados do trecho (Norte: Osasco/Barueri -> Sul: Taboão da Serra)
PONTO_NORTE = (-23.53, -46.79)
PONTO_SUL = (-23.63, -46.76)

# Status de urgência (semáforo), combinado com o grupo:
#   verde    -> não precisa de poda
#   amarelo  -> atenção, poda deve ser programada
#   vermelho -> poda imediata
#   preto    -> já podado (não entra na fila de otimização)
#
# Distribuição escolhida: cenário crítico, maioria amarelo/vermelho
# (serve pra testar o guloso sob pressão, com bastante trecho disputando funcionário)
NIVEIS_URGENCIA = ["verde", "amarelo", "vermelho", "preto"]
PESOS_URGENCIA = [15, 35, 35, 15]

# Prazo-limite por status (só faz sentido para amarelo/vermelho).
# verde e preto não entram na fila do scheduler, então não têm prazo.
PRAZO_DIAS_POR_NIVEL = {"amarelo": 14, "vermelho": 3}


def interpolar(p1, p2, fracao):
    """Interpola linearmente entre dois pontos (lat, lon) dado uma fração 0-1."""
    lat = p1[0] + (p2[0] - p1[0]) * fracao
    lon = p1[1] + (p2[1] - p1[1]) * fracao
    return lat, lon


def gerar_trechos_fake(n=N_TRECHOS_FAKE):
    """Gera trechos fictícios distribuídos ao longo do km 0-29 do SP-021 Trecho Oeste."""
    trechos = []
    passo = KM_TOTAL / n
    for i in range(n):
        km_inicio = round(i * passo, 2)
        km_fim = round((i + 1) * passo, 2)
        fracao = i / n
        lat, lon = interpolar(PONTO_NORTE, PONTO_SUL, fracao)
        extensao_m = round((km_fim - km_inicio) * 1000, 1)

        trechos.append({
            "km_inicio": km_inicio,
            "km_fim": km_fim,
            "localizacao": f"SP-021 km {km_inicio}-{km_fim}",
            "extensao_m": extensao_m,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
        })
    return trechos


def gerar_previsao_urgencia(trecho_ids):
    """
    Simula a saída do modelo de ML do colega: um status de urgência por trecho.
    verde/preto -> prazo_limite fica NULL (não entram na fila do scheduler)
    amarelo/vermelho -> recebem prazo_limite (usado pelo guloso pra priorizar)
    """
    previsoes = []
    hoje = date.today()
    for trecho_id in trecho_ids:
        status = random.choices(NIVEIS_URGENCIA, weights=PESOS_URGENCIA)[0]
        prazo_dias = PRAZO_DIAS_POR_NIVEL.get(status)  # None para verde/preto
        prazo_limite = hoje + timedelta(days=prazo_dias) if prazo_dias else None

        previsoes.append({
            "trecho_id": trecho_id,
            "data_previsao": hoje,
            "nivel_urgencia": status,
            "prazo_limite": prazo_limite,
        })
    return previsoes


def inserir_trechos(trechos):
    conn = conectar()
    cursor = conn.cursor()
    ids = []
    for t in trechos:
        cursor.execute(
            """
            INSERT INTO trechos (km_inicio, km_fim, localizacao, extensao_m, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (t["km_inicio"], t["km_fim"], t["localizacao"], t["extensao_m"],
             t["latitude"], t["longitude"]),
        )
        ids.append(cursor.fetchone()[0])
    conn.commit()
    cursor.close()
    conn.close()
    print(f"⚠️  {len(trechos)} trechos FAKE inseridos (placeholder).")
    return ids


def inserir_previsoes(previsoes):
    conn = conectar()
    cursor = conn.cursor()
    for p in previsoes:
        cursor.execute(
            """
            INSERT INTO previsao_urgencia (trecho_id, data_previsao, nivel_urgencia, prazo_limite)
            VALUES (%s, %s, %s, %s)
            """,
            (p["trecho_id"], p["data_previsao"], p["nivel_urgencia"], p["prazo_limite"]),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"⚠️  {len(previsoes)} previsões FAKE inseridas (placeholder).")


if __name__ == "__main__":
    print("=" * 60)
    print("⚠️  GERANDO DADOS FAKE/TEMPORÁRIOS (trechos + previsão)")
    print("    Isso NÃO substitui os dados reais que os colegas vão entregar.")
    print("=" * 60)

    resposta = input("\nConfirmar geração de dados fake? (s/n): ").strip().lower()
    if resposta != "s":
        print("Nada foi gerado.")
    else:
        trechos = gerar_trechos_fake()
        ids = inserir_trechos(trechos)
        previsoes = gerar_previsao_urgencia(ids)
        inserir_previsoes(previsoes)