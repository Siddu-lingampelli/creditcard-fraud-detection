import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router-dom'
import { useState } from 'react'
import Overview from './pages/Overview'
import Transactions from './pages/Transactions'
import FraudDetection from './pages/FraudDetection'
import ModelPerformance from './pages/ModelPerformance'
import Dataset from './pages/Dataset'
import Jobs from './pages/Jobs'
import About from './pages/About'

const nav = [
  ['Overview', '/'],
  ['Transactions', '/transactions'],
  ['Fraud Detection', '/fraud'],
  ['Model Performance', '/performance'],
  ['Dataset', '/dataset'],
  ['Jobs', '/jobs'],
  ['About', '/about'],
]

function Shell() {
  const location = useLocation()
  const [open, setOpen] = useState(false)
  return (
    <div className="min-h-screen bg-[#121212] text-[#ebebeb]">
      <div className="md:hidden flex items-center justify-between p-4 border-b border-[#191919]">
        <h1 className="text-lg font-bold">Fraud Analytics</h1>
        <button onClick={() => setOpen(!open)} className="px-3 py-1 border border-[#191919] rounded">Menu</button>
      </div>
      {open && (
        <nav className="md:hidden bg-[#121212] border-b border-[#191919] p-4 space-y-2">
          {nav.map(([label, path]) => (
            <Link key={path} to={path} onClick={() => setOpen(false)} className={`block rounded px-3 py-2 ${location.pathname === path ? 'bg-[#dd7627] text-[#121212]' : 'hover:bg-[#212121]'}`}>
              {label}
            </Link>
          ))}
        </nav>
      )}
      <div className="flex">
        <aside className="hidden md:block w-64 min-h-screen bg-[#121212] text-[#ebebeb] p-6 border-r border-[#191919]">
          <h1 className="text-xl font-bold mb-2">Fraud Analytics</h1>
          <p className="text-sm text-[#686868] mb-8">Credit card fraud detection</p>
          <nav className="space-y-2">
            {nav.map(([label, path]) => (
              <Link key={path} to={path} className={`block rounded px-3 py-2 ${location.pathname === path ? 'bg-[#dd7627] text-[#121212]' : 'hover:bg-[#212121]'}`}>
                {label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="flex-1 p-4 md:p-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/fraud" element={<FraudDetection />} />
            <Route path="/performance" element={<ModelPerformance />} />
            <Route path="/dataset" element={<Dataset />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/about" element={<About />} />
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
