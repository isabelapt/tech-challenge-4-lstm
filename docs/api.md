# 🔌 Guia da API REST - LSTM Stock Prediction

> 📚 **Navegação:** [← Voltar para README](../README.md) | [📖 Ver Índice de Docs](README.md) | [🧠 Ver Modelo LSTM](model.md)

A API FastAPI expõe o modelo LSTM para previsão do próximo preço de fechamento de ações.

**📖 Documentos Relacionados:**
- [Modelo LSTM - Especificação Técnica](model.md) - Detalhes da arquitetura e treinamento
- [README Principal](../README.md) - Visão geral do projeto
- [Índice de Documentação](README.md) - Todos os documentos

---

## 🚀 Inicialização

### Pré-requisitos

Certifique-se que os artefatos treinados estão em `models/`:
- `models/lstm_model.keras` - Modelo LSTM treinado
- `models/scaler.pkl` - MinMaxScaler para normalização

> 💡 **Não tem os artefatos?** Ver [Model - Como Treinar](model.md#🎯-treinamento-via-notebook)

### Rodar Localmente

```bash
# Opção 1: Via Makefile
make run-local

# Opção 2: Via Poetry
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Rodar com Docker

```bash
make docker-build
make docker-run
```

Acesse: http://localhost:8000

---

## 📡 Endpoints

### `GET /` - Health Check

Verifica se a API está rodando.

**Resposta:**
```json
{
  "status": "ok",
  "model": "LSTM V1.20260108",
  "message": "API LSTM rodando! Use /predict"
}
```

---

### `POST /predict` - Previsão de Preço

Retorna a previsão do próximo preço de fechamento com base nos últimos 60 dias de dados OHLCV.

#### 📥 Formato de Requisição

```json
{
  "last_60_days": [
    [open1, high1, low1, close1, volume1, adj_close1],
    [open2, high2, low2, close2, volume2, adj_close2],
    ...
    [open60, high60, low60, close60, volume60, adj_close60]
  ]
}
```

**Especificações:**
- **Exatamente 60 dias** de dados históricos
- Cada dia contém **6 features** (na ordem):
  1. `Open` - Preço de abertura ($)
  2. `High` - Preço máximo do dia ($)
  3. `Low` - Preço mínimo do dia ($)
  4. `Close` - Preço de fechamento ($)
  5. `Volume` - Volume negociado
  6. `Adj Close` - Preço de fechamento ajustado ($)

#### 📤 Formato de Resposta

```json
{
  "prediction": 245.67
}
```

---

## 🧪 Exemplos de Uso

### Exemplo 1: Python com yfinance (Recomendado)

```python
import requests
import yfinance as yf

# Baixar dados históricos
df = yf.download('AAPL', period='3mo', progress=False, auto_adjust=False)

# Preparar últimos 60 dias
last_60 = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']].tail(60)

# Fazer requisição
payload = {"last_60_days": last_60.values.tolist()}
response = requests.post("http://localhost:8000/predict", json=payload)

print(f"Previsão para AAPL: ${response.json()['prediction']:.2f}")
```

### Exemplo 2: cURL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "last_60_days": [
      [100.5, 102.3, 100.1, 101.8, 50000000, 101.8],
      [101.9, 103.5, 101.5, 102.3, 52000000, 102.3],
      ...
      [105.2, 106.8, 104.9, 106.5, 48000000, 106.5]
    ]
  }'
```

### Exemplo 3: JavaScript/Node.js

```javascript
const axios = require('axios');
const yf = require('yahoo-finance2').default;

async function predictStock(symbol) {
  // Baixar dados
  const data = await yf.historical(symbol, {
    period1: '2023-10-01',
    interval: '1d'
  });
  
  // Preparar últimos 60 dias
  const last60 = data.slice(-60).map(d => [
    d.open, d.high, d.low, d.close, d.volume, d.adjClose
  ]);
  
  // Fazer previsão
  const response = await axios.post('http://localhost:8000/predict', {
    last_60_days: last60
  });
  
  console.log(`Previsão: $${response.data.prediction.toFixed(2)}`);
}

predictStock('AAPL');
```

---

## 🧰 Script de Teste Pronto

O repositório inclui um script de teste completo:

```bash
# Testar a API com dados reais da AAPL
make test-api

# Ou diretamente
poetry run python src/scripts/teste_local.py
```

**Para testar outras ações**, edite `src/scripts/teste_local.py` linha 6:
```python
SYMBOL = 'TSLA'  # AAPL, PETR4.SA, MSFT, etc.
```

---

## ⚠️ Notas Importantes

1. **Ordem das Features**: As 6 features devem estar na ordem exata: `[Open, High, Low, Close, Volume, Adj Close]`

2. **Normalização**: A API aplica automaticamente o MinMaxScaler treinado. **NÃO normalize os dados antes de enviar!**

3. **Dados Faltantes**: Se usar yfinance, sempre use `auto_adjust=False` para garantir que `Adj Close` seja retornado:
   ```python
   df = yf.download('AAPL', period='3mo', auto_adjust=False)
   ```

4. **Volume**: Alguns APIs retornam volume como inteiro grande. Certifique-se que é um número válido (não NaN).

5. **Performance**: A primeira previsão após iniciar a API pode demorar ~2-5s (carregamento do modelo). Previsões subsequentes são instantâneas (~100ms).

---

## 🐛 Troubleshooting

### Erro: "Connection refused"
- **Causa**: API não está rodando
- **Solução**: Execute `make run-local` em outro terminal

### Erro: "Forneça exatamente 60 dias de dados"
- **Causa**: Array tem mais ou menos que 60 elementos
- **Solução**: Use `.tail(60)` ao preparar os dados

### Erro: "Cada dia deve conter 6 features"
- **Causa**: Algum dia no array tem mais ou menos que 6 valores
- **Solução**: Verifique se todas as colunas estão presentes: `['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']`

### Previsão parece incorreta
- **Causa**: Ordem errada das features ou dados normalizados
- **Solução**: Use dados brutos (sem normalização) e ordem correta

---

## 📊 Métricas do Modelo

O modelo atual (V1.20260108) possui as seguintes métricas:

- **R² Treino**: 99.28%
- **R² Validação**: 93.31%
- **R² Teste**: 85.19%
- **MAE Teste**: $9.15
- **MAPE**: 3.84%

Treinado com dados de **AAPL (2018-2025)** usando arquitetura LSTM [100, 50] unidades.

---

## 🔄 Fluxo de Dados

```
┌─────────────────┐
│  Cliente envia  │
│   60 dias de    │──┐
│  dados OHLCV    │  │
└─────────────────┘  │
                     ▼
              ┌─────────────────┐
              │  API recebe e   │
              │    valida:      │
              │  - 60 dias?     │
              │  - 6 features?  │
              └─────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │  MinMaxScaler   │
              │   normaliza     │
              │   (0, 1)        │
              └─────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │  Reshape para   │
              │  (1, 60, 6)     │
              └─────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │   Modelo LSTM   │
              │   prediz Close  │
              │   normalizado   │
              └─────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │  Denormaliza    │
              │  usando scaler  │
              └─────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │   Retorna $$$   │
              │  (próximo dia)  │
              └─────────────────┘
```

---

## 📋 Tabela de Códigos HTTP

| Código | Descrição | Solução |
|--------|-----------|---------|
| `200` | ✅ Sucesso | Previsão retornada com sucesso |
| `400` | ❌ Dados inválidos | Verifique se tem exatamente 60 dias com 6 features cada |
| `422` | ❌ Erro de validação | Formato JSON incorreto ou tipos de dados errados |
| `500` | ❌ Erro interno | Problema com modelo ou scaler, verifique logs |

---

## 🎯 Exemplo de Erro Detalhado

### Requisição Incorreta (faltando dias)
```json
{
  "last_60_days": [[100, 101, 99, 100.5, 1000000, 100.5]]  // Apenas 1 dia!
}
```

**Resposta (400):**
```json
{
  "detail": "Forneça exatamente 60 dias de dados."
}
```

### Requisição Incorreta (features erradas)
```json
{
  "last_60_days": [
    [100, 101, 99, 100.5],  // Faltam Volume e Adj Close!
    ...
  ]
}
```

**Resposta (400):**
```json
{
  "detail": "Cada dia deve conter 6 features: [Open, High, Low, Close, Volume, Adj Close]"
}
```

---

## 💡 Dicas Avançadas

### 1. Tratamento de Dados Faltantes

```python
import yfinance as yf
import pandas as pd

df = yf.download('AAPL', period='3mo', auto_adjust=False)

# Verificar dados faltantes
if df.isnull().any().any():
    print("⚠️  Dados faltantes detectados!")
    df = df.fillna(method='ffill')  # Forward fill

# Garantir 60 dias válidos
if len(df) < 60:
    raise ValueError(f"Apenas {len(df)} dias disponíveis")

last_60 = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']].tail(60)
```

### 2. Validação Antes de Enviar

```python
def validate_data(data):
    """Valida dados antes de enviar para API"""
    assert len(data) == 60, f"Esperado 60 dias, recebido {len(data)}"
    
    for i, day in enumerate(data):
        assert len(day) == 6, f"Dia {i}: esperado 6 features, recebido {len(day)}"
        assert all(isinstance(x, (int, float)) for x in day), f"Dia {i}: valores não numéricos"
        assert day[4] >= 0, f"Dia {i}: volume negativo"
    
    return True

# Usar
try:
    validate_data(payload['last_60_days'])
    response = requests.post(url, json=payload)
except AssertionError as e:
    print(f"❌ Erro de validação: {e}")
```

### 3. Retry com Backoff Exponencial

```python
import time

def predict_with_retry(payload, max_retries=3):
    """Tenta fazer previsão com retry automático"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"Tentativa {attempt + 1} falhou, aguardando {wait}s...")
                time.sleep(wait)
            else:
                raise
```

### 4. Batch Predictions (múltiplas ações)

```python
symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']
predictions = {}

for symbol in symbols:
    df = yf.download(symbol, period='3mo', auto_adjust=False, progress=False)
    last_60 = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']].tail(60)
    
    response = requests.post(
        "http://localhost:8000/predict",
        json={"last_60_days": last_60.values.tolist()}
    )
    
    predictions[symbol] = response.json()['prediction']
    print(f"{symbol}: ${predictions[symbol]:.2f}")
```

---

## 📚 Recursos Adicionais

- **Swagger UI**: http://localhost:8000/docs (interface interativa)
- **ReDoc**: http://localhost:8000/redoc (documentação alternativa)
- **Código Fonte**: [src/api/main.py](../src/api/main.py)
- **Script de Teste**: [src/scripts/teste_local.py](../src/scripts/teste_local.py)

---

## 🔐 Considerações de Produção

### Segurança
- [ ] Adicionar autenticação (API Key, OAuth2)
- [ ] Rate limiting para prevenir abuso
- [ ] HTTPS/TLS em produção
- [ ] Validação de entrada mais rigorosa

### Monitoramento
- [ ] Logs estruturados com nível apropriado
- [ ] Métricas de latência e throughput
- [ ] Alertas para erros 500
- [ ] Health checks periódicos

### Performance
- [ ] Cache de previsões recentes
- [ ] Batch inference para múltiplas requisições
- [ ] Load balancing com múltiplas réplicas
- [ ] GPU acceleration (opcional)

---

## 📞 Suporte

**Problemas ou dúvidas?**
- Consulte: [Troubleshooting](#🐛-troubleshooting) acima
- Ver arquitetura do modelo: [Model - Especificação Técnica](model.md)
- Verificar logs da API: `docker logs <container_id>`
- Testar localmente: `make test-api`

**Quer melhorar o modelo?**
👉 Ver [Model - Hyperparameter Tuning](model.md#🔧-dicas-de-hyperparameter-tuning)

---

## 📚 Documentação Relacionada

- **[← README Principal](../README.md)** - Visão geral e quick start
- **[🧠 Modelo LSTM](model.md)** - Arquitetura e treinamento
- **[📖 Índice de Docs](README.md)** - Todas as documentações

---

**Última Atualização:** 8 de Janeiro de 2026  
**Versão da API:** V1.20260108  
**Status:** ✅ Documentação Completa
- [ ] GPU acceleration (opcional)

---

## 📞 Suporte

Problemas ou dúvidas? 
- Abra uma issue no GitHub
- Consulte: [docs/model.md](model.md) para detalhes do modelo
- Verifique logs da API: `docker logs <container_id>`
