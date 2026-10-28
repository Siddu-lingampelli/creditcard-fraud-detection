import { useEffect, useState } from 'react'
import { getDatasets } from '../api'

export default function Dataset() {
  const [datasets, setDatasets] = useState<any[]>([])

  useEffect(() => {
    getDatasets().then(setDatasets).catch(() => {})
  }, [])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dataset</h2>
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
