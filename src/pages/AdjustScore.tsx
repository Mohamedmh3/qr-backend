import { useEffect, useState, useMemo } from 'react'
import type { AdminResult } from '../api/client'
import { fetchAllResults, updateResult, fetchGames, type Game } from '../api/client'
import { fetchUsers } from '../admin/api'

export function AdjustScore() {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [results, setResults] = useState<AdminResult[]>([])
    const [users, setUsers] = useState<Array<{ id: string; name: string; email: string }>>([])
    const [error, setError] = useState('')
    const [savingId, setSavingId] = useState<string | null>(null)
    const [savingGameId, setSavingGameId] = useState<string | null>(null)
    const [games, setGames] = useState<Game[]>([])
    const [gamesLoading, setGamesLoading] = useState(false)
    const [selectedResult, setSelectedResult] = useState<AdminResult | null>(null)
    const [showGamesPopup, setShowGamesPopup] = useState(false)

    async function loadGames() {
        setGamesLoading(true)
        try {
            const data = await fetchGames()
            setGames(data.games.filter(g => g.is_active))
        } catch (err: any) {
            console.error('Failed to load games:', err)
        } finally {
            setGamesLoading(false)
        }
    }

    // Helper to deduplicate results by result_id
    function deduplicateResults(results: AdminResult[]): AdminResult[] {
        return Array.from(
            new Map(results.map(r => [r.result_id, r])).values()
        )
    }

    async function loadData() {
        setLoading(true)
        setError('')
        try {
            // Fetch results first
            const resultsData = await fetchAllResults(query ? { user_id: query } : undefined)
            const resultsList = deduplicateResults(resultsData.results || [])
            console.log('Fetched results:', resultsList.length)
            setResults(resultsList)
            
            // Try to fetch users, but if it fails, extract users from results
            let usersList: Array<{ id: string; name: string; email: string }> = []
            try {
                const usersData = await fetchUsers()
                usersList = usersData.users || []
                console.log('Fetched users from API:', usersList.length)
                if (usersList.length > 0) {
                    setUsers(usersList)
                } else {
                    // Backend returned empty list - extract from results
                    console.warn('Users endpoint returned empty list, extracting from results')
                    usersList = extractUsersFromResults(resultsList)
                    setUsers(usersList)
                }
            } catch (usersErr: any) {
                console.warn('Failed to fetch users, extracting from results:', usersErr)
                usersList = extractUsersFromResults(resultsList)
                setUsers(usersList)
            }
            
            function extractUsersFromResults(results: AdminResult[]): Array<{ id: string; name: string; email: string }> {
                // Extract unique users from results
                const usersMap = new Map<string, { id: string; name: string; email: string }>()
                results.forEach((r) => {
                    const userId = typeof r.user === 'string' ? r.user : (r.user as any)?.id || ''
                    const userName = r.user_name || 'Unknown'
                    if (userId && !usersMap.has(userId)) {
                        usersMap.set(userId, {
                            id: userId,
                            name: userName,
                            email: '', // We don't have email in results
                        })
                    }
                })
                const extractedUsers = Array.from(usersMap.values())
                console.log('Extracted users from results:', extractedUsers.length)
                if (extractedUsers.length === 0 && results.length === 0) {
                    console.warn('No users found in results either. This might indicate a data issue.')
                }
                return extractedUsers
            }
        } catch (err: any) {
            setError(err?.response?.data?.error || 'Failed to load data')
        } finally {
            setLoading(false)
        }
    }

    async function search() {
        await loadData()
    }

    useEffect(() => {
        loadData()
        loadGames()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    async function addGameScore(result: AdminResult, game: Game) {
        // Check if this is a placeholder (user has no results yet)
        const isPlaceholder = result.result_id.startsWith('placeholder-')
        const userId = isPlaceholder ? result.result_id.replace('placeholder-', '') : (typeof result.user === 'string' ? result.user : (result.user as any)?.id || '')
        
        try {
            setSavingId(result.result_id)
            setSavingGameId(game.game_id)
            
            // Always create a NEW result for each game play
            // Each click of "Add Game" should create a separate result record
            const { createResult } = await import('../admin/api')
            const newResult = await createResult(userId, { 
                game_id: game.game_id, 
                score: game.max_points 
            })
            
            // Add the new result to the results list
            setResults((prev) => {
                const updated = [...prev, newResult]
                return deduplicateResults(updated)
            })
            
            // Reload data to ensure we have the latest from server
            // This ensures High Scores page will see the new results when it refreshes
            await loadData()
            
            // Don't close the popup - allow adding multiple games
            // Only close if it was a placeholder (user had no results)
            if (isPlaceholder) {
                setShowGamesPopup(false)
                setSelectedResult(null)
            }
        } catch (err: any) {
            alert(err?.response?.data?.error || 'Failed to add score')
        } finally {
            setSavingId(null)
            setSavingGameId(null)
        }
    }

    function openGamesPopup(result: AdminResult | null, user?: { id: string; name: string; email: string }) {
        if (result) {
            setSelectedResult(result)
            setShowGamesPopup(true)
        } else if (user) {
            // User has no results - create a placeholder result for them
            // This will be handled when they select a game
            const placeholderResult: AdminResult = {
                result_id: `placeholder-${user.id}`,
                user: user.id,
                user_name: user.name,
                team: '',
                team_name: '',
                game: '',
                game_name: '',
                points_scored: 0,
                score: 0,
                played_at: new Date().toISOString(),
                verified_by_admin: false,
            }
            setSelectedResult(placeholderResult)
            setShowGamesPopup(true)
        }
    }

    function closeGamesPopup() {
        setShowGamesPopup(false)
        setSelectedResult(null)
        setSavingId(null)
        setSavingGameId(null)
    }

    return (
        <div>
            <h2 style={{ color: '#9ddc2d', textShadow: '2px 2px #000', marginBottom: '1rem' }}>Adjust Score</h2>
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

            {loading && <div style={{ color: '#eaeaea', padding: '1rem', textAlign: 'center' }}>Loading...</div>}
            {error && <div className="pixel-error" style={{ marginBottom: '1rem' }}>{error}</div>}

            {!loading && !error && (
                <div className="pixel-panel" style={{ padding: '1rem' }}>
                    {(() => {
                        // If we have no users, extract from results as fallback
                        let usersToDisplay = users
                        if (users.length === 0 && results.length > 0) {
                            const usersMap = new Map<string, { id: string; name: string; email: string }>()
                            results.forEach((r) => {
                                const userId = typeof r.user === 'string' ? r.user : (r.user as any)?.id || ''
                                const userName = r.user_name || 'Unknown'
                                if (userId && !usersMap.has(userId)) {
                                    usersMap.set(userId, {
                                        id: userId,
                                        name: userName,
                                        email: '',
                                    })
                                }
                            })
                            usersToDisplay = Array.from(usersMap.values())
                        }
                        
                        // Create a map of user ID to their results
                        const userResultsMap = new Map<string, AdminResult[]>()
                        results.forEach((r) => {
                            const userId = typeof r.user === 'string' ? r.user : (r.user as any)?.id || ''
                            if (userId) {
                                if (!userResultsMap.has(userId)) {
                                    userResultsMap.set(userId, [])
                                }
                                userResultsMap.get(userId)!.push(r)
                            }
                        })

                        // Create display list: all users with their total score across all results
                        const displayList = usersToDisplay.map(user => {
                            const userResults = userResultsMap.get(user.id) || []
                            // Calculate total score across all results for this user
                            const totalScore = userResults.reduce((sum, r) => {
                                const score = (r.points_scored ?? r.score ?? 0)
                                return sum + (typeof score === 'number' ? score : parseInt(String(score), 10) || 0)
                            }, 0)
                            // Get the best result for display purposes (most recent or highest)
                            const bestResult = userResults.length > 0
                                ? userResults.reduce((best, current) => 
                                    ((current.points_scored ?? current.score ?? 0) > (best.points_scored ?? best.score ?? 0)) ? current : best
                                  )
                                : null
                            return {
                                user,
                                result: bestResult,
                                score: totalScore, // Show total score, not just best result
                            }
                        })

                        // Filter by query if provided
                        const filteredList = query 
                            ? displayList.filter(item => 
                                item.user.name.toLowerCase().includes(query.toLowerCase()) ||
                                item.user.email.toLowerCase().includes(query.toLowerCase()) ||
                                item.user.id.toLowerCase().includes(query.toLowerCase())
                              )
                            : displayList

                        if (filteredList.length === 0) {
                            return <div style={{ color: '#eaeaea', textAlign: 'center', padding: '2rem' }}>No players found.</div>
                        }

                        return (
                            <table className="pixel-table" style={{ width: '100%' }}>
                                <thead>
                                    <tr>
                                        <th style={{ textAlign: 'left', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Player</th>
                                        <th style={{ textAlign: 'left', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Team</th>
                                        <th style={{ textAlign: 'right', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Points</th>
                                        <th style={{ textAlign: 'left', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredList.map((item, idx) => {
                                        if (!item.result) {
                                            // User has no results - show with score 0
                                            return (
                                                <tr key={`user-${item.user.id}-${idx}`}>
                                                    <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea' }}>
                                                        {item.user.name}
                                                    </td>
                                                    <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea' }}>
                                                        -
                                                    </td>
                                                    <td style={{ padding: '0.75rem', textAlign: 'right', verticalAlign: 'middle', color: '#eaeaea', fontWeight: 'bold', fontSize: '1.1rem' }}>
                                                        0
                                                    </td>
                                                    <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle' }}>
                                                        <button
                                                            className="pixel-button"
                                                            onClick={() => openGamesPopup(null, item.user)}
                                                            disabled={savingId === `placeholder-${item.user.id}`}
                                                        >
                                                            Add Game
                                                        </button>
                                                    </td>
                                                </tr>
                                            )
                                        }
                                        return (
                                            <tr key={`${item.result.result_id}-${idx}`}>
                                                <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea' }}>
                                                    {item.result.user_name || item.user.name || 'Unknown Player'}
                                                </td>
                                                <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea' }}>
                                                    {item.result.team_name || 'Unknown Team'}
                                                </td>
                                                <td style={{ padding: '0.75rem', textAlign: 'right', verticalAlign: 'middle', color: '#eaeaea', fontWeight: 'bold', fontSize: '1.1rem' }}>
                                                    {item.score}
                                                </td>
                                                <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle' }}>
                                                    <button
                                                        className="pixel-button"
                                                        onClick={() => openGamesPopup(item.result!)}
                                                        disabled={savingId === item.result!.result_id}
                                                    >
                                                        Add Game
                                                    </button>
                                                </td>
                                            </tr>
                                        )
                                    })}
                                </tbody>
                            </table>
                        )
                    })()}
                </div>
            )}

            {/* Games Popup Modal */}
            {showGamesPopup && selectedResult && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                    }}
                    onClick={closeGamesPopup}
                >
                    <div
                        className="pixel-panel"
                        style={{
                            padding: '1.5rem',
                            maxWidth: '700px',
                            width: '90%',
                            maxHeight: '85vh',
                            overflow: 'auto',
                            position: 'relative',
                            backgroundColor: '#2b2b2b',
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ margin: 0, color: '#9ddc2d', textShadow: '2px 2px #000' }}>Select Game to Add Score</h3>
                            <button
                                className="pixel-button"
                                onClick={closeGamesPopup}
                                style={{ padding: '0.5rem 1rem', fontSize: '1.2rem', lineHeight: 1, minWidth: 'auto' }}
                            >
                                ×
                            </button>
                        </div>

                        <div
                            className="pixel-panel"
                            style={{
                                marginBottom: '1.5rem',
                                padding: '1rem',
                                backgroundColor: '#1e1e1e',
                            }}
                        >
                            <div style={{ color: '#eaeaea', marginBottom: '0.5rem' }}>
                                <strong style={{ color: '#9ddc2d' }}>Player:</strong> {selectedResult.user_name || selectedResult.user || 'Unknown Player'}
                            </div>

                            {/* NEW: show player id on top of the list */}
                            <div style={{ color: '#eaeaea', marginBottom: '0.5rem' }}>
                                <strong style={{ color: '#9ddc2d' }}>Player ID:</strong>{' '}
                                <span style={{ color: '#eaeaea', fontFamily: 'monospace' }}>
                                    {selectedResult.user ?? (selectedResult as any).user_id ?? selectedResult.result_id}
                                </span>
                            </div>

                            <div style={{ color: '#eaeaea' }}>
                                <strong style={{ color: '#9ddc2d' }}>Current Score:</strong>{' '}
                                <span style={{ color: '#9ddc2d', fontSize: '1.2rem', fontWeight: 'bold' }}>
                                    {selectedResult.points_scored ?? selectedResult.score ?? 0}
                                </span>
                            </div>
                        </div>

                        {gamesLoading ? (
                            <div style={{ color: '#eaeaea', textAlign: 'center', padding: '2rem' }}>Loading games...</div>
                        ) : games.length === 0 ? (
                            <div style={{ color: '#eaeaea', textAlign: 'center', padding: '2rem' }}>No games available.</div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {games.map((game) => (
                                    <div
                                        key={game.game_id}
                                        className="pixel-panel"
                                        style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            padding: '1rem',
                                            backgroundColor: '#1e1e1e',
                                            border: '4px solid #000',
                                        }}
                                    >
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontWeight: 'bold', color: '#9ddc2d', marginBottom: '0.5rem', fontSize: '1.1rem' }}>
                                                {game.game_name}
                                            </div>
                                            {game.game_description && (
                                                <div style={{ fontSize: '0.9rem', color: '#cfcfcf', marginBottom: '0.5rem' }}>
                                                    {game.game_description}
                                                </div>
                                            )}
                                            <div style={{ fontSize: '0.85rem', color: '#eaeaea' }}>
                                                <span style={{ color: '#9ddc2d' }}>Score:</span> {game.max_points} points
                                            </div>
                                        </div>
                                        <button
                                            className="pixel-button"
                                            onClick={() => addGameScore(selectedResult, game)}
                                            disabled={savingId === selectedResult.result_id && savingGameId === game.game_id}
                                            style={{ marginLeft: '1rem', whiteSpace: 'nowrap' }}
                                        >
                                            {savingId === selectedResult.result_id && savingGameId === game.game_id ? 'Adding...' : `+${game.max_points}`}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

