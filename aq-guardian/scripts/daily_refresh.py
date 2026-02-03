#!/usr/bin/env python3
"""
Daily ETL: fetch new Chemnitz PM10 + weather → process → retrain model
"""

from dotenv import load_dotenv
import os, requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import GradientBoostingRegressor  # XGBoost improvement

load_dotenv()
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
headers = {"X-API-Key": OPENAQ_API_KEY}

# Constants from your Phase 1
CHEMNITZ_LAT, CHEMNITZ_LON = 50.79, 12.87
SENSOR_ID = 11057  # PM10 sensor

def fetch_latest_chemnitz_data(days_back=7):
    """
    Fetch NEW PM10 + weather data since last data point.
    Returns processed DataFrame ready for modeling.
    """
    
    # 1. Find last date in existing data
    try:
        existing = pd.read_csv("data/processed/chemnitz_features.csv")
        last_date = pd.to_datetime(existing['datetime']).max()
        date_from = (last_date + timedelta(hours=1)).strftime('%Y-%m-%d')
    except:
        date_from = (datetime.now().date() - timedelta(days=days_back)).isoformat()
    
    date_to = datetime.now().strftime('%Y-%m-%d')
    print(f"Fetching data from {date_from} to {date_to}")
    
    # 2. Fetch PM10 (OpenAQ sensor 11057)
    meas_url = f"https://api.openaq.org/v3/sensors/{SENSOR_ID}/measurements"
    params = {
        "datetime_from": f"{date_from}T00:00:00Z",
        "datetime_to": f"{date_to}T23:59:59Z",
        "limit": 1000
    }
    resp = requests.get(meas_url, params=params, headers=headers)
    
 
    
    if resp.status_code != 200:
        print(f"❌ OpenAQ API error: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        pm10 = pd.DataFrame()  # Return empty
    
    else:
        json_data = resp.json()
        if "results" not in json_data or len(json_data["results"]) == 0:
            print("⚠️  No new PM10 data available (normal if up to date)")
            pm10 = pd.DataFrame()
        else:
            meas_df = pd.json_normalize(json_data["results"])
            pm10 = meas_df[["period.datetimeTo.local", "value"]].copy()
            pm10.columns = ["datetime", "pm10"]
            pm10["datetime"] = pd.to_datetime(pm10["datetime"])
            pm10["pm10"] = pd.to_numeric(pm10["pm10"], errors="coerce")
            pm10.dropna(inplace=True)
            pm10.sort_values("datetime", inplace=True)
            print(f"✅ Got {len(pm10)} new PM10 measurements")
    
    # 3. Fetch weather (Open-Meteo)
    weather_url = "https://archive-api.open-meteo.com/v1/archive"
    weather_params = {
        "latitude": CHEMNITZ_LAT,
        "longitude": CHEMNITZ_LON,
        "start_date": date_from,
        "end_date": date_to,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,windspeed_10m",
        "timezone": "Europe/Berlin"
    }
    weather_resp = requests.get(weather_url, params=weather_params)
    hourly = weather_resp.json()["hourly"]
    weather_df = pd.DataFrame({
        "datetime": pd.to_datetime(hourly["time"]),
        "temp_2m": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "precipitation": hourly["precipitation"],
        "wind_speed": hourly["windspeed_10m"]
    })
    
    # 4. Merge
    if pm10.empty:
        print("⏭️  No new data to process")
        return pd.DataFrame()  # Empty
    
    pm10_hourly = pm10.set_index("datetime").resample("H").mean().reset_index()
    pm10_hourly["datetime"] = pm10_hourly["datetime"].dt.tz_localize(None)
    new_data = pd.merge(pm10_hourly, weather_df, on="datetime", how="inner")
    
    print(f"Fetched {len(new_data)} new hourly rows")
    return new_data

def create_features(df):
    """Add lag/rolling/time features (from your Phase 2)"""
    if df.empty:
        return df
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    
    # Lags
    df["pm10_lag_1h"] = df["pm10"].shift(1)
    df["pm10_lag_3h"] = df["pm10"].shift(3)
    df["pm10_lag_6h"] = df["pm10"].shift(6)
    
    # Rolling
    df["pm10_rolling_mean_3h"] = df["pm10"].rolling(3).mean()
    df["pm10_rolling_std_6h"] = df["pm10"].rolling(6).std()
    
    return df.dropna()

# MAIN
if __name__ == "__main__":
    print("🛡️ AQ-Guardian Daily Refresh")
    
    # Fetch new data
    new_raw = fetch_latest_chemnitz_data()
    
    if new_raw.empty:
        print("✅ Already up to date - nothing new to process!")
       
    else:
        print("🔄 Processing new data...")
        # Load historical + append
        try:
            historical = pd.read_csv("data/processed/chemnitz_features.csv")
            print(f"📂 Found {len(historical)} existing rows")
            full_data = pd.concat([historical, new_raw], ignore_index=True)
        except FileNotFoundError:
            print("🚀 First run - using only new data")
            full_data = new_raw
        
        full_data["datetime"] = pd.to_datetime(full_data["datetime"])
        full_data.sort_values("datetime", inplace=True)
        
        # Feature engineering (your Phase 2)
        full_features = create_features(full_data)
        
        if len(full_features) > 50:  # Need minimum data
            print(f"📊 Training on {len(full_features)} rows")
            
            feature_cols = [
                'hour', 'day_of_week', 'is_weekend',
                'pm10_lag_1h', 'pm10_lag_3h', 'pm10_lag_6h',
                'pm10_rolling_mean_3h', 'pm10_rolling_std_6h',
                'temp_2m', 'humidity', 'wind_speed', 'precipitation'
            ]
            
            # Train/test split
            split_idx = int(0.8 * len(full_features))
            train = full_features.iloc[:split_idx]
            
            # Align X/y
            X_train = train[feature_cols].dropna()
            y_train = train['pm10'].shift(-1).loc[X_train.index].dropna()
            X_train = X_train.loc[y_train.index]
            
            # XGBoost model
            model = GradientBoostingRegressor(
                n_estimators=150, max_depth=5, learning_rate=0.05, random_state=42
            )
            model.fit(X_train, y_train)
            
            # Save everything
            Path("data/processed").mkdir(parents=True, exist_ok=True)
            Path("models").mkdir(parents=True, exist_ok=True)
            
            full_features.to_csv("data/processed/chemnitz_features.csv", index=False)
            joblib.dump(model, "models/pm10_model_latest.pkl")
            
            print("✅ XGBoost trained & saved!")
            print(f"📈 Dataset: {len(full_features)} rows")
        else:
            print("⚠️  Need more data for training")