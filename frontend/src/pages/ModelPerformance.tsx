import { useEffect, useState } from 'react'
import { getMetrics } from '../api'

export default function ModelPerformance() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getMetrics().then(setData).catch((e) => setError(e.message))
  }, [])

  const m = data?.metrics || {}
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Model Performance</h2>
      {error && <p className="text-red-600">{error}</p>}
      {!data && <p>No metrics available yet.</p>}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Metric label="ROC-AUC" value={m.roc_auc} help="How well the model separates fraud from legitimate transactions." />
          <Metric label="Precision" value={m.precision} help="Of transactions predicted fraud, how many were actually fraud." />
          <Metric label="Recall" value={m.recall} help="Of actual fraud transactions, how many were detected." />
          <Metric label="F1-score" value={m.f1} help="Balance between precision and recall." />
          <div className="bg-[#191919] rounded shadow p-4 col-span-full">
            <h3 className="font-semibold mb-2">Confusion matrix</h3>
            <div className="grid grid-cols-2 gap-2 text-center">
              <Cell label="True positives" value={m.tp} />
              <Cell label="True negatives" value={m.tn} />
              <Cell label="False positives" value={m.fp} />
              <Cell label="False negatives" value={m.fn} />
            </div>
            <p className="text-sm text-[#686868] mt-4">
              Accuracy can be misleading because fraud cases are rare; precision, recall and F1 are more informative.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

function Metric({ label, value, help }: { label: string; value: number; help: string }) {
  return (
    <div className="bg-[#191919] rounded shadow p-4">
      <p className="text-sm text-[#686868]">{label}</p>
      <p className="text-2xl font-bold">{typeof value === 'number' ? value.toFixed(4) : '—'}</p>
      <p className="text-xs text-[#686868] mt-2">{help}</p>
    </div>
  )
}

function Cell({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-[#212121] rounded p-3">
      <p className="text-xs text-[#686868]">{label}</p>
      <p className="text-xl font-bold">{value ?? '—'}</p>
    </div>
  )
}
