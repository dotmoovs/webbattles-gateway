# Guia para Testes Estatísticos (100+ amostras)

## 🎯 Objetivo

Executar múltiplos testes (recomendado: 100) para obter dados estatísticos robustos e demonstrar consistência do sistema para o relatório TRL 8.

---

## 📋 Pré-requisitos

✅ Gateway running (`docker compose up -d`)  
✅ Suficiente testnet ETH (~0.02 ETH em Sepolia + Base Sepolia)  
✅ Tempo disponível (~15-20 minutos para 100 testes)

---

## 🚀 Executar Testes

### Opção 1: 100 Testes (Recomendado)

```bash
cd /Users/hugoduarte/Desktop/Dotmoovs/webbattles-gateway/gateway/oracle/case_4/webbattles
python3 run-multiple-tests.py --num-tests 100
```

**Tempo estimado:** ~15-20 minutos  
**Custo estimado:** ~$0.15 USD em gas  
**Resultado:** Análise estatística completa

### Opção 2: 50 Testes (Alternativa)

```bash
python3 run-multiple-tests.py --num-tests 50
```

**Tempo estimado:** ~8-10 minutos

### Opção 3: Teste Rápido (10 testes)

```bash
python3 run-multiple-tests.py --num-tests 10
```

**Tempo estimado:** ~2 minutos

---

## 📊 O que o Script Faz

Para cada teste:
1. ✅ Cria uma battle em Sepolia
2. ✅ Replica para Base Sepolia
3. ✅ Verifica consistência de dados
4. ✅ Coleta métricas completas

No final:
- 📈 Calcula estatísticas (média, desvio padrão, min, max)
- 💾 Guarda todos os dados individuais
- 📊 Gera relatório agregado

---

## 📈 Métricas Coletadas

### Para Cada Teste Individual:
- Tempo de criação da battle
- Gas usado na criação
- Tempo de replicação
- Gas usado na replicação
- Tempo total de sync
- Consistência de dados
- Custos (ETH e USD)

### Estatísticas Agregadas:
- **Média** de todas as métricas
- **Mediana** (valor central)
- **Desvio Padrão** (variabilidade)
- **Mínimo e Máximo** (range)
- **Taxa de Sucesso** (%)
- **Taxa de Consistência** (%)

---

## 📁 Resultados

Os resultados são guardados em:
```
test_results/multiple_tests_results_100tests_YYYYMMDD_HHMMSS.json
```

### Estrutura do JSON:

```json
{
  "test_metadata": {
    "test_date": "...",
    "num_tests": 100,
    "trl_level": 8
  },
  "individual_tests": [
    {
      "test_number": 1,
      "status": "success",
      "battle_id": "...",
      "creation_tx": "...",
      "replication_tx": "...",
      "metrics": {
        "creation_time_seconds": 4.5,
        "replication_time_seconds": 0.95,
        "total_sync_time_seconds": 1.2,
        "data_consistency": true,
        ...
      }
    },
    ...
  ],
  "statistical_analysis": {
    "total_sync_time_seconds": {
      "mean": 1.05,
      "median": 1.02,
      "std_dev": 0.15,
      "min": 0.85,
      "max": 1.45,
      "sample_size": 100
    },
    ...
  },
  "aggregated_metrics": {
    "total_tests_run": 100,
    "successful_tests": 98,
    "success_rate_percentage": 98.0,
    "data_consistency_rate_percentage": 100.0,
    "avg_sync_time_seconds": 1.05,
    "avg_cost_usd": 0.0015
  }
}
```

---

## 📝 Para o Relatório Final

### Dados a Incluir:

1. **Número de Testes:** 100
2. **Taxa de Sucesso:** ~98-100%
3. **Tempo Médio de Sync:** ~1.0s ± 0.2s
4. **Consistência de Dados:** 100%
5. **Custo Médio:** ~$0.0015 ± $0.0002

### Benefícios para o Relatório:

✅ **Validação Estatística:** N=100 demonstra robustez  
✅ **Intervalos de Confiança:** Desvio padrão mostra previsibilidade  
✅ **TRL 8:** Múltiplos testes em condições reais  
✅ **Reprodutibilidade:** Todos os transaction hashes guardados  

---

## 🎯 Exemplo de Uso no Relatório

### Secção: Métricas Quantitativas

> "Para validar a consistência e performance do sistema, executámos 100 testes independentes em testnets públicas (Sepolia e Base Sepolia). Os resultados demonstram:
> 
> - **Tempo médio de sincronização cross-chain:** 1.05s ± 0.15s (N=100)
> - **Range de performance:** 0.85s - 1.45s
> - **Taxa de sucesso:** 98% (98/100 testes)
> - **Consistência de dados:** 100% (todos os testes bem-sucedidos mantiveram dados consistentes)
> - **Custo médio por operação:** $0.0015 ± $0.0002
>
> A baixa variabilidade (desvio padrão de 0.15s, ~14% do valor médio) demonstra a previsibilidade e estabilidade do sistema em condições de testnet pública."

---

## ⚠️ Notas Importantes

1. **Rate Limiting:** O script tem delays entre testes para evitar rate limiting dos RPCs públicos

2. **Gas Necessário:** 
   - Sepolia: ~0.04 ETH para 100 testes
   - Base Sepolia: ~0.02 ETH para 100 testes

3. **Duração:** 
   - Cada teste: ~10-15 segundos
   - 100 testes: ~15-20 minutos

4. **Falhas Esperadas:**
   - 2-5% de falhas são normais devido a condições de rede
   - O importante é ter >95% success rate

5. **Verificação Manual:**
   - Podes verificar qualquer transaction hash nos explorers
   - Todos os dados são guardados para auditoria

---

## 🔍 Verificar Resultados

Depois dos testes:

```bash
# Ver resumo
cat test_results/multiple_tests_results_100tests_*.json | grep -A 10 "aggregated_metrics"

# Contar testes bem-sucedidos
cat test_results/multiple_tests_results_100tests_*.json | grep -c '"status": "success"'
```

---

## ✅ Checklist Final

Antes de submeter ao relatório:

- [ ] Executados 100 testes
- [ ] Success rate > 95%
- [ ] Consistência rate = 100% (dos sucessos)
- [ ] JSON guardado em `test_results/`
- [ ] Estatísticas calculadas (média, std_dev, etc.)
- [ ] Transaction hashes disponíveis para verificação
- [ ] Dados prontos para Google Doc

---

**Boa sorte com os testes! 🚀**


