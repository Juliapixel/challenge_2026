# Cronograma de Podas — Motiva (Módulo de IA)

Este módulo resolve um problema de **otimização combinatória**: dado um conjunto de trechos
de rodovia que precisam de poda (com nível de urgência) e um conjunto de funcionários
disponíveis (com turnos e localização), sugerir automaticamente **quem poda o quê, onde e
em que horário**, otimizando prioridade e deslocamento.

📊 **Banco de dados (Supabase):** mandei no email
---

## Contexto do problema

- Rodovia simulada: **SP-021 (Rodoanel Mário Covas), Trecho Oeste**, km 0-29, região
  Osasco / Taboão da Serra / Barueri — trecho real operado pela Motiva (CCR RodoAnel).
- Cada trecho tem um **status de urgência** (semáforo):
  - 🟢 `verde` — não precisa de poda
  - 🟡 `amarelo` — atenção, entra na fila
  - 🔴 `vermelho` — poda imediata, prioridade máxima
  - ⚫ `preto` — já foi podado
- Cada funcionário tem turno, dias de trabalho e uma base/garagem (lat/long) de onde parte.
- **Restrição central:** nem tudo pode ser podado no mesmo dia — depende da mão de obra
  disponível e de quanto tempo cada poda leva.

---

## Arquitetura

```
[Supabase / PostgreSQL]  (tabelas: funcionarios, trechos, previsao_urgencia, cronograma_sugerido)
        │
        ▼
   db.py            → toda leitura/escrita no banco
        │
        ▼
   scheduler.py      → algoritmo guloso: decide quem poda o quê, quando
        │
        ▼
   main.py           → orquestra tudo: busca dados → aloca → salva → imprime resumo
```

Módulos auxiliares (geração de dados de teste):
- `gerar_funcionarios.py` — dados **reais** do escopo (funcionários fictícios, mas é o
  dado de verdade do projeto)
- `gerar_dados_fake_temporarios.py` — dados **placeholder** de trechos e previsão de
  urgência, usados só até os colegas (rodovia + modelo de previsão) entregarem os dados reais

---

## Como o algoritmo decide (resumo da lógica)

1. Ordena os trechos pendentes por prioridade: `vermelho` sempre antes de `amarelo`;
   dentro do mesmo status, prazo mais apertado primeiro.
2. Para cada trecho, testa todos os funcionários disponíveis naquele dia e calcula quanto
   tempo cada um levaria (deslocamento real via fórmula de Haversine + tempo de poda).
3. Aloca ao funcionário que **termina mais rápido** aquele serviço — isso já favorece
   quem está fisicamente mais perto, sem precisar de uma regra separada de distância.
4. Se um trecho não cabe no turno de ninguém, ele fica pendente pra próxima data
   (continua `amarelo`/`vermelho` no banco, não é descartado).

**Premissas assumidas** (documentar no relatório):
- Tempo de poda: ~1,5h por km (faixa realista de 1-2h/km), igual para todos os funcionários
- Velocidade média de deslocamento: 60 km/h
- Distância entre pontos: real, via lat/long (Haversine) — não é aproximação por km

---

## Estrutura das tabelas (Supabase)

| Tabela | O que guarda | Quem popula |
|---|---|---|
| `funcionarios` | Dados reais/sintéticos da equipe (turno, base, velocidade de poda) | Este módulo |
| `trechos` | Segmentos da rodovia (km, lat/long, extensão) | Colega responsável pela malha viária |
| `previsao_urgencia` | Status de urgência por trecho (saída do modelo de ML) | Colega do módulo de previsão |
| `cronograma_sugerido` | **Saída deste módulo** — a alocação final | Este módulo |

> Os scripts de migração (`migracao_*.sql`) documentam as mudanças de schema feitas ao
> longo do desenvolvimento — rode-os na ordem cronológica se for recriar o banco do zero.

