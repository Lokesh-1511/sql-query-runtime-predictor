import React, { useState } from 'react'

export default function FeaturePlayground() {
  const [features, setFeatures] = useState({
    number_of_tables: 0,
    number_of_joins: 0,
    number_of_filters: 0,
    aggregation_count: 0,
    subquery_depth: 0,
    scan_count: 0,
  })

  const calculateMockPrediction = () => {
    let baseTime = 0.05
    baseTime += features.number_of_tables * 0.05
    baseTime += features.number_of_joins * 0.15
    baseTime += features.number_of_filters * 0.03
    baseTime += features.aggregation_count * 0.2
    baseTime += features.subquery_depth * 0.3
    baseTime += features.scan_count * 0.1
    return baseTime
  }

  const handleChange = (key, value) => {
    setFeatures((prev) => ({
      ...prev,
      [key]: Math.max(0, parseInt(value, 10) || 0),
    }))
  }

  const mockPrediction = calculateMockPrediction()
  const fields = [
    { key: 'number_of_tables', label: 'Number of Tables', max: 10 },
    { key: 'number_of_joins', label: 'Number of Joins', max: 10 },
    { key: 'number_of_filters', label: 'Number of Filters', max: 15 },
    { key: 'aggregation_count', label: 'Aggregation Count', max: 8 },
    { key: 'subquery_depth', label: 'Subquery Depth', max: 6 },
    { key: 'scan_count', label: 'Scan Count', max: 8 },
  ]

  return (
    <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Feature Playground</h2>
      <p className="mt-2 text-sm text-slate-600">Adjust structural values to simulate runtime trends in a local mock model.</p>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        {fields.map((field) => (
          <div key={field.key} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <label className="text-sm font-medium text-slate-700">{field.label}</label>
              <span className="text-sm font-semibold text-slate-900">{features[field.key]}</span>
            </div>
            <input
              type="range"
              min="0"
              max={field.max}
              value={features[field.key]}
              onChange={(e) => handleChange(field.key, e.target.value)}
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-blue-600"
            />
          </div>
        ))}
      </div>

      <div className="mx-auto mt-8 max-w-md rounded-xl border border-blue-200 bg-blue-50 p-6 text-center">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Mock Runtime</p>
        <p className="mt-2 text-4xl font-bold text-slate-900">{mockPrediction.toFixed(3)}s</p>
        <p className="mt-2 text-xs text-slate-500">This value is simulated in the UI and is not a backend prediction.</p>
      </div>
    </section>
  )
}
