# FireSight AI

AI-powered forest fire early warning and response system.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python, FastAPI
- ML: Python, pandas, numpy, scikit-learn (to be implemented in later phases)

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- GET /health
- GET /api/risk
- GET /api/hotspots
- GET /api/alerts
- GET /api/incidents

## Notes

This is a prototype for a hackathon. ML model, satellite API, weather API, database, authentication, SMS, and email are to be implemented in later phases.