import { useEffect, useMemo, useState } from 'react'
import { fetchAllResults, fetchUsers, updateResult, createResult } from './api'
import type { AdminResult, UsersResponse } from './api'
import './styles/pixel.css'

type SortKey = 'score' | 'name' | 'email'

// Helper function to deduplicate results by result_id
function deduplicateResults(results: AdminResult[]): AdminResult[] {
    return Array.from(
        new Map(results.map(r => [r.result_id, r])).values()
    )
}

export default function AdminDashboard() {
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [results, setResults] = useState<AdminResult[]>([])
    const [users, setUsers] = useState<UsersResponse['users']>([])
    const [sortBy, setSortBy] = useState<SortKey>('score')
    const [filterGameId, setFilterGameId] = useState<string>('')
    
    // Wrapper for setResults that always deduplicates
    const setResultsDeduped = (newResults: AdminResult[] | ((prev: AdminResult[]) => AdminResult[])) => {
        setResults(prev => {
            const next = typeof newResults === 'function' ? newResults(prev) : newResults
            const deduped = deduplicateResults(next)
            // Debug: Check for duplicates
            const ids = deduped.map(r => r.result_id)
            const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index)
            if (duplicates.length > 0) {
                console.warn('Found duplicate result_ids after deduplication:', duplicates)
                console.warn('Full results array:', deduped)
            }
            return deduped
        })
    }

    useEffect(() => {
        let mounted = true
        async function load() {
            setLoading(true)
            setError(null)
            try {
                const [us] = await Promise.all([
                    fetchUsers(),
                ])
                if (!mounted) return
                
                const usersList = us.users || []
                // Create users map for email lookup
                const usersMap = new Map(usersList.map(u => [u.id, u.email]))
                
                // Now fetch results with users map for email mapping
                const res = await fetchAllResults(filterGameId ? { game_id: filterGameId } : undefined, usersMap)
                let resultsList = res.results || []
                
                // Immediately deduplicate the fetched results
                resultsList = deduplicateResults(resultsList)
                
                // Debug: Check for duplicates in API response
                const ids = resultsList.map(r => r.result_id)
                const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index)
                if (duplicates.length > 0) {
                    console.warn('API returned duplicate result_ids:', duplicates)
                }
                
                // Create a set of user IDs that have results (for the current filter)
                const usersWithResults = new Set(resultsList.map(r => r.user?.id).filter(Boolean))
                
                // Automatically create default results for users without any results
                const usersWithoutResults = usersList.filter(u => !usersWithResults.has(u.id))
                
                if (usersWithoutResults.length > 0) {
                    console.log(`Creating default results for ${usersWithoutResults.length} users without results`)
                    // Create results for users without them
                    // If filtering by game, create results for that specific game
                    const createPromises = usersWithoutResults.map(user => {
                        const createData: { score?: number; game_id?: string } = { score: 1 }
                        if (filterGameId) {
                            createData.game_id = filterGameId
                        }
                        return createResult(user.id, createData).catch(err => {
                            console.error(`Failed to create default result for user ${user.id}:`, err)
                            console.error('Error details:', err?.response?.data || err?.message)
                            return null
                        })
                    })
                    
                    const createResults = await Promise.all(createPromises)
                    const successCount = createResults.filter(r => r !== null).length
                    console.log(`Successfully created ${successCount} out of ${usersWithoutResults.length} default results`)
                    
                    // Reload results to get the newly created ones with all their data
                    const refreshedRes = await fetchAllResults(filterGameId ? { game_id: filterGameId } : undefined, usersMap)
                    setResultsDeduped(refreshedRes.results || [])
                } else {
                    setResultsDeduped(resultsList)
                }
                
                setUsers(usersList)
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

    // Create a merged list of all users with their results
    // This ensures all users appear, even if they have no results
    const allPlayersWithScores = useMemo(() => {
        // Results should already be deduplicated, but ensure it here too
        const uniqueResults = deduplicateResults(results)
        
        // Create a map of user ID to their results
        const userResultsMap = new Map<string, AdminResult[]>()
        uniqueResults.forEach((result) => {
            const userId = result.user?.id
            if (userId) {
                if (!userResultsMap.has(userId)) {
                    userResultsMap.set(userId, [])
                }
                userResultsMap.get(userId)!.push(result)
            }
        })

        // Create entries for all users, including those without results
        const playerEntries: Array<{
            user: { id: string; name: string; email: string }
            results: AdminResult[]
            bestScore: number
            bestResult: AdminResult | null
        }> = []

        users.forEach((user) => {
            const userResults = userResultsMap.get(user.id) || []
            // Get the best (highest) score for this user
            const bestResult = userResults.length > 0
                ? userResults.reduce((best, current) => {
                    const currentScore = current.score ?? (current as any).points_scored ?? 0
                    const bestScore = best.score ?? (best as any).points_scored ?? 0
                    return currentScore > bestScore ? current : best
                  })
                : null
            const bestScore = bestResult ? (bestResult.score ?? (bestResult as any).points_scored ?? 0) : 0

            playerEntries.push({
                user: {
                    id: user.id,
                    name: user.name,
                    email: user.email,
                },
                results: userResults,
                bestScore,
                bestResult,
            })
        })

        return playerEntries
    }, [users, results])

    const sortedPlayers = useMemo(() => {
        const copy = [...allPlayersWithScores]
        if (sortBy === 'score') {
            copy.sort((a, b) => b.bestScore - a.bestScore)
        } else if (sortBy === 'name') {
            copy.sort((a, b) => a.user.name.localeCompare(b.user.name))
        } else if (sortBy === 'email') {
            copy.sort((a, b) => a.user.email.localeCompare(b.user.email))
        }
        return copy
    }, [allPlayersWithScores, sortBy])

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
                        <TopPlayersTable players={sortedPlayers} />
                    </div>

                    <div className="pixel-panel">
                        <h2 className="pixel-subtitle">Add/Adjust Score</h2>
                        <AddScoreForm users={users} results={results} onUpdated={(r) => {
                            setResultsDeduped((prev) => {
                                const existing = prev.find((x) => x.result_id === r.result_id)
                                if (existing) {
                                    return prev.map((x) => (x.result_id === r.result_id ? r : x))
                                } else {
                                    return [...prev, r]
                                }
                            })
                        }} />
                    </div>
                </div>
            )}
        </div>
    )
}

type PlayerWithScore = {
    user: { id: string; name: string; email: string }
    results: AdminResult[]
    bestScore: number
    bestResult: AdminResult | null
}

function TopPlayersTable({ players }: { players: PlayerWithScore[] }) {
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
                    {players.map((player, idx) => (
                        <tr key={player.user.id}>
                            <td>{idx + 1}</td>
                            <td>{player.user.name}</td>
                            <td>{player.user.email}</td>
                            <td>{player.bestResult?.team?.team_name || player.bestResult?.team?.team_id || '-'}</td>
                            <td>{player.bestResult?.game?.name || player.bestResult?.game?.game_id || '-'}</td>
                            <td>{player.bestScore}</td>
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

    // Create options from all users, deduplicated by user ID
    // For each user, show their results (or indicate no results)
    const options = useMemo(() => {
        // Results should already be deduplicated, but ensure it here too
        const uniqueResults = deduplicateResults(results)
        
        // Group results by user ID to avoid duplicates
        const userResultsMap = new Map<string, AdminResult[]>()
        uniqueResults.forEach((r) => {
            const userId = r.user?.id
            if (userId) {
                if (!userResultsMap.has(userId)) {
                    userResultsMap.set(userId, [])
                }
                userResultsMap.get(userId)!.push(r)
            }
        })

        const optionsList: Array<{ value: string; label: string; userId: string }> = []

        // Add all users, including those without results
        users.forEach((user) => {
            const userResults = userResultsMap.get(user.id) || []
            
            if (userResults.length === 0) {
                // User has no results - show them with score 0
                // We'll need to handle this case when submitting
                optionsList.push({
                    value: `user_${user.id}`,
                    label: `${user.name} — No results yet (score: 0)`,
                    userId: user.id,
                })
            } else {
                // User has results - show each result
                // Deduplicate by result_id to avoid duplicate options
                const seenResultIds = new Set<string>()
                userResults.forEach((result) => {
                    if (!seenResultIds.has(result.result_id)) {
                        seenResultIds.add(result.result_id)
                        optionsList.push({
                            value: result.result_id,
                            label: `${result.user?.name || user.name} — ${result.game?.name || result.game?.game_id || 'N/A'} — current ${result.score ?? 0}`,
                            userId: user.id,
                        })
                    }
                })
            }
        })

        // Final deduplication by value to ensure no duplicate keys
        const seenValues = new Set<string>()
        const finalOptions = optionsList.filter(opt => {
            if (seenValues.has(opt.value)) {
                console.warn(`Duplicate option value found: ${opt.value}`, opt)
                return false
            }
            seenValues.add(opt.value)
            return true
        })
        
        // Debug: Log if we still have duplicates
        const values = finalOptions.map(o => o.value)
        const duplicateValues = values.filter((v, i) => values.indexOf(v) !== i)
        if (duplicateValues.length > 0) {
            console.error('Still have duplicate option values after filtering:', duplicateValues)
        }
        
        return finalOptions
    }, [users, results])

    async function submit(e: React.FormEvent) {
        e.preventDefault()
        setErr(null)
        if (!resultId) {
            setErr('Select a player to modify')
            return
        }
        setBusy(true)
        try {
            // Check if this is a user without results (starts with "user_")
            if (resultId.startsWith('user_')) {
                // Extract user ID and create a default result
                const userId = resultId.replace('user_', '')
                try {
                    const newResult = await createResult(userId, { score: 1 })
                    // Now update the newly created result with the delta
                    const finalScore = 1 + Number(delta || 0)
                    if (finalScore < 0) {
                        setErr('Score cannot be negative')
                        setBusy(false)
                        return
                    }
                    const updated = await updateResult(newResult.result_id, { score: finalScore, verified_by_admin: true })
                    onUpdated(updated)
                    setDelta(0)
                    setResultId('') // Reset selection after successful update
                } catch (createErr: any) {
                    setErr(createErr?.response?.data?.error || createErr?.message || 'Failed to create result for player')
                }
                return
            }

            const current = results.find((r) => r.result_id === resultId)
            if (!current) {
                setErr('Result not found')
                setBusy(false)
                return
            }

            const newScore = (current.score ?? 0) + Number(delta || 0)
            
            if (newScore < 0) {
                setErr('Score cannot be negative')
                setBusy(false)
                return
            }
            
            const updated = await updateResult(resultId, { score: newScore, verified_by_admin: true })
            onUpdated(updated)
            setDelta(0)
            setResultId('') // Reset selection after successful update
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
                    {options.map((o, idx) => {
                        // Ensure unique keys - use index as fallback if value is duplicate
                        // But first check if we have duplicates
                        const key = `${o.value}-${idx}`
                        return (
                            <option key={key} value={o.value}>{o.label}</option>
                        )
                    })}
                </select>
            </div>

            <div className="pixel-field">
                <label className="pixel-label">Score Delta</label>
                <input
                    type="number"
                    className="pixel-input"
                    value={String(delta)}
                    onChange={(e) => {
                        const value = Number(e.target.value || 0)
                        setDelta(value)
                    }}
                    title="Enter score adjustment"
                />
                <small style={{ display: 'block', marginTop: '0.25rem', opacity: 0.7 }}>
                    {resultId && !resultId.startsWith('user_') ? (
                        <>
                            Current: {results.find((r) => r.result_id === resultId)?.score ?? 0} | New: {(results.find((r) => r.result_id === resultId)?.score ?? 0) + Number(delta || 0)}
                        </>
                    ) : resultId && resultId.startsWith('user_') ? (
                        <>This player has no results yet. They need to play a game first.</>
                    ) : (
                        <>Select a player to see current score</>
                    )}
                </small>
            </div>

            {err && <div className="pixel-error">{err}</div>}

            <button className="pixel-button" disabled={busy}>
                {busy ? 'Saving...' : 'Apply'}
            </button>
        </form>
    )
}
