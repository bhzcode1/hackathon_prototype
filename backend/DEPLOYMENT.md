# FireSight Backend Deployment on Render

## Build Command
```bash
pip install -r requirements.txt
```

## Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables
- `AI_PROVIDER`: AI provider to use (e.g., "openai", "anthropic", "google"). Default: "rule-based"
- `AI_MODEL`: Model name for the AI provider (e.g., "gpt-4")
- `AI_API_KEY`: API key for the AI provider
- `FIRMS_MAP_KEY`: NASA FIRMS MAP key (required for FIRMS service)
- `FIRMS_SOURCE`: FIRMS source (default: "VIIRS_NOAA20_NRT")
- `FIRMS_DAYS`: Number of days for FIRMS data (default: "1")
- `FIRMS_WEST`: Western longitude bound (default: "68")
- `FIRMS_SOUTH`: Southern latitude bound (default: "6")
- `FIRMS_EAST`: Eastern longitude bound (default: "98")
- `FIRMS_NORTH`: Northern latitude bound (default: "36")
- `FIRMS_CACHE_DURATION_SECONDS`: Cache duration for FIRMS data in seconds (default: "300")
- `RISK_POINTS_PER_REGION`: Number of sample points per forest region (default: "2")
- `RISK_POINT_RADIUS_DEGREE`: Radius in degrees for point distribution (default: "0.5")
- `CORS_ORIGINS`: Comma-separated list of allowed origins for CORS (default: "http://localhost:3000")

## Notes
- The backend binds to host 0.0.0.0 and port $PORT as required by Render.
- The CORS configuration can be adjusted to allow your Vercel frontend domain.