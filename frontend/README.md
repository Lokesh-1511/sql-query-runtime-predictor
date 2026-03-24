# SQL Query Runtime Predictor - Frontend

A modern React frontend for the Machine Learning Based SQL Query Runtime Prediction System.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── api.js              # Axios API client
│   ├── components/
│   │   ├── QueryInput.jsx       # SQL query input component
│   │   ├── PredictionResult.jsx # Results display component
│   │   ├── FeatureDisplay.jsx   # Query features display
│   │   ├── FeaturePlayground.jsx # Feature explorer
│   │   └── ModelInfo.jsx        # Model metrics display
│   ├── pages/
│   │   └── Dashboard.jsx        # Main dashboard page
│   ├── App.jsx                  # Root component
│   ├── main.jsx                 # Entry point
│   └── index.css               # Tailwind styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🔌 Backend Integration

The frontend connects to a FastAPI backend running on `http://localhost:8000`

### Expected API Endpoints

#### POST /predict
Predicts query runtime

**Request Body:**
```json
{
  "query": "SELECT * FROM orders WHERE id = 1"
}
```

**Response:**
```json
{
  "predicted_runtime_seconds": 0.125,
  "predicted_log_runtime": -2.079,
  "model_name": "XGBoost Runtime Predictor",
  "query_category": "SELECT",
  "tables_used": ["orders"],
  "number_of_tables": 1,
  "number_of_joins": 0,
  "number_of_filters": 1,
  "aggregation_count": 0,
  "subquery_depth": 0,
  "scan_count": 1,
  "confidence_score": 0.92
}
```

#### GET /model-info
Returns model metadata

**Response:**
```json
{
  "model_name": "XGBoost Runtime Predictor",
  "r2_score": 0.8742,
  "mae": 0.0234,
  "rmse": 0.0567,
  "feature_count": 12,
  "training_samples": 4000,
  "model_version": "1.0",
  "last_trained": "2024-03-17"
}
```

## 🎨 Features

- ✅ SQL query input with sample queries
- ✅ Real-time predictions
- ✅ Visual runtime indicator (speed gauge)
- ✅ Query feature extraction display
- ✅ Feature playground for experimentation
- ✅ Model performance metrics
- ✅ Loading spinners and error handling
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Modern UI with Tailwind CSS
- ✅ Dark mode ready

## 📦 Dependencies

- **react**: UI framework
- **react-dom**: React DOM rendering
- **axios**: HTTP client for API calls
- **tailwindcss**: Utility-first CSS framework
- **recharts**: Charts and visualizations (ready for use)

## ⚙️ Configuration

### Backend URL
To change the backend URL, edit `src/api/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:8000'
```

### Tailwind Customization
Edit `tailwind.config.js` to customize colors, spacing, and more.

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter (if eslint configured)
npm run lint
```

## 📝 Component Documentation

### QueryInput
Allows users to input SQL queries and trigger predictions
- Sample query loader
- Clear button
- Loading state feedback

### PredictionResult
Displays prediction results with visual indicators
- Runtime in seconds and milliseconds
- Speed indicator (Fast/Medium/Slow)
- Progress bar visualization
- Confidence score

### FeatureDisplay
Shows extracted query features
- Tables used
- Join count
- Filter count
- Aggregation count
- Subquery depth

### ModelInfo
Displays model performance metrics
- R² score
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- Feature count
- Training samples

### FeaturePlayground
Interactive feature explorer
- Sliders to adjust query characteristics
- Mock runtime calculation
- Current values display

## 🌐 Cross-Origin (CORS)

The backend must have CORS enabled for `http://localhost:5173` (dev) and your production domain.

Example FastAPI CORS configuration:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Responsive Design

The frontend is fully responsive:
- **Mobile**: Single column layout
- **Tablet**: Two column layout
- **Desktop**: Optimized grid layout

## 🎯 Future Enhancements

- Add query history
- Export prediction reports
- Comparison metrics between queries
- Advanced feature visualization
- Query optimization suggestions
- Real-time monitoring dashboard

## 📄 License

This project is part of the ML-based SQL Query Runtime Prediction System.

## 🤝 Support

For issues or questions, please refer to the main project documentation.
