print("DEBUG: main.py top level")  # Debug print
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import risk, hotspots, alerts, incidents
from app.services.firms_service import FirmsService
from app.services.ai_incident_service import AIIncidentService
from app.services.risk_zone_service import RiskZoneService
import os

print("DEBUG: main.py imported risk, hotspots, alerts, incidents")  # Debug print

app = FastAPI(title="FireSight AI", description="AI-Powered Forest Fire Early Warning & Response System", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(hotspots.router, prefix="/api/hotspots", tags=["hotspots"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FireSight AI"}

@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check for all services."""
    # Initialize services
    firms_service = FirmsService()
    ai_service = AIIncidentService()
    risk_service = RiskZoneService()

    # Check Backend (always healthy if we reach this endpoint)
    backend_status = "ONLINE"

    # Check ML Engine - try to make a prediction with dummy data
    ml_status = "ONLINE"
    try:
        # Test the predictor with dummy data
        from app.ml.predictor import predict_fire_risk
        test_features = {
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 10.0,
            "rainfall": 5.0,
            "vegetation_index": 0.5,
            "fuel_moisture": 0.5,
            "elevation": 1000.0,
            "slope": 10.0
        }
        prediction = predict_fire_risk(test_features)
        # If we get here without exception, ML is working
        if "risk_score" not in prediction or "risk_level" not in prediction:
            ml_status = "DEGRADED"
    except Exception as e:
        ml_status = "OFFLINE"

    # Check NASA FIRMS
    firs_status = "ONLINE" if firms_service.check_availability() else "OFFLINE"

    # Check AI Engine
    if ai_service.provider == "rule-based":
        ai_status = "ONLINE (RULE-BASED)"
    else:
        # For LLM providers, check if API key is configured
        ai_status = "ONLINE" if ai_service.api_key else "OFFLINE (NO API KEY)"

    # Overall status
    overall_status = "healthy"
    if ml_status == "OFFLINE" or firs_status == "OFFLINE":
        overall_status = "degraded"
    elif ml_status == "DEGRADED":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "services": {
            "backend": backend_status,
            "ml_engine": ml_status,
            "nasa_firms": firs_status,
            "ai_engine": ai_status
        },
        "timestamp": os.times().elapsed  # Simple timestamp
    }