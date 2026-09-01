"""
scheduler.py — Algoritmo guloso de alocação de cronograma (núcleo do trabalho)

Premissas definidas com o grupo:
- Tempo de poda: ~1.5h por km (faixa realista de 1-2h/km), igual para todos os funcionários
- Deslocamento: distância real via Haversine (lat/long), velocidade média 60 km/h
- Prioridade: vermelho > amarelo; dentro do mesmo status, prazo mais próximo primeiro
- Se um trecho não cabe no turno de ninguém hoje, fica pendente para a próxima data
  (não é removido nem marcado como erro — ele continua "amarelo"/"vermelho" no banco)
"""
import math
from datetime import date, datetime, timedelta

VELOCIDADE_DESLOCAMENTO_KMH = 60

PESO_STATUS = {"vermelho": 1000, "amarelo": 500}


def haversine_km(lat1, lon1, lat2, lon2):
    """Distância real em km entre dois pontos geográficos (fórmula de Haversine)."""
    R = 6371  # raio da Terra em km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def calcular_prioridade(trecho):
    """
    Retorna um score numérico de prioridade.
    Status pesa mais que prazo: um 'vermelho' com prazo distante ainda vem
    antes de um 'amarelo' com prazo próximo. Dentro do mesmo status,
    quanto menor o prazo restante, maior o bônus de prioridade.
    """
    peso_status = PESO_STATUS.get(trecho["nivel_urgencia"], 0)

    dias_restantes = (trecho["prazo_limite"] - date.today()).days
    dias_restantes = max(dias_restantes, 0)  # evita bônus absurdo com prazo já vencido
    bonus_prazo = 100 / (dias_restantes + 1)

    return peso_status + bonus_prazo


def calcular_tempo_poda(trecho, funcionario):
    """Tempo de poda = extensão do trecho (m) / velocidade de poda do funcionário (m/hora)."""
    horas = trecho["extensao_m"] / funcionario["velocidade_poda_m_por_hora"]
    return timedelta(seconds=round(horas * 3600))


def calcular_tempo_deslocamento(lat_a, lon_a, lat_b, lon_b,
                                 velocidade_kmh=VELOCIDADE_DESLOCAMENTO_KMH):
    """
    Tempo de deslocamento entre dois pontos, usando distância real (Haversine)
    e velocidade média combinada com o grupo (60 km/h).
    """
    distancia_km = haversine_km(lat_a, lon_a, lat_b, lon_b)
    horas = distancia_km / velocidade_kmh
    return timedelta(seconds=round(horas * 3600))


def alocar_cronograma(trechos, funcionarios, data):
    """
    Algoritmo guloso principal.

    Entrada:
        trechos: lista de dicts (formato de buscar_trechos_pendentes()) —
                 precisa ter: trecho_id, extensao_m, latitude, longitude,
                 nivel_urgencia, prazo_limite
        funcionarios: lista de dicts (formato de buscar_funcionarios_disponiveis()) —
                 precisa ter: id, turno_inicio, turno_fim,
                 latitude_base, longitude_base, velocidade_poda_m_por_hora
        data: date alvo do cronograma

    Saída:
        lista de dicts prontos para salvar_cronograma():
        {trecho_id, funcionario_id, horario_inicio, horario_fim, ordem_no_trajeto}
    """
    trechos_ordenados = sorted(trechos, key=calcular_prioridade, reverse=True)

    # Estado de cada funcionário ao longo do dia: onde está, que horas são, quantos trechos já fez
    estado = {
        f["id"]: {
            "funcionario": f,
            "localizacao": (f["latitude_base"], f["longitude_base"]),
            "horario_atual": datetime.combine(data, f["turno_inicio"]),
            "turno_fim_dt": datetime.combine(data, f["turno_fim"]),
            "ordem_no_trajeto": 0,
        }
        for f in funcionarios
    }

    alocacoes = []
    trechos_nao_alocados = []

    for trecho in trechos_ordenados:
        melhor_funcionario_id = None
        melhor_horario_inicio = None
        melhor_horario_fim = None
        melhor_tempo_total = None

        for f_id, e in estado.items():
            deslocamento = calcular_tempo_deslocamento(
                e["localizacao"][0], e["localizacao"][1],
                trecho["latitude"], trecho["longitude"],
            )
            poda = calcular_tempo_poda(trecho, e["funcionario"])
            tempo_total = deslocamento + poda

            horario_inicio_tentativa = e["horario_atual"] + deslocamento
            horario_fim_tentativa = horario_inicio_tentativa + poda

            # Só considera esse funcionário se ele terminar dentro do próprio turno
            cabe_no_turno = horario_fim_tentativa <= e["turno_fim_dt"]

            if cabe_no_turno and (melhor_tempo_total is None or tempo_total < melhor_tempo_total):
                melhor_funcionario_id = f_id
                melhor_tempo_total = tempo_total
                melhor_horario_inicio = horario_inicio_tentativa
                melhor_horario_fim = horario_fim_tentativa

        if melhor_funcionario_id is not None:
            e = estado[melhor_funcionario_id]
            e["ordem_no_trajeto"] += 1
            e["horario_atual"] = melhor_horario_fim
            e["localizacao"] = (trecho["latitude"], trecho["longitude"])

            alocacoes.append({
                "trecho_id": trecho["trecho_id"],
                "funcionario_id": melhor_funcionario_id,
                "horario_inicio": melhor_horario_inicio.time(),
                "horario_fim": melhor_horario_fim.time(),
                "ordem_no_trajeto": e["ordem_no_trajeto"],
            })
        else:
            trechos_nao_alocados.append(trecho)

    if trechos_nao_alocados:
        print(f"⚠️  {len(trechos_nao_alocados)} trecho(s) não couberam no turno de ninguém "
              f"hoje e ficam pendentes para a próxima data.")

    return alocacoes


# ============================================================
# Teste isolado com dados de mentira (sem precisar do banco)
# Critério de "pronto": rodar este arquivo direto e ver alocações coerentes,
# sem funcionário estourando turno e sem trecho duplicado.
# ============================================================
if __name__ == "__main__":
    hoje = date.today()

    trechos_teste = [
        {"trecho_id": 1, "extensao_m": 1500, "latitude": -23.55, "longitude": -46.78,
         "nivel_urgencia": "vermelho", "prazo_limite": hoje + timedelta(days=2)},
        {"trecho_id": 2, "extensao_m": 800, "latitude": -23.58, "longitude": -46.77,
         "nivel_urgencia": "amarelo", "prazo_limite": hoje + timedelta(days=10)},
        {"trecho_id": 3, "extensao_m": 2000, "latitude": -23.60, "longitude": -46.76,
         "nivel_urgencia": "vermelho", "prazo_limite": hoje + timedelta(days=1)},
        {"trecho_id": 4, "extensao_m": 1200, "latitude": -23.62, "longitude": -46.755,
         "nivel_urgencia": "amarelo", "prazo_limite": hoje + timedelta(days=5)},
    ]

    from datetime import time as time_type
    funcionarios_teste = [
        {"id": 101, "turno_inicio": time_type(8, 0), "turno_fim": time_type(17, 0),
         "latitude_base": -23.5305, "longitude_base": -46.8760,
         "velocidade_poda_m_por_hora": 667},
        {"id": 102, "turno_inicio": time_type(6, 0), "turno_fim": time_type(14, 0),
         "latitude_base": -23.6094, "longitude_base": -46.7593,
         "velocidade_poda_m_por_hora": 667},
    ]

    resultado = alocar_cronograma(trechos_teste, funcionarios_teste, hoje)

    print(f"\n{'=' * 60}\nCRONOGRAMA GERADO PARA {hoje}\n{'=' * 60}")
    for a in resultado:
        print(f"  Funcionário {a['funcionario_id']} | trecho {a['trecho_id']} | "
              f"{a['horario_inicio']} - {a['horario_fim']} | ordem {a['ordem_no_trajeto']}")
    print(f"\nTotal alocado: {len(resultado)} de {len(trechos_teste)} trechos")