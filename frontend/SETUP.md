# Frontend Environment Setup

## Backend Requirements

Make sure your FastAPI backend is running on `http://localhost:8000` with these endpoints:

### POST /predict
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM orders"}'
```

### GET /model-info
```bash
curl http://localhost:8000/model-info
```

## CORS Configuration

Ensure your FastAPI backend has CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Running the Frontend

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 3. Open in Browser
Navigate to `http://localhost:5173` and start using the application.

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 8000
- Check CORS configuration in backend
- Verify `API_BASE_URL` in `src/api/api.js`

### Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
```bash
# Use a different port
npm run dev -- --port 5174
```

## Production Build

```bash
npm run build
# Dist folder will contain optimized production files
```

Deploy the `dist` folder to your hosting service.
