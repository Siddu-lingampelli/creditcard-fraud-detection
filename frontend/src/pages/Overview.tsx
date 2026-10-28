import { useEffect, useState } from 'react'
import { getSummary, getMetrics } from '../api'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

export default function Overview() {
  const [summary, setSummary] = useState<any>(null)
  const [metrics, setMetrics] = useState<any>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    getSummary().then(setSummary).catch((e) => setError(e.message))
    getMetrics().then(setMetrics).catch(() => {})
  }, [])

  const latestJob = summary?.latest_job
  const result = latestJob?.result
  const isPrediction = latestJob?.job_type === 'prediction'
  const total = isPrediction
    ? result?.rows ?? 0
    : result
      ? (result.train_rows ?? 0) + (result.test_rows ?? 0)
      : 0
  const fraud = isPrediction
    ? result?.predicted_fraud ?? 0
    : metrics?.metrics
      ? (metrics.metrics.tp ?? 0) + (metrics.metrics.fp ?? 0)
      : 0

  const pieData = [
    { name: 'Legitimate', value: result ? result.test_class_counts?.['0'] ?? 0 : 0 },
    { name: 'Fraud', value: result ? result.test_class_counts?.['1'] ?? 0 : 0 },
  ]

  return (
    <div>
      <div className="mb-8">
      <p className="text-xs uppercase tracking-[0.3em] text-[#686868] mb-3">Fraud intelligence</p>
      <h1 className="text-5xl md:text-6xl signature-gradient mb-3">Credit Card Fraud Detection</h1>
      <p className="text-[#686868]">Spark MLlib pipeline - held-out evaluation - metrics from real runs only</p>
    </div>
      {error && <p className="text-red-600">{error}</p>}
      {!summary?.has_results && (
        <div className="bg-[#191919] rounded shadow p-6 mb-6">
          <p>No model run yet. Upload a dataset and run fraud detection to see results.</p>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total transactions" value={total || '—'} />
        <Card title="Predicted fraud" value={fraud || '—'} />
        <Card title="ROC-AUC" value={metrics?.metrics?.roc_auc?.toFixed?.(4) ?? '—'} />
        <Card title="F1-score" value={metrics?.metrics?.f1?.toFixed?.(4) ?? '—'} />
      </div>
      {summary?.has_results && (
        <div className="bg-[#191919] rounded shadow p-6">
          <h3 className="font-semibold mb-4">Test class distribution</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label>
                  <Cell fill="#2563eb" />
                  <Cell fill="#dc2626" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}

function Card({ title, value }: { title: string; value: any }) {
  return (
    <div className="bg-[#191919] rounded shadow p-4">
      <p className="text-sm text-[#686868]">{title}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}

