import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/client'

export function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(email, password)
      if (data.user.role !== 'admin') {
        setError('Admin access required')
        setLoading(false)
        return
      }
      navigate('/admin')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container pixel-font" style={{ width: '100%' }}>
      <h1 style={{ textAlign: 'center' }}>Admin Login</h1>
      <form onSubmit={onSubmit} style={{ maxWidth: 520, margin: '2rem auto' }} className="pixel-panel">
        <div style={{ display: 'grid', gap: '1rem', padding: '1rem' }}>
          <label>
            <div style={{ marginBottom: 8 }}>Email</div>
            <input className="pixel-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            <div style={{ marginBottom: 8 }}>Password</div>
            <input className="pixel-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          {error && <div style={{ color: '#ff6b6b' }}>{error}</div>}
          <button className="pixel-button" type="submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign In'}</button>
        </div>
      </form>
    </div>
  )
}


