#!/usr/bin/env python3
"""
Train the fire risk prediction model.
"""
import os
import numpy as np
import pandas as pd
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'fire_risk_training.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'fire_risk_model.joblib')

def generate_synthetic_data(n_samples=5000):
    """
    Generate synthetic data for fire risk prediction.
    """
    np.random.seed(42)  # For reproducibility

    # Generate features within realistic ranges
    temperature = np.random.uniform(10, 50, n_samples)          # °C
    humidity = np.random.uniform(10, 100, n_samples)           # %
    wind_speed = np.random.uniform(0, 60, n_samples)           # km/h
    rainfall = np.random.uniform(0, 100, n_samples)            # mm
    vegetation_index = np.random.uniform(0, 1, n_samples)      # 0-1
    fuel_moisture = np.random.uniform(0, 1, n_samples)         # 0-1
    elevation = np.random.uniform(0, 4000, n_samples)          # m
    slope = np.random.uniform(0, 60, n_samples)                # degrees

    # Create feature matrix
    X = np.column_stack([
        temperature, humidity, wind_speed, rainfall,
        vegetation_index, fuel_moisture, elevation, slope
    ])

    # Create a latent variable that combines features with realistic weights
    # Fire probability increases with:
    # - high temperature
    # - low humidity
    # - high wind speed
    # - low rainfall
    # - low vegetation_index (less green = more dry fuel)
    # - low fuel_moisture
    # - moderate to high elevation (but we'll keep simple linear)
    # - high slope

    # Normalize each feature to 0-1 range for weighting
    temp_norm = (temperature - 10) / 40          # 0-1
    hum_norm = (humidity - 10) / 90              # 0-1 (but we want inverse for fire)
    wind_norm = wind_speed / 60                  # 0-1
    rain_norm = rainfall / 100                   # 0-1 (inverse for fire)
    veg_norm = vegetation_index                  # 0-1 (inverse for fire)
    fuel_norm = fuel_moisture                    # 0-1 (inverse for fire)
    elev_norm = elevation / 4000                 # 0-1
    slope_norm = slope / 60                      # 0-1

    # Compute fire score (higher = more likely fire)
    # Weights chosen to give reasonable fire probability (~0.3)
    fire_score = (
        0.25 * temp_norm -          # temperature increases fire
        0.25 * hum_norm +           # humidity decreases fire (so we subtract)
        0.20 * wind_norm +          # wind increases fire
        0.15 * (1 - rain_norm) +    # rain decreases fire (so we use 1 - norm)
        0.15 * (1 - veg_norm) +     # vegetation decreases fire (less green = more fire)
        0.15 * (1 - fuel_norm) +    # fuel moisture decreases fire
        0.10 * elev_norm +          # elevation increases fire
        0.10 * slope_norm           # slope increases fire
    )

    # Apply sigmoid to get probability between 0 and 1
    # Add some noise to avoid perfect separation
    noise = np.random.normal(0, 0.1, n_samples)
    fire_prob = 1 / (1 + np.exp(-(fire_score * 4 + noise)))  # Scale fire_score to make probabilities spread

    # Generate binary target (0=no fire, 1=fire)
    y = np.random.binomial(1, fire_prob)

    # Create feature names
    feature_names = [
        'temperature', 'humidity', 'wind_speed', 'rainfall',
        'vegetation_index', 'fuel_moisture', 'elevation', 'slope'
    ]

    # Create DataFrame
    df = pd.DataFrame(X, columns=feature_names)
    df['fire'] = y

    return df

def main():
    print("Training model...")

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    # Generate or load data
    if not os.path.exists(DATA_PATH):
        print("Generating synthetic dataset...")
        df = generate_synthetic_data(5000)
        df.to_csv(DATA_PATH, index=False)
        print(f"Dataset saved to {DATA_PATH}")
    else:
        print(f"Loading dataset from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)

    print(f"Dataset size: {len(df)}")

    # Separate features and target
    feature_columns = [
        'temperature', 'humidity', 'wind_speed', 'rainfall',
        'vegetation_index', 'fuel_moisture', 'elevation', 'slope'
    ]
    X = df[feature_columns]
    y = df['fire']

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # Train Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    # Ensure model directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")

    # Also save feature names for reference
    feature_info = {
        'feature_names': feature_columns,
        'model_type': 'RandomForestClassifier',
        'training_date': pd.Timestamp.now().isoformat()
    }
    feature_info_path = os.path.join(os.path.dirname(MODEL_PATH), 'feature_info.json')
    with open(feature_info_path, 'w') as f:
        json.dump(feature_info, f, indent=2)

if __name__ == "__main__":
    main()