# Tech Challenge Fase 04 – LSTM Stock Prediction

## 📌 Objetivo
Desenvolver um modelo de Deep Learning utilizando LSTM para prever o preço de fechamento de ações e disponibilizar o modelo através de uma API REST.

## 🧠 Tecnologias
- Python 3.11
- TensorFlow / Keras
- FastAPI
- Docker
- Terraform
- AWS (ECR + ECS)

## 📊 Pipeline do Projeto
1. Coleta de dados via Yahoo Finance
2. Pré-processamento e normalização
3. Treinamento do modelo LSTM
4. Avaliação com métricas (MAE, RMSE)
5. Salvamento do modelo
6. Deploy via API REST

## 🚀 Setup de Desenvolvimento

### Pré-requisitos
1. **pyenv** (gerenciador de versão Python):
   ```bash
   # macOS (Homebrew)
   brew install pyenv
   
   # Linux (Ubuntu/Debian)
   curl https://pyenv.run | bash
   ```
   
2. **Python 3.11.5** (via pyenv):
   ```bash
   pyenv install 3.11.5
   pyenv local 3.11.5  # Define versão para este projeto
   python --version    # Verifica (deve ser 3.11.5)
   ```
   > O arquivo `.python-version` garante que todos usem a mesma versão.

3. **Poetry** (gerenciador de dependências):
   ```bash
   pip install poetry
   poetry install      # Instala dependências do pyproject.toml
   ```

### Execução Local

```bash
# Ativar ambiente e dependências
poetry shell

# Opção 1: Treinar modelo
poetry run python -m src.ml.train

# Opção 2: Rodar API localmente
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Opção 3: Testar a API (em outro terminal)
poetry run python scripts/teste_local.py
```

### Comandos Úteis (Makefile)

```bash
# Desenvolvimento
make setup          # Install dependencies
make train          # Run training pipeline
make run-local      # Start API locally
make test-api       # Send test request to API

# Docker
make docker-build   # Build Docker image
make docker-run     # Run Docker container

# AWS + Terraform
make tf-init        # Initialize Terraform
make tf-plan        # Preview infra changes
make tf-apply       # Create AWS resources
make aws-push-tf    # Push image using Terraform outputs
make deploy-ecs-tf  # Force redeploy on ECS
```

## 📁 Estrutura do Projeto

```
lstm-predict/
├── src/
│   ├── api/           # FastAPI app
│   ├── ml/            # Training scripts
│   └── __init__.py
├── notebooks/         # Exploratory notebooks
├── scripts/           # Test scripts
├── infra/             # Terraform configuration
├── modelos/           # Trained models (local)
├── Dockerfile         # Container image
├── Makefile           # Development tasks
├── pyproject.toml     # Poetry dependencies
├── .python-version    # Python 3.11.5
└── README.md          # This file
```

## 🐳 Docker

```bash
# Build
docker build -t lstm-api .

# Run locally
docker run -p 8000:8000 lstm-api
```

## ☁️ Deploy na AWS (via Terraform)

Ver [infra/README.md](infra/README.md) para instruções completas.

Quick start:
```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars com seus valores (AWS Account ID, VPC, Subnets)

make tf-plan
make tf-apply
make aws-push-tf      # Push image
make deploy-ecs-tf    # Deploy na ECS
```

## 📊 API Endpoints

- `GET /` - Health check
- `POST /predict` - Predict next stock price

Request:
```json
{
  "last_60_days": [0.12, 0.15, ..., 0.18]
}
```

Response:
```json
{
  "prediction": 152.45
}
```

## 📝 Notas

- GPU: Desabilitada por padrão (CUDA_VISIBLE_DEVICES=-1) para evitar problemas de compatibilidade.
- MLflow: Usado para rastreamento de experimentos (veja `notebooks/01_exploracao_e_treino.ipynb`).
- Modelos: Salvos em `modelos/` e `models/` (ignorados no git - grandes binários).
