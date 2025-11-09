import { Link, NavLink, Outlet, useLocation, Navigate } from 'react-router-dom'
import { storage } from '../api/client'

function isAuthenticated() {
  return !!storage.token
}

export function DashboardLayout() {
  const location = useLocation()

  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return (
    <div className="pixel-font" style={{ width: '100%', minHeight: '100vh' }}>
      <header className="pixel-panel" style={{ padding: '1rem' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to="/admin" style={{ textDecoration: 'none', color: 'inherit' }}>
            <h2 style={{ margin: 0 }}>Admin Dashboard</h2>
          </Link>
          <nav style={{ display: 'flex', gap: '1rem' }}>
            <NavLink to="/admin/high-scores" className={({ isActive }) => isActive ? 'pixel-button' : ''}>
              High Scores
            </NavLink>
            <NavLink to="/admin/adjust-score" className={({ isActive }) => isActive ? 'pixel-button' : ''}>
              Adjust Score
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="container" style={{ paddingTop: '1rem', paddingBottom: '2rem' }}>
        <Outlet />
      </main>
    </div>
  )
}


