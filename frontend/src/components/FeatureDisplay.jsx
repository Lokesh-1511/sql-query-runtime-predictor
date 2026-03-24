import React from 'react'

const toDisplay = (value) => {
  if (value === null || value === undefined) {
    return 'N/A'
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return value
}

export default function FeatureDisplay({ features }) {
  const summary = [
    { label: 'Tables Used', value: toDisplay(features?.tables_used) },
    { label: 'Number of Tables', value: features?.number_of_tables },
    { label: 'Number of Joins', value: features?.number_of_joins },
    { label: 'Number of Filters', value: features?.number_of_filters },
    { label: 'Aggregation Count', value: features?.aggregation_count },
    { label: 'Query Depth', value: features?.query_depth ?? features?.subquery_depth },
    { label: 'Scan Count', value: features?.scan_count },
  ]

  return (
    <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Feature Summary</h2>

      {!features ? (
        <p className="mt-4 text-sm text-slate-500">Run a prediction to inspect extracted SQL features.</p>
      ) : (
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {summary.map((item) => (
            <div key={item.label} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{item.label}</p>
              <p className="mt-2 text-base font-semibold text-slate-900">{item.value ?? 'N/A'}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
