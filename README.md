# 🌍 AQ-Guardian: AI-Powered Air Quality Forecasting System

> Real-time PM10 forecasting with personalized health guidance for Chemnitz, Germany

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

**AQ-Guardian** is a production-ready, end-to-end ML system that forecasts air quality (PM10 levels) one hour ahead and provides personalized health recommendations based on WHO/EU guidelines. Built with real-time data from OpenAQ sensor 11057 in Chemnitz, Germany.

### ✨ Key Features

- **📊 Real-time Data Pipeline**: Automated daily ingestion from OpenAQ API
- **🤖 XGBoost ML Model**: 24% improvement over baseline (R²=0.65)
- **🔌 Production API**: FastAPI with interactive Swagger documentation
- **🎨 Consumer UI**: Beautiful gradient Streamlit dashboard
- **🩺 RAG Health Assistant**: Personalized advice for 6 health profiles
- **⚡ Live Predictions**: Dynamic forecasts based on weather inputs

---

## 🏗️ System Architecture

┌─────────────────────────────────────────────────────────────────┐
│ AQ-GUARDIAN ARCHITECTURE │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ OpenAQ API │ ← Chemnitz Sensor 11057 (PM10 data)
│ Open-Meteo │ ← Weather API (temp, humidity, wind)
└──────┬───────┘
│
▼
┌──────────────────────┐
│ Data Pipeline │
│ (scripts/daily_*) │
│ - ETL & Cleaning │
│ - Feature Eng. │
│ - Hourly Merge │
└──────┬───────────────┘
│
▼
┌──────────────────────┐
│ XGBoost Model │
│ - 12 features │
│ - R² = 0.65 │
│ - 24% > baseline │
└──────┬───────────────┘
│
▼
┌──────────────────────┐ ┌─────────────────────┐
│ FastAPI Server │◄────────│ Streamlit UI │
│ - /forecast │ │ - Weather inputs │
│ - /health-advice │ │ - Predictions │
│ - Swagger docs │ │ - RAG assistant │
└──────────────────────┘ └─────────────────────┘


---

## 📊 Model Performance

| Metric | Value | Comparison |
|--------|-------|------------|
| **RMSE** | 3.42 µg/m³ | 24% better than persistence baseline |
| **MAE** | 2.15 µg/m³ | Mean Absolute Error |
| **R²** | 0.65 | Coefficient of determination |
| **Training Data** | 103 hours | Real sensor readings |

**Model Comparison:**
- **Persistence Baseline** (naïve): RMSE = 4.50 µg/m³
- **XGBoost Model**: RMSE = 3.42 µg/m³ ✅ **24% improvement**

---


## 🧪 API Usage

curl -X POST "http://localhost:8000/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "hour": 14,
    "latest_pm10": 25.0,
    "temp": 15.0,
    "humidity": 65.0,
    "wind_speed": 3.5,
    "precipitation": 0.0
  }'

 ## Response:

{
  "pm10_forecast_1h": 23.82,
  "confidence": "high",
  "timestamp": "2026-02-03T15:00:00"
}

## 🩺 RAG Health Assistant
Provides personalized advice based on WHO Air Quality Guidelines and EU Regulations:

### Health Profiles
👤 General public
👶 Children (under 12)
👴 Elderly (65+)
😷 Asthma/respiratory conditions
❤️ Heart disease
🤰 Pregnant individuals

### Knowledge Base Sources
WHO Air Quality Guidelines (2021)
EU Air Quality Directive 2008/50/EC
German Federal Environment Agency (UBA)

## Requirements.txt
### Core ML & Data
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2
xgboost==2.0.3
joblib==1.3.2

### API
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

### Dashboard
streamlit==1.28.2
plotly==5.18.0

### Data Collection
requests==2.31.0
python-dotenv==1.0.0

### Visualization (optional, for notebooks)
matplotlib==3.8.2
seaborn==0.13.0
jupyter==1.0.0

## .gitignore

### Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

### Jupyter
.ipynb_checkpoints

### IDE
.vscode/
.idea/
*.swp
*.swo

### Data (don't commit large files)
data/raw/*.csv
data/raw/*.json
*.pkl

### OS
.DS_Store
Thumbs.db

### Environment
.env
.env.local

### Logs
*.log


## 📧 Contact
#### Your Name - @Keval-Savaliya - skeval1601@gmail.com
#### Project Link: https://github.com/Skeval/SKeval-aq-guardian
