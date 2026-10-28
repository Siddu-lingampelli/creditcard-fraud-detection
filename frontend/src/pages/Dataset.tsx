import { useEffect, useState } from 'react'
import { getDatasets, uploadDataset } from '../api'

export default function Dataset() {
  const [datasets, setDatasets] = useState<any[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    getDatasets().then(setDatasets).catch(() => {})
  }, [])

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const summary = await uploadDataset(file)
      setDatasets((prev) => [summary, ...prev])
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dataset</h2>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      <div className="bg-[#191919] rounded shadow p-4 mb-6">
        <label className="block mb-2 font-medium">Upload CSV dataset</label>
        <input type="file" accept=".csv" onChange={handleUpload} className="block w-full text-sm text-[#ebebeb] file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-[#dd7627] file:text-[#121212]" />
      </div>
      {datasets.length === 0 && <p>No datasets uploaded yet.</p>}
      {datasets.map((d) => (
        <div key={d.dataset_id} className="bg-[#191919] rounded shadow p-4 mb-4">
          <p className="font-semibold">{d.original_filename || d.name}</p>
          <p className="text-sm text-[#686868]">Rows: {d.row_count} · Columns: {d.column_count}</p>
          <p className="text-sm text-[#686868]">Columns: {d.columns.join(', ')}</p>
          {d.class_counts && Object.keys(d.class_counts).length > 0 && (
            <p className="text-sm text-[#686868]">Class counts: {JSON.stringify(d.class_counts)}</p>
          )}
        </div>
      ))}
    </div>
  )
}
