import { useEffect, useState } from 'react'
import { getTransactions, getTransaction } from '../api'

export default function Transactions() {
  const [data, setData] = useState<any>({ items: [], total: 0 })
  const [page, setPage] = useState(1)
  const [predicted, setPredicted] = useState('')
  const [minProb, setMinProb] = useState('')
  const [detail, setDetail] = useState<any>(null)

  useEffect(() => {
    getTransactions({ page, page_size: 25, predicted: predicted || undefined, min_probability: minProb || undefined })
      .then(setData)
      .catch(() => {})
  }, [page, predicted, minProb])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Transactions</h2>
      <div className="flex gap-3 mb-4">
        <select className="border rounded p-2" value={predicted} onChange={(e) => { setPredicted(e.target.value); setPage(1) }}>
          <option value="">All</option>
          <option value="1.0">Predicted fraud</option>
          <option value="0.0">Predicted legitimate</option>
        </select>
        <input className="border rounded p-2" placeholder="Min probability" value={minProb} onChange={(e) => setMinProb(e.target.value)} />
      </div>
      <div className="bg-[#191919] rounded shadow overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-[#212121]">
            <tr>
              <th className="p-2 text-left">ID</th>
              <th className="p-2 text-left">Amount</th>
              <th className="p-2 text-left">Actual</th>
              <th className="p-2 text-left">Prediction</th>
              <th className="p-2 text-left">Probability</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((row: any) => (
              <tr key={row._id} className="border-t cursor-pointer hover:bg-[#212121]" onClick={() => getTransaction(row._id).then(setDetail)}>
                <td className="p-2">{row._id}</td>
                <td className="p-2">{row.amount ?? '—'}</td>
                <td className="p-2">{row.actual_class ?? '—'}</td>
                <td className="p-2">{row.prediction === '1.0' ? 'Fraud' : 'Legitimate'}</td>
                <td className="p-2">{row.fraud_probability}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex gap-2 mt-4">
        <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="px-3 py-1 border rounded disabled:opacity-50">Prev</button>
        <span className="px-3 py-1">Page {page} of {Math.max(1, Math.ceil(data.total / 25))}</span>
        <button disabled={page * 25 >= data.total} onClick={() => setPage((p) => p + 1)} className="px-3 py-1 border rounded disabled:opacity-50">Next</button>
      </div>
      {detail && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center" onClick={() => setDetail(null)}>
          <div className="bg-[#191919] rounded shadow p-6 w-full max-w-lg" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold mb-2">Transaction {detail._id}</h3>
            <pre className="text-xs bg-[#212121] p-3 rounded overflow-auto">{JSON.stringify(detail, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}
