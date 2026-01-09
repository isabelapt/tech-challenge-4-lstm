import requests
import numpy as np
from src.cache_manager import get_stock_data

# URL = "http://localhost:8000/predict" # Local
URL = "http://lstm-alb-74942114.sa-east-1.elb.amazonaws.com/predict" # AWS (Pegue do output do terraform)

print("Obtendo dados reais para teste...")
# Pega dados recentes para ter 60 dias reais
df = get_stock_data('DIS', '2023-01-01', '2024-07-20')
last_60 = df['Close'].values[-60:].tolist()

payload = {"last_60_days_prices": last_60}

try:
    response = requests.post(URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Predição: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")