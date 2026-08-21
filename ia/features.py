
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_OUT = os.path.join(BASE_DIR, "data", "output")
FEATURES_OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(FEATURES_OUT, exist_ok=True)

JANELA_CLIMA_DIAS = 7
JANELA_CRESCIMENTO_LEITURAS = 5  # nº de leituras passadas usadas pra estimar a taxa (reduz ruído)


def classificar_risco(dias_ate_poda):
    if dias_ate_poda <= 7:
        return "critico"
    elif dias_ate_poda <= 14:
        return "alto"
    elif dias_ate_poda <= 30:
        return "medio"
    else:
        return "baixo"


def main():
    try:
        leituras = pd.read_csv(os.path.join(DATA_OUT, "leituras.csv"), parse_dates=["data_leitura"])
        podas = pd.read_csv(os.path.join(DATA_OUT, "historico_poda.csv"), parse_dates=["data_poda"])
        clima = pd.read_csv(os.path.join(DATA_OUT, "clima.csv"), parse_dates=["data"])
    except:
        raise FileNotFoundError("Não foi possível encontrar os arquivos de entrada em data/output. "
                                "Execute o script gerar_dados.py antes de gerar as features.")
    leituras = leituras.sort_values(["trecho_id", "data_leitura"]).reset_index(drop=True)
    clima = clima.sort_values(["trecho_id", "data"]).reset_index(drop=True)

    linhas = []

    for trecho_id, grupo in leituras.groupby("trecho_id"):
        grupo = grupo.reset_index(drop=True)
        podas_trecho = podas[podas["trecho_id"] == trecho_id].sort_values("data_poda")
        clima_trecho = clima[clima["trecho_id"] == trecho_id].set_index("data")

        historico_janela = []  # lista de (data, altura) só com leituras JÁ VISTAS (passado)

        for i, leitura in grupo.iterrows():
            data_ref = leitura["data_leitura"]

            janela = historico_janela[-JANELA_CRESCIMENTO_LEITURAS:]
            if len(janela) >= 2:
                dias_rel = np.array([(d - janela[0][0]).days for d, _ in janela])
                alturas_janela = np.array([a for _, a in janela])
                taxa_recente = np.polyfit(dias_rel, alturas_janela, 1)[0]
            else:
                taxa_recente = np.nan  # histórico insuficiente ainda


            podas_passadas = podas_trecho[podas_trecho["data_poda"] < data_ref]
            if len(podas_passadas) > 0:
                dias_desde_poda = (data_ref - podas_passadas["data_poda"].max()).days
            else:
                dias_desde_poda = (data_ref - grupo["data_leitura"].min()).days

            janela_clima = clima_trecho.loc[
                (clima_trecho.index <= data_ref) &
                (clima_trecho.index > data_ref - pd.Timedelta(days=JANELA_CLIMA_DIAS))
            ]
            chuva_acumulada_7d = janela_clima["precipitacao_mm"].sum() if len(janela_clima) else np.nan
            temp_media_7d = janela_clima["temperatura_media_c"].mean() if len(janela_clima) else np.nan

            
            podas_futuras = podas_trecho[podas_trecho["data_poda"] > data_ref]
            if len(podas_futuras) > 0:
                proxima_poda = podas_futuras["data_poda"].min()
                dias_ate_proxima_poda = (proxima_poda - data_ref).days
            else:
                dias_ate_proxima_poda = np.nan  # censurado (fim dos dados) -> descartar depois

            linhas.append({
                "trecho_id": trecho_id,
                "data_referencia": data_ref,
                "altura_cm": leitura["altura_cm"],
                "umidade_solo_pct": leitura["umidade_solo_pct"],
                "taxa_crescimento_recente_cm_dia": taxa_recente,
                "dias_desde_ultima_poda": dias_desde_poda,
                "chuva_acumulada_7d_mm": chuva_acumulada_7d,
                "temp_media_7d_c": temp_media_7d,
                "dias_ate_proxima_poda": dias_ate_proxima_poda,
            })
            historico_janela.append((data_ref, leitura["altura_cm"]))

    df = pd.DataFrame(linhas)

    n_total = len(df)
    n_censurado = df["dias_ate_proxima_poda"].isna().sum()
    n_sem_historico = df["taxa_crescimento_recente_cm_dia"].isna().sum()

    df = df.dropna(subset=["dias_ate_proxima_poda", "taxa_crescimento_recente_cm_dia"]).copy()
    df["risco_classe"] = df["dias_ate_proxima_poda"].apply(classificar_risco)

    df.to_csv(os.path.join(FEATURES_OUT, "dataset_features.csv"), index=False)

    print(f"Total de leituras processadas: {n_total}")
    print(f"  Descartadas por censura (sem poda futura nos dados): {n_censurado}")
    print(f"  Descartadas por falta de histórico anterior: {n_sem_historico}")
    print(f"Dataset final: {len(df)} linhas")
    print(df["risco_classe"].value_counts())


if __name__ == "__main__":
    
    main()