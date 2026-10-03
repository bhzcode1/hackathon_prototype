"""
Fire risk prediction pipeline.
Loads the trained model and provides prediction functionality.
"""
import os
import numpy as np
import pandas as pd
import json
import joblib
from typing import Dict, Any, Union

# Paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'fire_risk_model.joblib')
FEATURE_INFO_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'feature_info.json')

class FireRiskPredictor:
    """
    Loads the trained RandomForestClassifier and predicts fire risk.
    """
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self._load_model()
        self._load_feature_info()

    def _load_model(self):
        """Load the trained model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please train the model first.")
        self.model = joblib.load(self.model_path)

    def _load_feature_info(self):
        """Load feature names and metadata."""
        if os.path.exists(FEATURE_INFO_PATH):
            with open(FEATURE_INFO_PATH, 'r') as f:
                feature_info = json.load(f)
                self.feature_names = feature_info.get('feature_names')
        else:
            # Default feature names if info file not found
            self.feature_names = [
                'temperature', 'humidity', 'wind_speed', 'rainfall',
                'vegetation_index', 'fuel_moisture', 'elevation', 'slope'
            ]

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict fire risk from environmental features.

        Args:
            features: Dictionary containing the 8 environmental features.

        Returns:
            Dictionary with fire_probability, risk_score, risk_level, and input features.
        """
        # Validate input features
        self._validate_features(features)

        # Create feature array in the correct order
        feature_array = np.array([[features[name] for name in self.feature_names]])

        # Get probability of fire (class 1)
        fire_probability = self.model.predict_proba(feature_array)[0][1]

        # Convert probability to risk score (0-100)
        risk_score = int(round(fire_probability * 100))

        # Convert risk score to risk level
        if risk_score <= 30:
            risk_level = "LOW"
        elif risk_score <= 60:
            risk_level = "MEDIUM"
        elif risk_score <= 80:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        return {
            "fire_probability": float(fire_probability),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "features": features
        }

    def _validate_features(self, features: Dict[str, float]):
        """
        Validate that all required features are present and within sensible ranges.
        """
        # Define expected features and their valid ranges
        feature_ranges = {
            'temperature': (10, 50),      # °C
            'humidity': (0, 100),         # %
            'wind_speed': (0, 60),        # km/h
            'rainfall': (0, 100),         # mm
            'vegetation_index': (0, 1),   # 0-1
            'fuel_moisture': (0, 1),      # 0-1
            'elevation': (0, 4000),       # m
            'slope': (0, 60)              # degrees
        }

        # Check for missing features
        missing = set(self.feature_names) - set(features.keys())
        if missing:
            raise ValueError(f"Missing features: {missing}")

        # Check for extra features
        extra = set(features.keys()) - set(self.feature_names)
        if extra:
            raise ValueError(f"Unexpected features: {extra}")

        # Validate each feature's range
        for feature, value in features.items():
            if feature in feature_ranges:
                min_val, max_val = feature_ranges[feature]
                if not (min_val <= value <= max_val):
                    raise ValueError(
                        f"{feature} must be between {min_val} and {max_val}. Got {value}."
                    )
            else:
                raise ValueError(f"Unknown feature: {feature}")

# Convenience function for quick prediction
def predict_fire_risk(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Convenience function to predict fire risk.
    """
    predictor = FireRiskPredictor()
    return predictor.predict(features)

if __name__ == "__main__":
    # Example usage
    example_features = {
        "temperature": 38,
        "humidity": 25,
        "wind_speed": 32,
        "rainfall": 2,
        "vegetation_index": 0.65,
        "fuel_moisture": 0.18,
        "elevation": 850,
        "slope": 18
    }
    result = predict_fire_risk(example_features)
    print("Example prediction:")
    print(json.dumps(result, indent=2))