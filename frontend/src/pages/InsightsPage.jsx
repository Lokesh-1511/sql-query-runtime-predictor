import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import ModelInfo from '../components/ModelInfo'

const EMPTY_DATA = [
  { feature: 'No Data', value: 0 },
]

export default function InsightsPage({ prediction }) {
  const chartData = prediction?.top_feature_values
    ? Object.entries(prediction.top_feature_values)
        .map(([key, value]) => ({ feature: key, value: Number(value) }))
        .filter((item) => Number.isFinite(item.value))
        .sort((a, b) => b.value - a.value)
        .slice(0, 8)
    : EMPTY_DATA

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Insights</h2>
        <p className="mt-1 text-sm text-slate-600">Explore feature importance from the latest prediction and model quality metrics.</p>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Feature Importance</h3>
        <p className="mt-1 text-sm text-slate-600">Derived from top feature values in the most recent prediction response.</p>

        <div className="mt-6 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="feature" angle={-20} textAnchor="end" tick={{ fill: '#64748b', fontSize: 12 }} interval={0} height={60} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <ModelInfo />
    </div>
  )
}
