# React Frontend - SQL Query Runtime Predictor

## 🎉 Complete Setup Instructions

### Installation & Running

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit: **http://localhost:5173**

---

## 📋 Project Files Created

### Configuration Files
- `package.json` - Dependencies and scripts
- `vite.config.js` - Vite bundler configuration
- `tailwind.config.js` - Tailwind CSS theme
- `postcss.config.js` - PostCSS plugins
- `index.html` - HTML entry point
- `.gitignore` - Git ignore rules

### Source Code

#### Core Files
- `src/main.jsx` - React app entry point
- `src/App.jsx` - Root component
- `src/index.css` - Global Tailwind styles

#### API Integration
- `src/api/api.js` - Axios HTTP client with:
  - `predictQuery(query)` - POST to /predict
  - `getModelInfo()` - GET /model-info

#### Components
All components in `src/components/`:

1. **QueryInput.jsx**
   - SQL textarea with placeholder
   - "Predict Runtime" button (disabled during loading)
   - "Load Sample" button for pre-filled queries
   - Clear button
   - Loading spinner
   - Tip box

2. **PredictionResult.jsx**
   - Displays predicted_runtime_seconds
   - Shows runtime in milliseconds
   - Predicted_log_runtime
   - Model name
   - Query category
   - Speed indicator (Fast/Medium/Slow)
   - Visual progress bar
   - Confidence score
   - Loading state

3. **FeatureDisplay.jsx**
   - Displays all extracted query features:
     - Tables used
     - Number of tables
     - Number of joins
     - Number of filters
     - Aggregation count
     - Subquery depth
     - Scan count
   - Normalized features grid
   - Cards with icons

4. **FeaturePlayground.jsx**
   - Interactive sliders for:
     - Number of tables
     - Number of joins
     - Number of filters
     - Aggregation count
     - Subquery depth
     - Scan count
   - Mock prediction calculation
   - Reset to defaults button
   - Current values display

5. **ModelInfo.jsx**
   - Displays model metrics:
     - Model name
     - R² score
     - MAE
     - RMSE
     - Feature count
     - Training samples
   - Model version
   - Last trained date
   - Loading spinner
   - Error handling with retry

#### Pages
- `src/pages/Dashboard.jsx` - Main dashboard page with:
  - Header with title
  - Error notification area
  - Grid layout combining all components
  - State management for predictions
  - API error handling
  - Responsive design

### Documentation
- `README.md` - Complete feature documentation
- `SETUP.md` - Backend integration guide

---

## 🎨 Design Features

### Colors & Styling
- **Primary**: Blue (#3b82f6)
- **Backgrounds**: Light blue gradients
- **Cards**: White with shadows and borders
- **Icons**: Emojis for visual appeal
- **Responsive**: Mobile → Tablet → Desktop

### Components Styling
- Cards with left accent borders
- Rounded corners (rounded-lg)
- Shadows for depth
- Hover effects
- Loading spinners (animated)
- Progress bars
- Grid layouts

### Tailwind Classes Used
- `bg-blue-600`, `hover:bg-blue-700`
- `rounded-lg`, `shadow-md`
- `grid`, `flex`, `gap-4`
- `p-4`, `px-6`, `py-2` (spacing)
- `text-2xl`, `font-bold` (typography)
- `disabled:bg-gray-400` (states)
- `md:grid-cols-2`, `lg:col-span-2` (responsive)

---

## 🔌 Backend API Integration

### Expected Response Format for /predict

```json
{
  "predicted_runtime_seconds": 0.125,
  "predicted_log_runtime": -2.079,
  "model_name": "XGBoost Runtime Predictor",
  "query_category": "SELECT",
  "tables_used": ["orders", "customers"],
  "number_of_tables": 2,
  "number_of_joins": 1,
  "number_of_filters": 2,
  "aggregation_count": 0,
  "subquery_depth": 0,
  "scan_count": 1,
  "where_clause_count": 2,
  "confidence_score": 0.92,
  "normalized_features": {
    "feature_1": 0.45,
    "feature_2": 0.82,
    ...
  }
}
```

### Expected Response Format for /model-info

```json
{
  "model_name": "XGBoost Runtime Predictor",
  "r2_score": 0.8742,
  "mae": 0.0234,
  "rmse": 0.0567,
  "feature_count": 12,
  "training_samples": 4000,
  "model_version": "1.0",
  "last_trained": "2024-03-17",
  "description": "ML model for SQL query runtime prediction"
}
```

---

## 🚀 Features Implemented

✅ SQL query input with rich UI
✅ Real-time API predictions
✅ Loading spinners and error handling
✅ Query feature extraction display
✅ Speed indicator (visual progress bar)
✅ Feature playground with sliders
✅ Model information dashboard
✅ Sample query loader
✅ Responsive mobile/tablet/desktop design
✅ Modern Tailwind CSS styling
✅ Axios API client with error handling
✅ Component-based architecture
✅ State management with React hooks
✅ Confidence score display
✅ Mock prediction in playground

---

## 📱 Responsive Breakpoints

- **Mobile**: Single column layout
- **Tablet (md)**: 2-3 columns
- **Desktop (lg)**: Full grid with 3+ columns

```jsx
{/* Example responsive layout */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

---

## 🛠️ Available Development Scripts

```bash
# Start dev server (http://localhost:5173)
npm run dev

# Build for production (creates dist/ folder)
npm run build

# Preview production build locally
npm run preview

# Lint code (if ESLint configured)
npm run lint
```

---

## ⚙️ Backend Requirements

### Ensure Backend Has:

1. **CORS Enabled** for localhost:5173
2. **POST /predict endpoint**
3. **GET /model-info endpoint**
4. **Running on port 8000** or update API_BASE_URL in src/api/api.js

### FastAPI CORS Example:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔍 File Tree

```
frontend/
├── .gitignore
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── vite.config.js
├── README.md
├── SETUP.md
└── src/
    ├── index.css
    ├── main.jsx
    ├── App.jsx
    ├── api/
    │   └── api.js
    ├── components/
    │   ├── QueryInput.jsx
    │   ├── PredictionResult.jsx
    │   ├── FeatureDisplay.jsx
    │   ├── FeaturePlayground.jsx
    │   └── ModelInfo.jsx
    └── pages/
        └── Dashboard.jsx
```

---

## 🎯 Usage Flow

1. **Enter SQL Query** → QueryInput component
2. **Click Predict** → Axios calls POST /predict
3. **Show Results** → PredictionResult displays:
   - Runtime seconds
   - Speed indicator
   - Confidence score
4. **Show Features** → FeatureDisplay shows extracted features
5. **Explore Features** → FeaturePlayground for experimentation
6. **View Model Info** → ModelInfo shows performance metrics

---

## 📦 Dependencies Installed

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.0",
  "recharts": "^2.10.0",
  "vite": "^5.0.0",
  "tailwindcss": "^3.4.0",
  "postcss": "^8.4.0",
  "autoprefixer": "^10.4.0"
}
```

---

## ✨ Extra Features Included

✅ Loading spinner animation
✅ Error notifications
✅ Disabled button states during loading
✅ Sample query button
✅ Clear button
✅ Speed indicator with color coding
✅ Confidence score display
✅ Model performance metrics
✅ Feature playground with sliders
✅ Responsive mobile design
✅ Smooth animations and transitions

---

## 🚀 Next Steps

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Ensure Backend is Running
```bash
cd ml-sql-query-runtime-prediction-system
python -m uvicorn api.app:app --reload
# or run your backend start command
```

### 3. Start Frontend Dev Server
```bash
cd frontend
npm run dev
```

### 4. Open Browser
Visit: **http://localhost:5173**

---

## 📞 Troubleshooting

### "Cannot connect to backend"
- Verify backend is running on http://localhost:8000
- Check CORS is enabled in FastAPI
- Update API_BASE_URL in src/api/api.js if needed

### "npm install fails"
```bash
rm -rf node_modules package-lock.json
npm install
```

### "Port 5173 already in use"
```bash
npm run dev -- --port 5174
```

### "Build fails"
```bash
npm cache clean --force
npm install
npm run build
```

---

## 🎁 Bonus: Production Deployment

Build the app:
```bash
npm run build
```

This creates a `dist/` folder with optimized files ready to deploy to:
- Vercel
- Netlify
- GitHub Pages
- AWS S3
- Any static hosting service

---

**Your SQL Query Runtime Predictor frontend is ready! 🎉**
