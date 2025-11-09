import { useEffect, useMemo, useState } from 'react'
import type { AdminResult } from '../api/client'
import { fetchAllResults } from '../api/client'

type Leader = {
  user: string
  user_name: string
  total_points: number
}

export function HighScores() {
  const [results, setResults] = useState<AdminResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await fetchAllResults()
        setResults(data.results)
      } catch (err: any) {
        setError(err?.response?.data?.error || 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const leaders = useMemo<Leader[]>(() => {
    const map = new Map<string, Leader>()
    for (const r of results) {
      const existing = map.get(r.user) || { user: r.user, user_name: r.user_name, total_points: 0 }
      existing.total_points += r.points_scored
      map.set(r.user, existing)
    }
    return Array.from(map.values()).sort((a, b) => b.total_points - a.total_points).slice(0, 50)
  }, [results])

  return (
    <div>
      <h2>High Scores</h2>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: '#ff6b6b' }}>{error}</div>}
      {!loading && !error && (
        <div className="pixel-panel" style={{ padding: '1rem' }}>
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '0.5rem' }}>#</th>
                <th style={{ textAlign: 'left', padding: '0.5rem' }}>Player</th>
                <th style={{ textAlign: 'right', padding: '0.5rem' }}>Total Points</th>
              </tr>
            </thead>
            <tbody>
              {leaders.map((l, idx) => (
                <tr key={l.user}>
                  <td style={{ padding: '0.5rem' }}>{idx + 1}</td>
                  <td style={{ padding: '0.5rem' }}>{l.user_name}</td>
                  <td style={{ padding: '0.5rem', textAlign: 'right' }}>{l.total_points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


