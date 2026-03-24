import React, { useState } from 'react'
import PredictPage from './pages/PredictPage'
import PlaygroundPage from './pages/PlaygroundPage'
import InsightsPage from './pages/InsightsPage'
import { predictQuery } from './api/api'

const navItems = [
  { key: 'predict', label: 'Predict' },
  { key: 'playground', label: 'Playground' },
  { key: 'insights', label: 'Insights' },
]

function App() {
  const [activePage, setActivePage] = useState('predict')
  const [prediction, setPrediction] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePredict = async (query) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await predictQuery(query)
      setPrediction(result)
    } catch (err) {
      setPrediction(null)
      setError(
        err.response?.data?.detail ||
        'Prediction failed. Verify backend is running and query is schema-valid.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const renderPage = () => {
    if (activePage === 'playground') {
      return <PlaygroundPage />
    }
    if (activePage === 'insights') {
      return <InsightsPage prediction={prediction} />
    }
    return (
      <PredictPage
        prediction={prediction}
        isLoading={isLoading}
        error={error}
        onPredict={handlePredict}
      />
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold">SQL Runtime Predictor</h1>
            <p className="text-sm text-slate-500">Machine learning-based query runtime estimation</p>
          </div>
          <nav className="hidden gap-2 md:flex">
            {navItems.map((item) => (
              <button
                key={item.key}
                onClick={() => setActivePage(item.key)}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  activePage === item.key
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-6 py-6">
        <aside className="hidden w-56 shrink-0 md:block">
          <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Navigation</p>
            <div className="space-y-1">
              {navItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => setActivePage(item.key)}
                  className={`w-full rounded-lg px-3 py-2 text-left text-sm font-medium transition ${
                    activePage === item.key
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="mx-auto max-w-5xl">{renderPage()}</div>
        </main>
      </div>
    </div>
  )
}

export default App
