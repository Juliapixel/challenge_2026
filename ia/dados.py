import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

#conf base

#ainda preciso add sobre o id da estaca mas fiquei com preguica, amanha ja vou att 
N_TRECHO = 30
N_FUNCIONARIOS = 20
DATA_INICIO = date(2026, 1, 1)
N_DIAS = 365

CLIMA_PATH = os.path.join(OUTPUT_DIR, "weather.csv")
COORDENADAS_PATH = os.path.join(OUTPUT_DIR, "coordenadas_trechos.csv")

RODOVIAS = [
    {"rodovia_id":"BR-101", "km_total": 300 },
    {"rodovia_id":"SP-330", "km_total": 180 },
]

TAMANHO_TRECHO_KM = 50.0 

TIPOS_VEGETACAO = {
    "lerolerolero": {"taxa_base": 0.15 , "limiar_poda_cm": 30.0 , "altura_pos_poda_cm": 1.0},
    "alguma coisa": {"taxa_base": 0.80 , "limiar_poda_cm": 30.0, "altura_pos_poda_cm":2.0},
    "seila oq": {"taxa_base": 0.40 , "limiar_poda_cm": 600.0, "altura_pos_poda_cm": 2.5},
}


DIAS_SEMANA = ["seg", "ter", "qua", "qui","sex", "sab", "dom"]
TURNOS = ["manha", "tarde"]
JANELA_TAXA_CRESCIMENTO_DIAS = 14  


def exportar_trechos_para_coordenadas(trechos_df):
    """
    gera um CSV incompleto (trecho_id, km_inicial, km_final, latitude, longitude)
    para ser preenchido (visão computacional) e depois consumido
    por weather.py, que espera output/coordenadas_trechos.csv com latitude/longitude.
    """
    dados_inc = trechos_df[["trecho_id", "km_inicial", "km_final"]].copy()
    dados_inc["latitude"] = np.nan
    dados_inc["longitude"] = np.nan
    dados_inc.to_csv(COORDENADAS_PATH, index=False)
    return dados_inc

def carregar_infos_clima(trecho_df):
    if not os.path.exists(CLIMA_PATH):
        raise FileNotFoundError(f"não foi encontrado: {CLIMA_PATH}")

    clima_df = pd.read_csv(CLIMA_PATH, parse_dates=["data"])
    clima_df = clima_df[clima_df["trecho_id"].isin(trecho_df["trecho_id"])]
    return clima_df

def gerar_trechos():
    trechos = []
    for rod in RODOVIAS:
        n_trechos = int(np.ceil(rod["km_total"] / TAMANHO_TRECHO_KM))
        for i in range(n_trechos):
            km_inicial = i * TAMANHO_TRECHO_KM
            km_final = min((i + 1) * TAMANHO_TRECHO_KM, rod["km_total"])
            
            trechos.append({
                "trecho_id": f"{rod['rodovia_id']}_km{int(km_inicial):03d}_km{int(km_final):03d}",
                "rodovia_id": rod["rodovia_id"],
                "km_inicial": km_inicial,
                "km_final": km_final,
                "tipo_vegetacao": random.choice(list(TIPOS_VEGETACAO.keys())),
            })
    return pd.DataFrame(trechos)


def _perfil_crescimento_oculto(trecho_id):

    rng = np.random.RandomState(abs(hash(trecho_id)) % (2**32))
    taxa_base = rng.uniform(0.20, 0.45)       # cm/dia em condição neutra (fonte: vozes da minha cabeça)
    limiar_poda_cm = rng.uniform(8.0, 15.0)
    altura_pos_poda_cm = rng.uniform(3.0, 6.0)
    return taxa_base, limiar_poda_cm, altura_pos_poda_cm

def simular_crescimento_e_poda(trechos_df,clima_df):
    leituras = []
    podas = []

    clima_por_trecho = {t: df.sort_values("data").reset_index(drop=True)
                            for t, df in clima_df.groupby("trecho_id")}

    for _, trecho in trechos_df.iterrows():
        taxa_base, limiar_poda_cm, altura_pos_poda_cm = _perfil_crescimento_oculto(trecho["trecho_id"])
        clima_trecho = clima_por_trecho[trecho["trecho_id"]]

        altura_atual = altura_pos_poda_cm + np.random.uniform(0, 2)
        umidade_solo = 50.0
        historico_alturas = []  # pra calcular a taxa de crescimento observada

        for _, dia_clima in clima_trecho.iterrows():
            fator_temp = 1.0 - abs(dia_clima["temperatura_media_c"] - 23) / 20
            fator_temp = max(fator_temp, 0.2)
            fator_chuva = 1.0 + min(dia_clima["precipitacao_mm"] / 20, 0.6)

            crescimento_dia = taxa_base * fator_temp * fator_chuva
            crescimento_dia += np.random.normal(0, 0.02)
            altura_atual = max(altura_atual + crescimento_dia, 0)

            umidade_solo = np.clip(
                umidade_solo * 0.9 + dia_clima["precipitacao_mm"] * 1.5, 10, 100
            )

            historico_alturas.append(altura_atual)
            janela = historico_alturas[-JANELA_TAXA_CRESCIMENTO_DIAS:]
            # taxa de crescimento  nos últimos N dias (feature)
            if len(janela) >= 2:
                taxa_observada = (janela[-1] - janela[0]) / (len(janela) - 1)
            else:
                taxa_observada = 0.0

            leituras.append({
                "trecho_id": trecho["trecho_id"],
                "data_leitura": dia_clima["data"],
                "altura_cm": round(altura_atual, 2),
                "umidade_solo_pct": round(umidade_solo, 1),
                "taxa_crescimento_estimada_cm_dia": round(taxa_observada, 3),
            })

            if altura_atual >= limiar_poda_cm:
                podas.append({
                    "trecho_id": trecho["trecho_id"],
                    "data_poda": dia_clima["data"],
                    "altura_antes_cm": round(altura_atual, 2),
                    "altura_depois_cm": round(altura_pos_poda_cm, 2),
                    "equipamento_usado": random.choice(["roçadeira", "trator_corte", "roçadeira_costal"]),
                })
                altura_atual = altura_pos_poda_cm
                historico_alturas = []  # reinicia a janela após a poda

    return pd.DataFrame(leituras), pd.DataFrame(podas)

#funcionarios

def gerar_funcionarios():
    funcionarios = []
    for i in range(N_FUNCIONARIOS):
        disponibilidade = []
        for dia in DIAS_SEMANA[:5]:
            for turno in TURNOS:
                if random.random() < 0.8:
                    disponibilidade.append(f"{dia}-{turno}")
        if random.random() < 0.3:
            disponibilidade.append("sab-manha")

        funcionarios.append({
            "funcionario_id": f"func_{i:03d}",
            "nome": f"Funcionário {i+1}",
            "disponibilidade": ";".join(disponibilidade),
        })
    return pd.DataFrame(funcionarios)



def main():
    trechos_df = gerar_trechos()
    trechos_df.to_csv(os.path.join(OUTPUT_DIR, "trechos_rodovia.csv"), index=False)

    if not os.path.exists(COORDENADAS_PATH):
        exportar_trechos_para_coordenadas(trechos_df)
        print(
            f"Gerei {COORDENADAS_PATH} sem latitude/longitude preenchidas. "
            " Depois que a visao computacional compartilhar esses dados com essa parte , depois rode weather.py "
            "e execute este script novamente para testar "
        )
        return

    clima_df = carregar_infos_clima(trechos_df)
    leituras_df, podas_df = simular_crescimento_e_poda(trechos_df, clima_df)
    funcionarios_df = gerar_funcionarios()

    clima_df.to_csv(os.path.join(OUTPUT_DIR, "clima.csv"), index=False)
    leituras_df.to_csv(os.path.join(OUTPUT_DIR, "leituras.csv"), index=False)
    podas_df.to_csv(os.path.join(OUTPUT_DIR, "historico_poda.csv"), index=False)
    funcionarios_df.to_csv(os.path.join(OUTPUT_DIR, "funcionarios.csv"), index=False)
    print(f"OK: {len(trechos_df)} trechos, {len(leituras_df)} leituras, {len(podas_df)} podas")

if __name__ == "__main__":
    main()
