import { NavLink, Outlet, useLocation, Navigate } from 'react-router-dom'
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
    <div className="pixel-font" style={{ width: '100%', minHeight: '100vh', backgroundColor: '#1a1a1a' }}>
      <header 
        className="pixel-panel" 
        style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: '#2b2b2b' }}
        onMouseDown={(e) => e.preventDefault()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1400px', margin: '0 auto' }}>
          <h2 style={{ margin: 0, color: '#9ddc2d', textShadow: '2px 2px #000', marginRight: '2rem' }}>
            Admin Dashboard
          </h2>
          <nav style={{ display: 'flex', gap: '0.75rem' }}>
            <NavLink 
              to="/admin/high-scores" 
              className={({ isActive, isPending }) => {
                // Match both /admin and /admin/high-scores
                const path = location.pathname
                const shouldBeActive = path === '/admin' || path === '/admin/' || path === '/admin/high-scores' || isActive
                return shouldBeActive ? 'pixel-button' : 'pixel-button-inactive'
              }}
              style={{ textDecoration: 'none' }}
            >
              High Scores
            </NavLink>
            <NavLink 
              to="/admin/adjust-score" 
              className={({ isActive }) => 
                isActive 
                  ? 'pixel-button' 
                  : 'pixel-button-inactive'
              }
              style={{ textDecoration: 'none' }}
            >
              Adjust Score
            </NavLink>
          </nav>
        </div>
      </header>
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 1rem', paddingBottom: '2rem' }}>
        <Outlet />
      </main>
    </div>
  )
}


