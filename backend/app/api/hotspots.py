from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.services.firms_service import FirmsService
from app.services.incident_service import incident_service

router = APIRouter()
firms_service = FirmsService()

@router.get("")
async def get_hotspots(
    days: int = Query(1, ge=1, le=10, description="Number of days of data to retrieve"),
    source: str = Query("VIIRS_NOAA20_NRT", description="FIRMS data source (e.g., VIIRS_NOAA20_NRT)")
) -> List[Dict[str, Any]]:
    """
    Get active fire hotspots from NASA FIRMS with caching and fallback to mock data.
    Also processes each hotspot to create incidents and alerts.
    """
    # Temporarily override service parameters for this request
    # Note: This is not thread-safe but acceptable for a prototype.
    original_source = firms_service.source
    original_days = firms_service.days
    firms_service.source = source
    firms_service.days = days
    try:
        hotspots = firms_service.get_hotspots()
    finally:
        # Reset to original values
        firms_service.source = original_source
        firms_service.days = original_days

    # Process each hotspot to create incidents and alerts
    for hotspot in hotspots:
        incident_service.process_hotspot(hotspot)

    return hotspots
