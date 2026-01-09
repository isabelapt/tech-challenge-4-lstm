from fastapi import FastAPI, HTTPException
import tensorflow as tf
import numpy as np
from pydantic import BaseModel
from typing import List
import joblib

app = FastAPI(title="Previsor de Ações LSTM", description="Tech Challenge Fase 4")

# Carregar artefatos na inicialização (Padrão Singleton)
model = tf.keras.models.load_model("models/lstm_model.keras")
scaler = joblib.load("models/scaler.pkl")

class StockInput(BaseModel):
    # Espera uma lista de 60 dias, cada dia com 6 features [Open, High, Low, Close, Volume, Adj Close]
    last_60_days: List[List[float]]
    
@app.get("/")
def home():
    return {"status": "ok", "model": "LSTM V1.20260108.22H27m", "message": "API LSTM rodando! Use /predict"}

@app.post("/predict")
def predict(data: StockInput):
    if len(data.last_60_days) != 60:
        raise HTTPException(status_code=400, detail="Forneça exatamente 60 dias de dados.")
    
    # Validar que cada dia tem 6 features
    if not all(len(day) == 6 for day in data.last_60_days):
        raise HTTPException(status_code=400, detail="Cada dia deve conter 6 features: [Open, High, Low, Close, Volume, Adj Close]")
    
    # Prepara os dados: shape (60, 6)
    input_data = np.array(data.last_60_days)
    scaled_input = scaler.transform(input_data)
    
    # Reshape para (1, 60, 6) - batch_size=1, timesteps=60, features=6
    final_input = scaled_input.reshape(1, 60, 6)
    
    # Predição (retorna valor normalizado de Close)
    prediction_scaled = model.predict(final_input)
    
    # Denormalizar: criar array com 6 features, Close na posição 3
    dummy_features = np.zeros((1, 6))
    dummy_features[0, 3] = prediction_scaled[0, 0]  # Close na coluna 3
    prediction_denorm = scaler.inverse_transform(dummy_features)
    
    return {"prediction": float(prediction_denorm[0, 3])}

if __name__ == "__main__":
    import uvicorn
    # Executa a API localmente para facilitar o debug pelo VS Code
    # Use o launch config "Python: main.py" ou rode diretamente este arquivo.
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )

    # Permite iniciar o servidor executando o arquivo diretamente 
    # (ex.: python src/api/main.py), sem precisar da CLI do uvicorn. 
    # poetry run uvicorn src.api.main:app --reload