#!/bin/bash

echo "🚀 SQL Query Runtime Predictor - Frontend Setup"
echo "================================================"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js and npm first."
    exit 1
fi

echo "✅ npm found"
echo ""

echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "🎉 Next steps:"
    echo ""
    echo "1. Make sure the backend is running on http://localhost:8000"
    echo "   Run: cd ../ml-sql-query-runtime-prediction-system && python -m uvicorn api.app:app --reload"
    echo ""
    echo "2. Start the frontend development server:"
    echo "   Run: npm run dev"
    echo ""
    echo "3. Open in browser: http://localhost:5173"
    echo ""
else
    echo "❌ Installation failed. Please run 'npm install' manually."
    exit 1
fi
