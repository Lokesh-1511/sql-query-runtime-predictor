import React from 'react'
import FeaturePlayground from '../components/FeaturePlayground'

export default function PlaygroundPage() {
  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Playground</h2>
        <p className="mt-1 text-sm text-slate-600">Experiment with feature sliders and observe mock runtime behavior.</p>
      </section>

      <FeaturePlayground />
    </div>
  )
}
