import { useEffect, useState } from 'react'
import { getJobs } from '../api'

export default function Jobs() {
  const [jobs, setJobs] = useState<any[]>([])

  useEffect(() => {
    getJobs().then((d: any) => setJobs(d.jobs || [])).catch(() => {})
  }, [])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Jobs</h2>
      {jobs.length === 0 && <p>No jobs yet.</p>}
      {jobs.map((job) => (
        <div key={job.job_id} className="bg-[#191919] rounded shadow p-4 mb-3">
          <p className="font-semibold">{job.job_type} — {job.status}</p>
          <p className="text-sm text-[#686868]">Job ID: {job.job_id}</p>
          <p className="text-sm text-[#686868]">Dataset: {job.dataset_id}</p>
          <p className="text-sm text-[#686868]">Created: {new Date(job.created_at * 1000).toLocaleString()}</p>
          {job.error && <p className="text-red-600 text-sm">{job.error}</p>}
        </div>
      ))}
    </div>
  )
}
