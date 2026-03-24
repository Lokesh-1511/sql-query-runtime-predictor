import React, { useState } from 'react'

const SAMPLE_QUERIES = [
  `SELECT * FROM orders WHERE o_custkey = 123 LIMIT 100`,
  `SELECT o.o_orderkey, c.c_name, COUNT(*) AS order_count FROM orders o JOIN customer c ON o.o_custkey = c.c_custkey GROUP BY o.o_orderkey, c.c_name LIMIT 100`,
  `SELECT * FROM (SELECT o_orderkey, o_totalprice, o_orderstatus FROM orders WHERE o_totalprice > 100000) subquery WHERE subquery.o_orderstatus = 'O' LIMIT 100`,
]

export default function QueryInput({ onPredict, isLoading }) {
  const [query, setQuery] = useState('')

  const handlePredict = async () => {
    if (query.trim()) {
      await onPredict(query)
    }
  }

  const handleSampleQuery = () => {
    const randomQuery = SAMPLE_QUERIES[Math.floor(Math.random() * SAMPLE_QUERIES.length)]
    setQuery(randomQuery)
  }

  const handleClear = () => {
    setQuery('')
  }

  return (
    <section className="w-full rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between gap-3 mb-4">
        <h2 className="text-xl font-semibold text-slate-900">SQL Query</h2>
        <button
          onClick={handleSampleQuery}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          disabled={isLoading}
        >
          Load Sample
        </button>
      </div>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter SQL here... e.g., SELECT * FROM orders WHERE o_custkey = 1 LIMIT 50"
        className="h-56 w-full resize-none rounded-xl border border-slate-300 bg-slate-50 p-4 font-mono text-sm text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
        disabled={isLoading}
      />

      <div className="mt-4 flex items-center justify-between gap-3">
        <div className="flex gap-3">
          <button
            onClick={handlePredict}
            disabled={!query.trim() || isLoading}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isLoading ? 'Predicting...' : 'Predict Runtime'}
          </button>
          <button
            onClick={handleClear}
            disabled={isLoading}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Clear
          </button>
        </div>
        <p className="text-xs text-slate-500">Use schema-valid columns to get accurate feature extraction and runtime prediction.</p>
      </div>

      <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
        More joins, filters, and subqueries usually increase predicted runtime.
      </div>
    </section>
  )
}
