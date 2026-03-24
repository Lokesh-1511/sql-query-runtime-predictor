import React from 'react'
import QueryInput from '../components/QueryInput'
import PredictionResult from '../components/PredictionResult'
import FeatureDisplay from '../components/FeatureDisplay'

export default function PredictPage({ prediction, isLoading, error, onPredict }) {
  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Predict</h2>
        <p className="mt-1 text-sm text-slate-600">Submit SQL and get runtime estimation with extracted feature counts.</p>
      </section>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      <QueryInput onPredict={onPredict} isLoading={isLoading} />
      <PredictionResult result={prediction} isLoading={isLoading} />
      <FeatureDisplay features={prediction} />
    </div>
  )
}
