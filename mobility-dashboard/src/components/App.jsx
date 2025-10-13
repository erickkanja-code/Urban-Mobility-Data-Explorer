import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import DashboardPage from './pages/DashboardPage'
import RoutesPage from './pages/RoutesPage'
import FaresPage from './pages/FaresPage'
import InsightsPage from './pages/InsightsPage'

export default function App() {
  return (
    <div className="min-h-screen flex bg-momoSlate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="p-6">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/routes" element={<RoutesPage />} />
            <Route path="/fares" element={<FaresPage />} />
            <Route path="/insights" element={<InsightsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
