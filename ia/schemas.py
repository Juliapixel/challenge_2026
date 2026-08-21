from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
#entradas
class TrechoRodovia(BaseModel):
    trecho_id: str
    rodovia_id: str
    km_inicial: float
    km_final: float 

class HistoricoPoda(BaseModel):
    trecho_id: str
    data_poda: date
    altura_antes_cm: float
    altura_depois_cm: float
    equipamento_usado: Optional[str]= None

class LeituraVegetacao(BaseModel):
    trecho_id: str
    data_leitura: date
    altura_cm: float
    umidade_solo_pct: Optional[float]= None

class PosicaoGeografica(BaseModel):
    trecho_id: str
    latitude: float
    longitude: float
    precipitacao_mm: float
    umidade_relativa_pct: float

class previsaoTempo(BaseModel):
    trecho_id: str 
    data: date 
    temperatura_media_c: float
    precipitacao_mm: float
    umidade_relativa_pct: float

class Funcionario(BaseModel):
    funcionario_id: str
    nome: str
    disponibilidade: list[str]= Field(default_factory=list, description="dias/horários disponíveis")
    base_latitude: Optional[float]= None
    base_longitude: Optional[float]= None

class Avaliacao(BaseModel):
    trecho_id: str
    data_avaliacao: datetime
    previsao_correta: bool
    comentario: Optional[str]= None

#saidas
class PrevisaoProximaPoda(BaseModel):
    trecho_id: str
    data_prevista: date

class Recomendacao(BaseModel):
    trecho_id: str
    taxa_cresc_estimado_cm_dia: float
    horario_corte_recomendado: str
    observacoes_umidade: str

class TarefaCronograma(BaseModel):
    funcionario_id: str
    trecho_id: str
    data: date
    horario_inicio: str
    ordem_na_rota: int