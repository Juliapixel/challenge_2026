"""
gerar_funcionarios.py — Dados sintéticos de FUNCIONÁRIOS

Este é dado REAL do escopo do projeto (cronograma de funcionários),
não é placeholder. Critérios definidos com o grupo:

- 8 funcionários (Faker, nomes brasileiros)
- Turnos variados: manhã (06h-14h), tarde (14h-22h), comercial (08h-17h)
- Dias variados: maioria seg-sex, alguns seg-sáb
- Velocidade de poda igual para todos (decisão do grupo, por simplicidade)
- Base/garagem: Barueri (sede real da CCR RodoAnel/Motiva) ou Taboão da Serra
- Escopo geográfico: Rodoanel Mário Covas (SP-021), Trecho Oeste, km 0-29
  (região Osasco / Taboão da Serra / Barueri)
"""
import random
from datetime import time
from faker import Faker
from db import conectar

fake = Faker("pt_BR")

N_FUNCIONARIOS = 8

TURNOS = [
    {"nome": "manha", "inicio": time(6, 0), "fim": time(14, 0)},
    {"nome": "tarde", "inicio": time(14, 0), "fim": time(22, 0)},
    {"nome": "comercial", "inicio": time(8, 0), "fim": time(17, 0)},
]

DIAS_TRABALHO_OPCOES = ["seg-sex", "seg-sab"]
DIAS_TRABALHO_PESOS = [70, 30]  # maioria seg-sex, poucos seg-sab

# Bases/garagens (coordenadas aproximadas dentro da região do SP-021 Trecho Oeste)
BASES = [
    {"nome": "Base Barueri", "lat": -23.5305, "lon": -46.8760},
    {"nome": "Base Taboão da Serra", "lat": -23.6094, "lon": -46.7593},
]

VELOCIDADE_PODA_M_POR_MIN = 2.5  # igual para todos os funcionários


def gerar_funcionarios(n=N_FUNCIONARIOS):
    """Gera uma lista de dicts representando funcionários fictícios (dado real do escopo)."""
    funcionarios = []
    for _ in range(n):
        turno = random.choice(TURNOS)
        base = random.choice(BASES)
        dias = random.choices(DIAS_TRABALHO_OPCOES, weights=DIAS_TRABALHO_PESOS)[0]

        funcionarios.append({
            "nome": fake.name(),
            "turno_inicio": turno["inicio"],
            "turno_fim": turno["fim"],
            "dias_trabalho": dias,
            "localizacao_base": base["nome"],
            "latitude_base": base["lat"],
            "longitude_base": base["lon"],
            "velocidade_poda_m_por_min": VELOCIDADE_PODA_M_POR_MIN,
        })
    return funcionarios


def inserir_funcionarios(funcionarios):
    """Insere a lista de funcionários na tabela `funcionarios` do Supabase."""
    conn = conectar()
    cursor = conn.cursor()
    for f in funcionarios:
        cursor.execute(
            """
            INSERT INTO funcionarios
                (nome, turno_inicio, turno_fim, dias_trabalho,
                 localizacao_base, latitude_base, longitude_base,
                 velocidade_poda_m_por_min)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f["nome"], f["turno_inicio"], f["turno_fim"], f["dias_trabalho"],
                f["localizacao_base"], f["latitude_base"], f["longitude_base"],
                f["velocidade_poda_m_por_min"],
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {len(funcionarios)} funcionários inseridos com sucesso no Supabase.")


if __name__ == "__main__":
    dados = gerar_funcionarios()
    print("Funcionários gerados:")
    for f in dados:
        print(f"  - {f['nome']} | turno {f['turno_inicio']}-{f['turno_fim']} | "
              f"{f['dias_trabalho']} | base: {f['localizacao_base']}")

    resposta = input("\nInserir esses dados no Supabase? (s/n): ").strip().lower()
    if resposta == "s":
        inserir_funcionarios(dados)
    else:
        print("Nada foi inserido. Rode novamente quando quiser confirmar.")