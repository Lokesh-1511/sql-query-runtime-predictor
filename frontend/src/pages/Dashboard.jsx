import React from 'react'
import PredictPage from './PredictPage'

export default function Dashboard() {
  return <PredictPage prediction={null} isLoading={false} error={null} onPredict={async () => {}} />
}
