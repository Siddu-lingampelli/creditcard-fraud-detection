import axios from 'axios'

export const api = axios.create({ baseURL: '/api' })

export async function health() {
  const { data } = await api.get('/health')
  return data
}

export async function getDatasets() {
  const { data } = await api.get('/datasets')
  return data.datasets as any[]
}

export async function uploadDataset(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/dataset/upload', form)
  return data
}

export async function getDataset(id: string) {
  const { data } = await api.get(`/dataset/${id}`)
  return data
}

export async function train(datasetId: string, params: any) {
  const { data } = await api.post('/jobs/train', null, { params: { dataset_id: datasetId, ...params } })
  return data
}

export async function predict(datasetId: string, modelJobId?: string) {
  const { data } = await api.post('/jobs/predict', null, { params: { dataset_id: datasetId, model_job_id: modelJobId } })
  return data
}

export async function getJob(id: string) {
  const { data } = await api.get(`/jobs/${id}`)
  return data
}

export async function getMetrics(jobId?: string) {
  const { data } = await api.get('/metrics', { params: jobId ? { job_id: jobId } : {} })
  return data
}

export async function getSummary() {
  const { data } = await api.get('/summary')
  return data
}

export async function getTransactions(params: any) {
  const { data } = await api.get('/transactions', { params })
  return data
}

export async function getTransaction(id: number, jobId?: string) {
  const { data } = await api.get(`/transactions/${id}`, { params: jobId ? { job_id: jobId } : {} })
  return data
}
export async function getJobs() {
  const { data } = await api.get('/jobs')
  return data
}
