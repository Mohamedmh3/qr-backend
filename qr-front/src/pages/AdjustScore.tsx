import { useEffect, useState } from 'react'
import type { AdminResult } from '../api/client'
import { fetchAllResults, updateResult } from '../api/client'

export function AdjustScore() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<AdminResult[]>([])
  const [error, setError] = useState('')
  const [savingId, setSavingId] = useState<string | null>(null)

  async function search() {
    setLoading(true)
    setError('')
    try {
      // Allow searching by user_id or email (backend supports user_id param either id or email)
      const data = await fetchAllResults(query ? { user_id: query } : undefined)
      setResults(data.results)
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Failed to load results')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    search()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function savePoints(result: AdminResult, newPoints: number) {
    try {
      setSavingId(result.result_id)
      const updated = await updateResult(result.result_id, { points_scored: newPoints })
      setResults((prev) => prev.map((r) => (r.result_id === result.result_id ? { ...r, ...updated } : r)))
    } catch (err: any) {
      alert(err?.response?.data?.error || 'Update failed')
    } finally {
      setSavingId(null)
    }
  }

  return (
    <div>
      <h2>Adjust Score</h2>
      <div className="pixel-panel" style={{ padding: '1rem', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <input
            className="pixel-input"
            placeholder="Search by User ID or Email"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ flex: 1 }}
          />
          <button className="pixel-button" onClick={search}>Search</button>
        </div>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div style={{ color: '#ff6b6b' }}>{error}</div>}

      {!loading && !error && (
        <div className="pixel-panel" style={{ padding: '1rem' }}>
          {results.length === 0 ? (
            <div>No results found.</div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Player</th>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Game</th>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Team</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>Points</th>
                  <th style={{ padding: '0.5rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.result_id}>
                    <td style={{ padding: '0.5rem' }}>{r.user_name}</td>
                    <td style={{ padding: '0.5rem' }}>{r.game_name}</td>
                    <td style={{ padding: '0.5rem' }}>{r.team_name}</td>
                    <td style={{ padding: '0.5rem', textAlign: 'right' }}>
                      <input
                        type="number"
                        className="pixel-input"
                        defaultValue={r.points_scored}
                        onChange={(e) => {
                          const val = Number(e.target.value)
                          setResults((prev) => prev.map((x) => (x.result_id === r.result_id ? { ...x, points_scored: val } : x)))
                        }}
                        style={{ width: 120, textAlign: 'right' }}
                      />
                    </td>
                    <td style={{ padding: '0.5rem' }}>
                      <button
                        className="pixel-button"
                        disabled={savingId === r.result_id}
                        onClick={() => savePoints(r, r.points_scored)}
                      >
                        {savingId === r.result_id ? 'Saving...' : 'Save'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}


