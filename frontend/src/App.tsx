import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router-dom'
import Overview from './pages/Overview'
import Transactions from './pages/Transactions'
import FraudDetection from './pages/FraudDetection'
import ModelPerformance from './pages/ModelPerformance'
import Dataset from './pages/Dataset'
import About from './pages/About'
import Jobs from './pages/Jobs'

const nav = [
  ['Overview', '/'],
  ['Transactions', '/transactions'],
  ['Fraud Detection', '/fraud'],
  ['Model Performance', '/performance'],
  ['Dataset', '/dataset'],
  ['About', '/about'],
  ['Jobs', '/jobs'],
]

function Shell() {
  const location = useLocation()
  return (
    <div className="min-h-screen bg-[#212121] text-[#ebebeb]">
      <div className="flex">
        <aside className="w-64 min-h-screen bg-slate-900 text-[#ebebeb] p-6">
          <h1 className="text-xl font-bold mb-2">Fraud Analytics</h1>
          <p className="text-sm text-slate-300 mb-8">Credit card fraud detection</p>
          <nav className="space-y-2">
            {nav.map(([label, path]) => (
              <Link
                key={path}
                to={path}
                className={`block rounded px-3 py-2 ${location.pathname === path ? 'bg-[#dd7627]' : 'hover:bg-[#212121]'}`}
              >
                {label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="flex-1 p-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/fraud" element={<FraudDetection />} />
            <Route path="/performance" element={<ModelPerformance />} />
            <Route path="/dataset" element={<Dataset />} />
            <Route path="/about" element={<About />} />
            <Route path="/jobs" element={<Jobs />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Shell />
    </BrowserRouter>
  )
}

