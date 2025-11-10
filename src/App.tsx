import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import './index.css'
import { Login } from './pages/Login'
import { DashboardLayout } from './pages/DashboardLayout'
import { HighScores } from './pages/HighScores'
import { AdjustScore } from './pages/AdjustScore'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/admin" element={<DashboardLayout />}>
        <Route index element={<HighScores />} />
        <Route path="high-scores" element={<HighScores />} />
        <Route path="adjust-score" element={<AdjustScore />} />
      </Route>
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>
  )
}

export default App
