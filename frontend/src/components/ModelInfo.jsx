import React, { useEffect, useState } from 'react'
import { getModelInfo } from '../api/api'

export default function ModelInfo() {
  const [modelInfo, setModelInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchModelInfo()
  }, [])

  const fetchModelInfo = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getModelInfo()
      setModelInfo(data)
    } catch (err) {
      setError('Failed to load model metadata from backend.')
    } finally {
      setLoading(false)
    }
  }

  const formatMetric = (value, digits = 4) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return 'N/A'
    }
    return Number(value).toFixed(digits)
  }

  if (loading) {
    return (
      <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Model Metrics</h3>
        <p className="mt-4 text-sm text-slate-600">Loading model metadata...</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="w-full rounded-xl border border-rose-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Model Metrics</h3>
        <p className="mt-3 text-sm text-rose-700">{error}</p>
        <button
          onClick={fetchModelInfo}
          className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Retry
        </button>
      </section>
    )
  }

  if (!modelInfo) {
    return null
  }

  const metrics = [
    { label: 'Model Name', value: modelInfo.model_name ?? 'N/A' },
    { label: 'R2 Score', value: formatMetric(modelInfo.r2_score) },
    { label: 'MAE', value: formatMetric(modelInfo.mae) },
    { label: 'RMSE', value: formatMetric(modelInfo.rmse) },
    { label: 'Feature Count', value: modelInfo.feature_count ?? 'N/A' },
    { label: 'Training Samples', value: modelInfo.training_samples ?? 'N/A' },
  ]

  return (
    <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">Model Metrics</h3>
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{metric.label}</p>
            <p className="mt-2 text-xl font-semibold text-slate-900">{metric.value}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
