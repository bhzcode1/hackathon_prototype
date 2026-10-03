"""
Defines major forest regions for risk zone visualization.
These regions are used as centers for generating FireSight ML risk zones.
"""

from typing import List, Dict, Any

# Define forest regions with approximate centers and radii.
# Each region gets a small grid of risk cells around its center.
# Note: These are visualization regions for the FireSight prototype.
# They do not represent exact forest boundaries.
FOREST_REGIONS: List[Dict[str, Any]] = [
    {
        "id": "amazon_basin",
        "name": "Amazon Basin",
        "center_latitude": -3.0,
        "center_longitude": -60.0,
        "radius_latitude": 2.0,   # degrees
        "radius_longitude": 2.0,
    },
    {
        "id": "congo_basin",
        "name": "Congo Basin",
        "center_latitude": 0.0,
        "center_longitude": 23.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "southeast_asian_forests",
        "name": "Southeast Asian Forests",
        "center_latitude": 2.0,
        "center_longitude": 110.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "western_ghats",
        "name": "Western Ghats",
        "center_latitude": 12.0,
        "center_longitude": 75.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "siberian_forests",
        "name": "Siberian Forests",
        "center_latitude": 58.0,
        "center_longitude": 100.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "canadian_boreal_forest",
        "name": "Canadian Boreal Forest",
        "center_latitude": 55.0,
        "center_longitude": -105.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "alaska_forest_region",
        "name": "Alaska Forest Region",
        "center_latitude": 63.0,
        "center_longitude": -150.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "pacific_northwest",
        "name": "Pacific Northwest",
        "center_latitude": 45.0,
        "center_longitude": -120.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "california_forest_region",
        "name": "California Forest Region",
        "center_latitude": 39.0,
        "center_longitude": -121.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "central_american_forests",
        "name": "Central American Forests",
        "center_latitude": 15.0,
        "center_longitude": -90.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "mediterranean_forest_region",
        "name": "Mediterranean Forest Region",
        "center_latitude": 40.0,
        "center_longitude": 15.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "east_african_forest_region",
        "name": "East African Forest Region",
        "center_latitude": -3.0,
        "center_longitude": 35.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "australian_forest_region",
        "name": "Australian Forest Region",
        "center_latitude": -25.0,
        "center_longitude": 145.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "new_zealand_forest_region",
        "name": "New Zealand Forest Region",
        "center_latitude": -41.0,
        "center_longitude": 174.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
    {
        "id": "japan_forest_region",
        "name": "Japan Forest Region",
        "center_latitude": 36.0,
        "center_longitude": 138.0,
        "radius_latitude": 2.0,
        "radius_longitude": 2.0,
    },
]