"""
Service for generating fire risk zones using the existing FireSight predictor.
"""
import os
import logging
import math
from typing import List, Dict, Any
import numpy as np
from app.ml.predictor import predict_fire_risk
from app.services.forest_regions import FOREST_REGIONS

logger = logging.getLogger(__name__)

class RiskZoneService:
    """Service to generate risk zones around forest regions."""

    def __init__(self):
        """Initialize the risk zone service."""
        # Number of points per region (2-3 points per region for visualization)
        self.num_points_per_region = int(os.getenv("RISK_POINTS_PER_REGION", "2"))
        # Radius for point distribution around region center (in degrees)
        self.point_radius_degree = float(os.getenv("RISK_POINT_RADIUS_DEGREE", "0.5"))

    def generate_points_for_region(self, region: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate points around a forest region center for visualization.
        Points are placed on a circle of fixed radius around the center.

        Args:
            region: Dictionary containing region info with keys:
                center_latitude, center_longitude, radius_latitude, radius_longitude

        Returns:
            List of dictionaries, each representing a point with
            latitude and longitude, plus region id and name.
        """
        center_lat = region["center_latitude"]
        center_lon = region["center_longitude"]

        points = []
        for i in range(self.num_points_per_region):
            angle = i * (2 * math.pi / self.num_points_per_region)
            lat_offset = self.point_radius_degree * math.cos(angle)
            lon_offset = self.point_radius_degree * math.sin(angle)
            lat = center_lat + lat_offset
            lon = center_lon + lon_offset
            # Create a unique id: region_id_i
            point_id = f"{region['id']}_{i}"
            points.append({
                "id": point_id,
                "latitude": float(lat),
                "longitude": float(lon),
                "region_id": region["id"],
                "region_name": region["name"],
            })
        return points

    def prepare_features(self, lat: float, lon: float) -> Dict[str, float]:
        """
        Prepare environmental features for a given latitude and longitude.
        For the purpose of this hackathon, we'll generate mock environmental
        data based on the location. In a real system, this would come from
        external APIs or databases.

        Returns:
            Dictionary of environmental features.
        """
        # We'll create mock environmental data that varies with location.
        # This is just for demonstration. In a real system, you would use
        # real data sources (e.g., weather APIs, elevation models, etc.).

        # Base values (these are arbitrary and for demonstration only)
        base_temp = 25.0  # Celsius
        base_humidity = 60.0  # Percent
        base_wind_speed = 10.0  # km/h
        base_rainfall = 5.0  # mm

        # Adjust based on latitude (simulating temperature gradient)
        # We need a reference latitude range for adjustment; use -90 to 90
        lat_norm = (lat + 90) / 180  # 0 to 1
        temp_adjustment = lat_norm * 30  # -15 to +15? Actually we want variation.
        # Let's do: temperature = base_temp + (lat_norm - 0.5) * 30  => -15 to +15 around base
        temperature = base_temp + (lat_norm - 0.5) * 30

        # Adjust based on longitude for humidity (simple)
        lon_norm = (lon + 180) / 360  # 0 to 1
        humidity_adjustment = (lon_norm - 0.5) * 40  # -20 to +20
        humidity = base_humidity - humidity_adjustment  # More east -> less humidity? arbitrary

        # Wind speed and rainfall: simple functions
        wind_speed = base_wind_speed + abs(lat_norm - 0.5) * 20  # more wind away from equator
        rainfall = base_rainfall + (lon_norm - 0.5) * 30  # arbitrary

        # Ensure values are within reasonable bounds
        temperature = max(10, min(50, temperature))
        humidity = max(0, min(100, humidity))
        wind_speed = max(0, min(60, wind_speed))
        rainfall = max(0, min(100, rainfall))

        # For vegetation_index, fuel_moisture, elevation, slope we'll use mock values
        # that are within bounds and vary slightly with location.
        vegetation_index = max(0, min(1, 0.5 + (lat_norm - 0.5) * 0.5))  # 0 to 1
        fuel_moisture = max(0, min(1, 0.5 + (lon_norm - 0.5) * 0.5))   # 0 to 1
        elevation = max(0, min(4000, 1000 + (lat_norm - 0.5) * 3000))  # 0 to 4000m
        slope = max(0, min(60, 10 + (lon_norm - 0.5) * 50))            # 0 to 60 degrees

        return {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "rainfall": rainfall,
            "vegetation_index": vegetation_index,
            "fuel_moisture": fuel_moisture,
            "elevation": elevation,
            "slope": slope,
        }

    def get_risk_zones(self) -> List[Dict[str, Any]]:
        """
        Generate risk zones by creating points around each forest region
        and predicting risk for each point.

        Returns:
            List of dictionaries, each representing a risk zone with
            latitude, longitude, risk_score, risk_level, region info,
            and the environmental features used for the prediction.
        """
        logger.info("Generating risk zones using forest regions")
        all_points = []
        for region in FOREST_REGIONS:
            points = self.generate_points_for_region(region)
            all_points.extend(points)

        risk_zones = []

        for point in all_points:
            lat = point["latitude"]
            lon = point["longitude"]

            # Prepare environmental features for this point
            features = self.prepare_features(lat, lon)

            # Use the existing predictor to get fire probability and risk level
            try:
                prediction = predict_fire_risk(features)
                risk_score = prediction["risk_score"]
                risk_level = prediction["risk_level"]
            except Exception as e:
                logger.error(f"Error predicting risk for point {point['id']}: {e}")
                # In case of error, we set a default risk level
                risk_score = 0
                risk_level = "LOW"

            # Build the risk zone object
            risk_zone = {
                "id": point["id"],
                "latitude": lat,
                "longitude": lon,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "region_id": point["region_id"],
                "region_name": point["region_name"],
                "temperature": features["temperature"],
                "humidity": features["humidity"],
                "wind_speed": features["wind_speed"],
                "rainfall": features["rainfall"],
            }
            risk_zones.append(risk_zone)

        logger.info(f"Generated {len(risk_zones)} risk zones")
        return risk_zones