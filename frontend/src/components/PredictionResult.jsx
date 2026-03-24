import React from 'react'

export default function PredictionResult({ result, isLoading }) {
  if (isLoading) {
    return (
      <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Prediction Result</h2>
        <div className="mt-4 flex h-24 items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600"></div>
          <p className="ml-3 text-sm text-slate-600">Running model inference...</p>
        </div>
      </section>
    )
  }

  if (!result) {
    return (
      <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Prediction Result</h2>
        <p className="mt-4 text-sm text-slate-500">Submit a SQL query to view prediction details.</p>
      </section>
    )
  }

  const runtimeSeconds = result.predicted_runtime_seconds || 0
  const runtimeMillis = runtimeSeconds * 1000

  let runtimeColor = 'bg-emerald-500'
  let runtimeLabel = 'Fast'
  if (runtimeSeconds > 10) {
    runtimeColor = 'bg-rose-500'
    runtimeLabel = 'Slow'
  } else if (runtimeSeconds > 5) {
    runtimeColor = 'bg-amber-500'
    runtimeLabel = 'Moderate'
  }

  const barWidth = Math.min((runtimeSeconds / 5) * 100, 100)

  return (
    <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Prediction Result</h2>

      <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Predicted Runtime</p>
        <div className="mt-2 flex items-end gap-2">
          <span className="text-5xl font-bold text-slate-900">{runtimeSeconds.toFixed(3)}</span>
          <span className="pb-2 text-base text-slate-600">seconds</span>
        </div>
        <p className="mt-1 text-sm text-slate-500">{runtimeMillis.toFixed(2)} ms</p>

        <div className="mt-4">
          <div className="mb-1 flex items-center justify-between text-xs text-slate-600">
            <span>Performance Band</span>
            <span className="font-semibold">{runtimeLabel}</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
            <div className={`h-full ${runtimeColor}`} style={{ width: `${barWidth}%` }}></div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Model</p>
          <p className="mt-2 text-base font-semibold text-slate-900">{result.model_name || 'N/A'}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Category</p>
          <p className="mt-2 text-base font-semibold text-slate-900">{result.query_category || 'N/A'}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Log Runtime</p>
          <p className="mt-2 text-base font-semibold text-slate-900">{result.predicted_log_runtime?.toFixed(4) ?? 'N/A'}</p>
        </div>
      </div>
    </section>
  )
}
