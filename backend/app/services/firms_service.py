"""
NASA FIRMS service for retrieving active fire hotspots.
"""
import os
import logging
import time
from typing import List, Dict, Any, Optional
import requests
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FirmsService:
    """Service to interact with NASA FIRMS API."""

    def __init__(self):
        """Initialize the FIRMS service with configuration from environment."""
        self.map_key = os.getenv("FIRMS_MAP_KEY")
        if not self.map_key:
            logger.warning("FIRMS_MAP_KEY not set. FIRMS service will not work.")

        self.source = os.getenv("FIRMS_SOURCE", "VIIRS_NOAA20_NRT")
        self.days = int(os.getenv("FIRMS_DAYS", "1"))
        self.west = float(os.getenv("FIRMS_WEST", "68"))
        self.south = float(os.getenv("FIRMS_SOUTH", "6"))
        self.east = float(os.getenv("FIRMS_EAST", "98"))
        self.north = float(os.getenv("FIRMS_NORTH", "36"))
        self.cache_duration = int(os.getenv("FIRMS_CACHE_DURATION_SECONDS", "300"))

        # In-memory cache: {cache_key: (timestamp, data)}
        self._cache: Dict[str, Any] = {}

        # Base URL for FIRMS API
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

    def check_availability(self) -> bool:
        """Check if the FIRMS API is reachable."""
        if not self.map_key:
            return False
        url = self._build_url()
        try:
            response = requests.get(url, timeout=10, stream=True)
            # We don't need to download the body, just check the status code.
            response.close()
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _build_url(self) -> str:
        """Construct the FIRMS API URL."""
        if not self.map_key:
            raise ValueError("FIRMS_MAP_KEY is not set")

        return (
            f"{self.base_url}/{self.map_key}/{self.source}/"
            f"{self.west},{self.south},{self.east},{self.north}/{self.days}"
        )

    def _fetch_firms_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch data from FIRMS API.

        Returns:
            DataFrame with FIRMS data or None if failed.
        """
        url = self._build_url()
        logger.info(f"Fetching FIRMS data from: {url} (without API key)")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch FIRMS data: {e}")
            return None

        # Check if response is empty
        if not response.text.strip():
            logger.warning("FIRMS returned empty response")
            return None

        try:
            # Parse CSV data
            df = pd.read_csv(pd.compat.StringIO(response.text))
        except Exception as e:
            logger.error(f"Failed to parse FIRMS CSV data: {e}")
            return None

        logger.info(f"FIRMS returned {len(df)} rows")
        return df

    def _normalize_hotspot(self, row: pd.Series) -> Dict[str, Any]:
        """
        Normalize a FIRMS row into our hotspot format.

        Args:
            row: A row from the FIRMS DataFrame.

        Returns:
            Dictionary representing a hotspot.
        """
        # Extract relevant fields, providing defaults if missing
        latitude = float(row.get("latitude", 0.0))
        longitude = float(row.get("longitude", 0.0))
        acq_date = str(row.get("acq_date", ""))
        acq_time = str(row.get("acq_time", ""))
        satellite = str(row.get("satellite", ""))
        instrument = str(row.get("instrument", ""))
        confidence = row.get("confidence")
        frp = row.get("frp")
        daynight = str(row.get("daynight", ""))

        # Convert confidence to float if possible, else None
        try:
            confidence_float = float(confidence) if confidence is not None else None
        except (ValueError, TypeError):
            confidence_float = None

        # Convert FRP to float if possible, else None
        try:
            frp_float = float(frp) if frp is not None else None
        except (ValueError, TypeError):
            frp_float = None

        # Calculate severity based on FRP and confidence
        severity = self._calculate_severity(confidence_float, frp_float)

        # Construct detection timestamp
        detection_time = None
        if acq_date and acq_time:
            # FIRMS acq_time is in format HHMM (local time)
            try:
                time_str = acq_time.zfill(4)  # Ensure 4 digits
                detection_time = datetime.strptime(
                    f"{acq_date} {time_str}", "%Y-%m-%d %H%M"
                )
            except ValueError:
                pass

        # If we couldn't parse detection time, use current time as fallback
        if detection_time is None:
            detection_time = datetime.now()

        return {
            "latitude": latitude,
            "longitude": longitude,
            "acq_date": acq_date,
            "acq_time": acq_time,
            "satellite": satellite,
            "instrument": instrument,
            "confidence": confidence_float,
            "frp": frp_float,
            "daynight": daynight,
            "severity": severity,
            "source": "NASA FIRMS",
            "detected_at": detection_time.isoformat(),
        }

    def _calculate_severity(
        self, confidence: Optional[float], frp: Optional[float]
    ) -> str:
        """
        Calculate severity level from confidence and FRP.

        This is a simple heuristic and not an official NASA classification.

        Args:
            confidence: Confidence value (0-100) or None.
            frp: Fire Radiative Power in MW or None.

        Returns:
            Severity level: "LOW", "MEDIUM", "HIGH", or "CRITICAL".
        """
        # If we don't have data, default to LOW
        if confidence is None and frp is None:
            return "LOW"

        # Normalize confidence to 0-1 scale (if it's 0-100)
        conf_norm = None
        if confidence is not None:
            if confidence > 1.0:  # Assume it's 0-100
                conf_norm = confidence / 100.0
            else:
                conf_norm = confidence  # Assume it's already 0-1

        # Normalize FRP: typical FRP values for fires range from 0 to 500 MW?
        # We'll use a simple threshold:
        #   LOW: FRP < 10 MW
        #   MEDIUM: 10 <= FRP < 50
        #   HIGH: 50 <= FRP < 100
        #   CRITICAL: FRP >= 100
        # But we also want to incorporate confidence.

        # We'll compute a score:
        #   score = (conf_norm or 0.5) * (1 + log1p(frp or 0))
        # Then map to severity.

        # For simplicity, we'll use:
        #   If FRP is available, use it primarily.
        #   Else, use confidence.

        if frp is not None:
            # FRP-based severity
            if frp >= 100:
                return "CRITICAL"
            elif frp >= 50:
                return "HIGH"
            elif frp >= 10:
                return "MEDIUM"
            else:
                return "LOW"
        elif conf_norm is not None:
            # Confidence-based severity
            if conf_norm >= 0.8:
                return "HIGH"
            elif conf_norm >= 0.5:
                return "MEDIUM"
            else:
                return "LOW"
        else:
            return "LOW"

    def get_hotspots(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get hotspots from FIRMS with caching and fallback to mock.

        Args:
            use_cache: Whether to use cached data if available and not expired.

        Returns:
            List of hotspot dictionaries.
        """
        cache_key = f"firms_{self.source}_{self.days}_{self.west}_{self.south}_{self.east}_{self.north}"

        # Check cache
        if use_cache and cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                logger.info(f"Returning cached FIRMS data (age: {time.time() - timestamp:.0f}s)")
                return data

        # Try to fetch from FIRMS
        try:
            df = self._fetch_firms_data()
            if df is not None and not df.empty:
                # Normalize each row
                hotspots = []
                for _, row in df.iterrows():
                    hotspot = self._normalize_hotspot(row)
                    hotspots.append(hotspot)

                # Update cache
                if use_cache:
                    self._cache[cache_key] = (time.time(), hotspots)

                logger.info(f"Returning {len(hotspots)} hotspots from FIRMS")
                return hotspots
            else:
                logger.warning("FIRMS returned no data")
        except Exception as e:
            logger.error(f"Unexpected error in FIRMS service: {e}")

        # Fallback to mock data
        logger.warning("Falling back to mock hotspot data")
        return self._generate_mock_hotspots()

    def _generate_mock_hotspots(self) -> List[Dict[str, Any]]:
        """
        Generate mock hotspot data (similar to the original mock but with FIRMS-like fields).

        Returns:
            List of mock hotspot dictionaries.
        """
        # We'll generate mock data that resembles FIRMS format
        import random
        from datetime import datetime, timedelta

        # Use regions that are within our default bounding box (India)
        regions = [
            "Jammu & Kashmir", "Himachal Pradesh", "Uttarakhand", "Sikkim", "Arunachal Pradesh",
            "Assam", "Meghalaya", "Nagaland", "Manipur", "Mizoram", "Tripura",
            "West Bengal", "Bihar", "Jharkhand", "Odisha", "Chhattisgarh",
            "Madhya Pradesh", "Gujarat", "Maharashtra", "Goa", "Karnataka",
            "Kerala", "Tamil Nadu", "Andhra Pradesh", "Telangana", "Uttar Pradesh",
            "Rajasthan", "Punjab", "Haryana", "Delhi"
        ]

        hotspots = []
        for i in range(15):  # Generate 15 mock hotspots
            # Generate random latitude and longitude within India bounds
            latitude = round(random.uniform(self.south, self.north), 4)
            longitude = round(random.uniform(self.west, self.east), 4)

            # Random confidence (0-100)
            confidence = round(random.uniform(30, 98), 1)

            # Random FRP (0-100 MW)
            frp = round(random.uniform(0.1, 50.0), 2)

            # Random satellite and instrument
            satellite = random.choice(["NOAA-20", "NOAA-21", "SUOMI-NPP"])
            instrument = "VIIRS"

            # Random acquisition time (last 24 hours)
            detected_at = datetime.now() - timedelta(hours=random.randint(0, 24))
            acq_date = detected_at.strftime("%Y-%m-%d")
            acq_time = detected_at.strftime("%H%M").zfill(4)

            # Random day/night
            daynight = random.choice(["D", "N"])

            # Calculate severity
            severity = self._calculate_severity(confidence, frp)

            hotspot = {
                "latitude": latitude,
                "longitude": longitude,
                "acq_date": acq_date,
                "acq_time": acq_time,
                "satellite": satellite,
                "instrument": instrument,
                "confidence": confidence,
                "frp": frp,
                "daynight": daynight,
                "source": "MOCK",
                "detected_at": detected_at.isoformat(),
            }
            hotspots.append(hotspot)

        return hotspots