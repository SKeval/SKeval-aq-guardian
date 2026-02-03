from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime
from pathlib import Path
import uvicorn

app = FastAPI(title="🛡️ AQ-Guardian PM10 API")

# Load your trained model
model = joblib.load("models/pm10_model_latest.pkl")

class ForecastRequest(BaseModel):
    hour: int = 12
    latest_pm10: float = 20.0
    temp: float = 5.0
    humidity: float = 70.0
    wind_speed: float = 3.0
    precipitation: float = 0.0

@app.get("/")
def home():
    return {"message": "Chemnitz PM10 Forecaster", "status": "ready"}

@app.post("/forecast")
def predict_pm10(request: ForecastRequest):
    # Create feature vector (same as training)
    features = pd.DataFrame([{
        'hour': request.hour,
        'day_of_week': 1, 'is_weekend': 0,
        'pm10_lag_1h': request.latest_pm10,
        'pm10_lag_3h': request.latest_pm10,
        'pm10_lag_6h': request.latest_pm10,
        'pm10_rolling_mean_3h': request.latest_pm10,
        'pm10_rolling_std_6h': 2.0,
        'temp_2m': request.temp,
        'humidity': request.humidity,
        'wind_speed': request.wind_speed,
        'precipitation': request.precipitation
    }])
    
    forecast = model.predict(features)[0]
    return {
        "pm10_forecast_1h": round(float(forecast), 2),
        "confidence": "high",
        "timestamp": datetime.now().isoformat(),
        "input": request.dict()
    }

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
