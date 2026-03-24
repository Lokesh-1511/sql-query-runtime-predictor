# 🚀 QUICKSTART - React Frontend

## Installation (2 minutes)

### Option 1: Automatic (Windows)
```bash
cd frontend
setup.bat
```

### Option 2: Automatic (macOS/Linux)
```bash
cd frontend
bash setup.sh
```

### Option 3: Manual
```bash
cd frontend
npm install
```

---

## Run the Application

### Start Backend (in new terminal)
```bash
cd ml-sql-query-runtime-prediction-system
python -m uvicorn api.app:app --reload
```

**Backend will run on: http://localhost:8000**

### Start Frontend (in another terminal)
```bash
cd frontend
npm run dev
```

**Frontend will run on: http://localhost:5173**

---

## 🎉 Open in Browser

Visit: **http://localhost:5173**

---

## 📝 What You Can Do

1. **Enter a SQL Query**
   - Type or paste any SQL query
   - Or click "Load Sample" for examples

2. **Get Prediction**
   - Click "Predict Runtime" button
   - Instantly see predicted execution time

3. **View Results**
   - Predicted runtime in seconds
   - Speed indicator (Fast/Medium/Slow)
   - Extracted query features
   - Model metrics

4. **Explore Features**
   - Use Feature Playground
   - Adjust feature sliders
   - See how features affect runtime

---

## 📋 Sample Queries to Try

```sql
-- Simple query
SELECT * FROM orders WHERE id = 1

-- Join query
SELECT a.id, b.name 
FROM orders a 
JOIN customers b ON a.customer_id = b.id 
WHERE a.total > 100

-- Complex query with subquery
SELECT * FROM (
    SELECT customer_id, COUNT(*) as order_count 
    FROM orders 
    GROUP BY customer_id
) subq 
WHERE order_count > 5
```

---

## 🛑 If Something Goes Wrong

### Backend won't connect
✅ Ensure backend is running on http://localhost:8000
✅ Check if CORS is enabled in backend
✅ Check Error message in browser console (DevTools)

### npm install fails
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
npm run dev -- --port 5174
```

---

## 📦 What Was Created

```
frontend/
├── src/
│   ├── api/api.js                      # API calls
│   ├── components/
│   │   ├── QueryInput.jsx              # Input form
│   │   ├── PredictionResult.jsx        # Results
│   │   ├── FeatureDisplay.jsx          # Features
│   │   ├── FeaturePlayground.jsx       # Playground
│   │   └── ModelInfo.jsx               # Model metrics
│   └── pages/Dashboard.jsx             # Main page
├── package.json                        # Dependencies
├── vite.config.js                      # Build config
├── tailwind.config.js                  # Styling
└── README.md                           # Full docs
```

---

## 🎨 What You Can Customize

### Change Backend URL
Edit `src/api/api.js`:
```javascript
const API_BASE_URL = 'http://your-server:8000'
```

### Change Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  primary: { 500: '#your-color' }
}
```

### Change Layout
Edit `src/pages/Dashboard.jsx` to arrange components differently

---

## 📚 More Info

- **[README.md](README.md)** - Full feature documentation
- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Detailed setup guide
- **[SETUP.md](SETUP.md)** - Backend integration details

---

## ✨ Key Features

✅ Real-time SQL query predictions
✅ Beautiful, responsive UI
✅ Loading spinners & error handling
✅ Feature extraction display
✅ Interactive feature playground
✅ Model performance metrics
✅ Sample queries
✅ Speed indicator visualization
✅ Mobile-friendly design

---

**Ready? Open http://localhost:5173 and start predicting! 🎉**
