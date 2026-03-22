import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Trips from './pages/Trips'
import Charging from './pages/Charging'
import Comparison from './pages/Comparison'
import Settings from './pages/Settings'
import Connect from './pages/Connect'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/connect" element={<Connect />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/trips" element={<Trips />} />
          <Route path="/charging" element={<Charging />} />
          <Route path="/comparison" element={<Comparison />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
