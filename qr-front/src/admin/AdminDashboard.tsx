import { useEffect, useMemo, useState } from 'react'
import { fetchAllResults, fetchUsers, updateResult } from './api'
import type { AdminResult, UsersResponse } from './api'
import './styles/pixel.css'

type SortKey = 'score' | 'name' | 'email'

function sortResults(results: AdminResult[], sortBy: SortKey): AdminResult[] {
  const copy = [...results]
  if (sortBy === 'score') {
    copy.sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
  } else if (sortBy === 'name') {
    copy.sort((a, b) => a.user.name.localeCompare(b.user.name))
  } else if (sortBy === 'email') {
    copy.sort((a, b) => a.user.email.localeCompare(b.user.email))
  }
  return copy
}

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<AdminResult[]>([])
  const [users, setUsers] = useState<UsersResponse['users']>([])
  const [sortBy, setSortBy] = useState<SortKey>('score')
  const [filterGameId, setFilterGameId] = useState<string>('')

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const [res, us] = await Promise.all([
          fetchAllResults(filterGameId ? { game_id: filterGameId } : undefined),
          fetchUsers(),
        ])
        if (!mounted) return
        setResults(res.results || [])
        setUsers(us.users || [])
      } catch (e: any) {
        setError(e?.response?.data?.error || e?.message || 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [filterGameId])

  const sorted = useMemo(() => sortResults(results, sortBy), [results, sortBy])

  return (
    <div className="pixel-app-container">
      <header className="pixel-header">
        <h1 className="pixel-title">Admin Dashboard</h1>
        <nav className="pixel-nav">
          <a href="/" className="pixel-link">Home</a>
        </nav>
      </header>

      <section className="pixel-toolbar">
        <div className="pixel-field">
          <label className="pixel-label">Filter by Game ID</label>
          <input
            value={filterGameId}
            onChange={(e) => setFilterGameId(e.target.value)}
            placeholder="e.g. minecraft_build"
            className="pixel-input"
          />
        </div>
        <div className="pixel-field">
          <label className="pixel-label">Sort by</label>
          <select className="pixel-select" value={sortBy} onChange={(e) => setSortBy(e.target.value as SortKey)}>
            <option value="score">Score (desc)</option>
            <option value="name">Name (A-Z)</option>
            <option value="email">Email (A-Z)</option>
          </select>
        </div>
      </section>

      {loading && <div className="pixel-panel">Loading...</div>}
      {error && <div className="pixel-panel pixel-error">{error}</div>}

      {!loading && !error && (
        <div className="pixel-grid">
          <div className="pixel-panel">
            <h2 className="pixel-subtitle">High Scores</h2>
            <TopPlayersTable results={sorted} />
          </div>

          <div className="pixel-panel">
            <h2 className="pixel-subtitle">Add/Adjust Score</h2>
            <AddScoreForm users={users} results={results} onUpdated={(r) => {
              setResults((prev) => prev.map((x) => (x.result_id === r.result_id ? r : x)))
            }} />
          </div>
        </div>
      )}
    </div>
  )
}

function TopPlayersTable({ results }: { results: AdminResult[] }) {
  return (
    <div className="pixel-table-wrapper">
      <table className="pixel-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Player</th>
            <th>Email</th>
            <th>Team</th>
            <th>Game</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, idx) => (
            <tr key={r.result_id}>
              <td>{idx + 1}</td>
              <td>{r.user?.name}</td>
              <td>{r.user?.email}</td>
              <td>{r.team?.team_name || r.team?.team_id || '-'}</td>
              <td>{r.game?.name || r.game?.game_id || '-'}</td>
              <td>{r.score ?? 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function AddScoreForm({
  users,
  results,
  onUpdated,
}: {
  users: UsersResponse['users']
  results: AdminResult[]
  onUpdated: (result: AdminResult) => void
}) {
  const [resultId, setResultId] = useState<string>('')
  const [delta, setDelta] = useState<number>(0)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const options = useMemo(() => {
    return results.map((r) => ({
      value: r.result_id,
      label: `${r.user?.name} — ${r.game?.name || r.game?.game_id || 'N/A'} — current ${r.score ?? 0}`,
    }))
  }, [results])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null)
    if (!resultId) {
      setErr('Select a result to modify')
      return
    }
    setBusy(true)
    try {
      const current = results.find((r) => r.result_id === resultId)
      const newScore = (current?.score ?? 0) + Number(delta || 0)
      const updated = await updateResult(resultId, { score: newScore, verified_by_admin: true })
      onUpdated(updated)
      setDelta(0)
    } catch (e: any) {
      setErr(e?.response?.data?.error || e?.message || 'Failed to update score')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="pixel-form">
      <div className="pixel-field">
        <label className="pixel-label">Result</label>
        <select className="pixel-select" value={resultId} onChange={(e) => setResultId(e.target.value)}>
          <option value="">Select player/game</option>
          {options.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div className="pixel-field">
        <label className="pixel-label">Score Delta</label>
        <input
          type="number"
          className="pixel-input"
          value={String(delta)}
          onChange={(e) => setDelta(Number(e.target.value || 0))}
        />
      </div>

      {err && <div className="pixel-error">{err}</div>}

      <button className="pixel-button" disabled={busy}>
        {busy ? 'Saving...' : 'Apply'}
      </button>
    </form>
  )
}


