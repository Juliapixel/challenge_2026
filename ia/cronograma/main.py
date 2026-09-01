"""
main.py — Orquestração ponta a ponta (Fase 4)

Fluxo:
    1. Busca trechos pendentes (amarelo/vermelho) no Supabase
    2. Busca funcionários disponíveis na data alvo
    3. Roda o algoritmo guloso (scheduler.py)
    4. Salva o cronograma resultante em cronograma_sugerido (sobrescrevendo a data)

Uso:
    python main.py                # gera o cronograma de hoje
    python main.py 2026-09-05     # gera o cronograma de uma data específica
"""
import sys
from datetime import date, datetime

import db
import scheduler


def gerar_cronograma_do_dia(data):
    """Executa o pipeline completo e retorna a lista de alocações geradas."""
    trechos = db.buscar_trechos_pendentes()
    funcionarios = db.buscar_funcionarios_disponiveis(data)

    if not trechos:
        print("Nenhum trecho pendente (amarelo/vermelho) encontrado. Nada a agendar.")
        return []

    if not funcionarios:
        print(f"Nenhum funcionário disponível em {data}. Nada a agendar.")
        return []

    alocacoes = scheduler.alocar_cronograma(trechos, funcionarios, data)
    db.salvar_cronograma(alocacoes, data)

    _imprimir_resumo(alocacoes, trechos, funcionarios, data)
    return alocacoes


def _imprimir_resumo(alocacoes, trechos, funcionarios, data):
    """Imprime o cronograma de forma legível: 'funcionário X poda trecho Y às Z horas'."""
    # Lookups rápidos pra não precisar consultar o banco de novo só pra exibir nomes
    trechos_por_id = {t["trecho_id"]: t for t in trechos}
    funcionarios_por_id = {f["id"]: f for f in funcionarios}

    print(f"\n{'=' * 70}")
    print(f"CRONOGRAMA SUGERIDO — {data}")
    print(f"{'=' * 70}")

    if not alocacoes:
        print("Nenhuma alocação foi gerada (nenhum trecho coube no turno de ninguém).")
        return

    # Agrupa por funcionário e ordena pela ordem no trajeto, pra ler como uma rota do dia
    por_funcionario = {}
    for a in alocacoes:
        por_funcionario.setdefault(a["funcionario_id"], []).append(a)

    for f_id, lista in por_funcionario.items():
        funcionario = funcionarios_por_id[f_id]
        lista.sort(key=lambda a: a["ordem_no_trajeto"])
        print(f"\n{funcionario['nome']} (turno {funcionario['turno_inicio']}-{funcionario['turno_fim']}):")
        for a in lista:
            trecho = trechos_por_id[a["trecho_id"]]
            print(f"  {a['ordem_no_trajeto']}. Poda trecho {a['trecho_id']} "
                  f"({trecho['localizacao']}) às {a['horario_inicio']} "
                  f"[{trecho['nivel_urgencia']}] — término previsto {a['horario_fim']}")

    print(f"\n{'-' * 70}")
    print(f"Total alocado: {len(alocacoes)} de {len(trechos)} trechos pendentes")
    nao_alocados = len(trechos) - len(alocacoes)
    if nao_alocados > 0:
        print(f"⚠️  {nao_alocados} trecho(s) ficaram pendentes para a próxima data.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_alvo = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        data_alvo = date.today()

    gerar_cronograma_do_dia(data_alvo)