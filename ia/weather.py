import openmeteo_requests

import os
import time
import pandas as pd
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
#dados que precisam ser fornecidos pela visao computacional 
COORDENADAS_PATH = os.path.join(OUTPUT_DIR, "coordenadas_trechos.csv")


url = "https://archive-api.open-meteo.com/v1/archive"
DATA_INICIO= "2010-08-18"
DATA_FIM = "2026-08-16"


def buscar_clima_trecho(lat,lon,data_inicio , data_fim):

    params = {
	"latitude": lat, 
	"longitude": lon,
	"start_date": data_inicio,
	"end_date": data_fim,
	"daily": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "soil_moisture_7_to_28cm"],
	"timezone": "auto",
}

    resp = retry_session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    dados = resp.json()["daily"]
    return pd.DataFrame({
        "data": dados["time"],
        "temperatura_media_c": dados["temperature_2m"],
        "precipitacao_mm": dados["precipitation"],
        "umidade_relativa_pct": dados["relative_humidity_2m"],
    })


def main():
    if not os.path.exists(COORDENADAS_PATH):
        raise FileNotFoundError(f"não foi encontrado: {COORDENADAS_PATH}")


    coordenadas_df = pd.read_csv(COORDENADAS_PATH)
    registros = []
    for _, linha in coordenadas_df.iterrows():
        trecho_id = linha["trecho_id"]
        lat, lon = linha["latitude"], linha["longitude"]
        print(f"buscando clima do trecho {trecho_id} (lat={lat}, lon={lon})")

        clima_trecho = buscar_clima_trecho(lat, lon, DATA_INICIO, DATA_FIM)
        clima_trecho["trecho_id"] = trecho_id
        registros.append(clima_trecho)

        time.sleep(1)

    clima_df = pd.concat(registros, ignore_index=True)
    clima_df = clima_df[["trecho_id","data", "temperatura_media_c", "precipitacao_mm", "umidade_relativa_pct"]]
    clima_df.to_csv(os.path.join(OUTPUT_DIR, "weather.csv"), index=False)
    print(f"\n Csv gerado com sucesso. Arquivo salvo em {OUTPUT_DIR}/weather.csv")

if __name__ == "__main__":
    main()