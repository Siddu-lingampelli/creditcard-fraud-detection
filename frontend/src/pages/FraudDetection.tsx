import { useEffect, useState } from 'react'
import { getDatasets, uploadDataset, train, predict, getJob } from '../api'

export default function FraudDetection() {
  const [datasets, setDatasets] = useState<any[]>([{ dataset_id: 'default', original_filename: 'creditcard.csv (default)' }])
  const [selected, setSelected] = useState<string>('default')
  const [jobId, setJobId] = useState<string>('')
  const [job, setJob] = useState<any>(null)
  const [error, setError] = useState('')

  function loadDatasets() {
    getDatasets()
      .then((ds) => {
        if (Array.isArray(ds) && ds.length) {
          const merged = [ { dataset_id: 'default', original_filename: 'creditcard.csv (default)' }, ...ds.filter((d: any) => d.dataset_id !== 'default') ]
          setDatasets(merged)
          if (!selected) setSelected('default')
        }
      })
      .catch((e) => setError(e?.message || 'Failed to load datasets'))
  }

  useEffect(() => {
    loadDatasets()
  }, [])

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const summary = await uploadDataset(file)
      setDatasets((prev) => [summary, ...prev])
      setSelected(summary.dataset_id)
    } catch (err: any) {
      setError(err.message)
    }
  }

  async function runTraining() {
    if (!selected) return
    try {
      const res = await train(selected, { test_size: 0.2, seed: 42, threshold: 0.5 })
      setJobId(res.job_id)
    } catch (err: any) {
      setError(err.message)
    }
  }

  async function runPrediction() {
    if (!selected) return
    try {
      const res = await predict(selected)
      setJobId(res.job_id)
    } catch (err: any) {
      setError(err.message)
    }
  }

  useEffect(() => {
    if (!jobId) return
    const timer = setInterval(() => {
      getJob(jobId).then(setJob).catch((e) => setError(e.message))
    }, 2000)
    return () => clearInterval(timer)
  }, [jobId])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Fraud Detection</h2>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      <div className="bg-[#191919] rounded shadow p-4 mb-6">
        <label className="block mb-2 font-medium">Upload CSV dataset</label>
        <input type="file" accept=".csv" onChange={handleUpload} />
      </div>
      <div className="bg-[#191919] rounded shadow p-4 mb-6">
        <label className="block mb-2 font-medium">Select dataset</label>
        <div className="flex gap-2">
          <select className="border rounded p-2 w-full bg-[#212121] text-[#ebebeb]" value={selected} onChange={(e) => setSelected(e.target.value)}>
            {datasets.map((d) => (
              <option key={d.dataset_id} value={d.dataset_id}>{d.original_filename || d.name}</option>
            ))}
          </select>
          <button onClick={loadDatasets} className="px-3 py-2 border rounded">Refresh</button>
        </div>
        <div className="flex gap-3 mt-4">
          <button onClick={runTraining} className="bg-[#dd7627] text-[#121212] px-4 py-2 rounded">Train & Evaluate</button>
          <button onClick={runPrediction} className="bg-[#212121] text-[#ebebeb] px-4 py-2 rounded border border-[#191919]">Predict Only</button>
        </div>
      </div>
      {job && (
        <div className="bg-[#191919] rounded shadow p-4">
          <p>Status: {job.status}</p>
          <p>Progress: {Math.round((job.progress || 0) * 100)}%</p>
          <p>{job.message}</p>
          {job.error && <p className="text-red-600">{job.error}</p>}
        </div>
      )}
    </div>
  )
}
