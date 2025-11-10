import { useEffect, useMemo, useState } from 'react'
import { fetchAllResults, fetchUsers } from '../admin/api'
import type { AdminResult } from '../admin/api'

type Leader = {
  user: string
  user_name: string
  total_points: number
}

type GameScore = {
  game_name: string
  game_id: string
  total_score: number
  play_count: number
}

export function HighScores() {
  const [results, setResults] = useState<AdminResult[]>([])
  const [users, setUsers] = useState<Array<{ id: string; name: string; email: string }>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedPlayer, setSelectedPlayer] = useState<Leader | null>(null)
  const [playerGames, setPlayerGames] = useState<GameScore[]>([])

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        // Fetch results first
        const resultsData = await fetchAllResults()
        const resultsList = resultsData.results || []
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
            const userId = r.user?.id || ''
            const userName = r.user?.name || 'Unknown'
            const userEmail = r.user?.email || ''
            if (userId && !usersMap.has(userId)) {
              usersMap.set(userId, {
                id: userId,
                name: userName,
                email: userEmail,
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
    load()
  }, [])

  // Function to get games for a specific player
  const getPlayerGames = (playerId: string): GameScore[] => {
    const playerResults = results.filter(r => {
      const userId = r.user?.id || ''
      return userId === playerId
    })

    console.log(`Getting games for player ${playerId}, found ${playerResults.length} results:`, playerResults)

    // Group by game_id
    const gameMap = new Map<string, { game_name: string; game_id: string; scores: number[] }>()
    
    for (const result of playerResults) {
      // AdminResult has game as an object with game_id and name
      const gameId = result.game?.game_id || 'unknown'
      const gameName = result.game?.name || 'Unknown Game'
      
      // Normalize gameId - ensure it's a string and not empty
      const normalizedGameId = String(gameId || gameName || 'unknown').trim()
      
      const score = result.score ?? 0
      const scoreValue = typeof score === 'number' ? score : (typeof score === 'string' ? parseInt(score, 10) || 0 : 0)
      
      console.log(`Processing result: gameId="${normalizedGameId}", gameName="${gameName}", score=${scoreValue}`)
      
      if (!gameMap.has(normalizedGameId)) {
        gameMap.set(normalizedGameId, { game_name: gameName, game_id: normalizedGameId, scores: [] })
      }
      gameMap.get(normalizedGameId)!.scores.push(scoreValue)
    }

    // Convert to array and calculate totals
    const games = Array.from(gameMap.values()).map(game => ({
      game_name: game.game_name,
      game_id: game.game_id,
      total_score: game.scores.reduce((sum, s) => sum + s, 0),
      play_count: game.scores.length
    })).sort((a, b) => b.total_score - a.total_score)
    
    console.log(`Grouped into ${games.length} games:`, games)
    return games
  }

  const handleInfoClick = (leader: Leader) => {
    setSelectedPlayer(leader)
    const games = getPlayerGames(leader.user)
    setPlayerGames(games)
  }

  const closeModal = () => {
    setSelectedPlayer(null)
    setPlayerGames([])
  }

  const leaders = useMemo<Leader[]>(() => {
    // If we have no users, try to create from results
    if (users.length === 0) {
      // Extract users from results as fallback
      const userPointsMap = new Map<string, { name: string; points: number }>()
      for (const r of results) {
        const userId = r.user?.id || ''
        const userName = r.user?.name || 'Unknown'
        if (userId) {
          const score = r.score ?? 0
          // Ensure score is a number
          const scoreValue = typeof score === 'number' ? score : (typeof score === 'string' ? parseInt(score, 10) || 0 : 0)
          const existing = userPointsMap.get(userId)
          if (existing) {
            existing.points += scoreValue
          } else {
            userPointsMap.set(userId, { name: userName, points: scoreValue })
          }
        }
      }
      return Array.from(userPointsMap.entries())
        .map(([userId, data]) => ({
          user: userId,
          user_name: data.name,
          total_points: data.points
        }))
        .sort((a, b) => b.total_points - a.total_points)
    }
    
    // Create a map of user ID to their total points from results
    const userPointsMap = new Map<string, number>()
    for (const r of results) {
      const userId = r.user?.id || ''
      if (userId) {
        // Use score field from AdminResult
        const score = r.score ?? 0
        // Ensure score is a number
        const scoreValue = typeof score === 'number' ? score : (typeof score === 'string' ? parseInt(score, 10) || 0 : 0)
        userPointsMap.set(userId, (userPointsMap.get(userId) || 0) + scoreValue)
      }
    }

    // Create leaders list from all users, including those without results
    const leadersList: Leader[] = users.map(user => ({
      user: user.id,
      user_name: user.name,
      total_points: userPointsMap.get(user.id) || 0
    }))

    // Sort by total_points descending (highest first)
    return leadersList
      .sort((a, b) => b.total_points - a.total_points)
  }, [results, users])

  return (
    <div>
      <h2 style={{ color: '#9ddc2d', textShadow: '2px 2px #000', marginBottom: '1rem' }}>High Scores</h2>
      {loading && <div style={{ color: '#eaeaea', padding: '1rem', textAlign: 'center' }}>Loading...</div>}
      {error && <div className="pixel-error" style={{ marginBottom: '1rem' }}>{error}</div>}
      {!loading && !error && (
        <div className="pixel-panel" style={{ padding: '1rem' }}>
          {leaders.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#eaeaea', opacity: 0.7 }}>
              No scores yet. Play some games to see leaderboard!
            </div>
          ) : (
            <table className="pixel-table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'center', padding: '0.75rem', color: '#9ddc2d', width: '50px', verticalAlign: 'middle' }}></th>
                  <th style={{ textAlign: 'left', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>#</th>
                  <th style={{ textAlign: 'left', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Player</th>
                  <th style={{ textAlign: 'right', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Total Points</th>
                </tr>
              </thead>
              <tbody>
                {leaders.map((l, idx) => (
                  <tr key={l.user || `leader-${idx}`}>
                    <td style={{ padding: '0.75rem', textAlign: 'center', verticalAlign: 'middle' }}>
                      <button
                        onClick={() => handleInfoClick(l)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#9ddc2d',
                          cursor: 'pointer',
                          fontSize: '1rem',
                          padding: '0.25rem',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: '1.5rem',
                          height: '1.5rem',
                          borderRadius: '50%',
                          transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = 'rgba(157, 220, 45, 0.2)'
                          e.currentTarget.style.transform = 'scale(1.1)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent'
                          e.currentTarget.style.transform = 'scale(1)'
                        }}
                        title="View player games"
                      >
                        ℹ️
                      </button>
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea', fontWeight: idx < 3 ? 'bold' : 'normal' }}>
                      {idx + 1}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea', fontWeight: idx < 3 ? 'bold' : 'normal' }}>
                      {l.user_name || l.user || 'Unknown Player'}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', verticalAlign: 'middle', color: '#eaeaea', fontWeight: 'bold', fontSize: idx < 3 ? '1.2rem' : '1.1rem' }}>
                      {l.total_points}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Player Games Modal */}
      {selectedPlayer && (
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
          onClick={closeModal}
        >
          <div
            className="pixel-panel"
            style={{
              padding: '1.5rem',
              maxWidth: '600px',
              width: '90%',
              maxHeight: '85vh',
              overflow: 'auto',
              position: 'relative',
              backgroundColor: '#2b2b2b',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, color: '#9ddc2d', textShadow: '2px 2px #000' }}>
                {selectedPlayer.user_name}'s Games
              </h3>
              <button
                className="pixel-button"
                onClick={closeModal}
                style={{ padding: '0.5rem 1rem', fontSize: '1.2rem', lineHeight: 1, minWidth: 'auto' }}
              >
                ×
              </button>
            </div>

            {playerGames.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#eaeaea', opacity: 0.7 }}>
                No games played yet.
              </div>
            ) : (
              <table className="pixel-table" style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Game</th>
                    <th style={{ textAlign: 'center', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Plays</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem', color: '#9ddc2d', verticalAlign: 'middle' }}>Total Score</th>
                  </tr>
                </thead>
                <tbody>
                  {playerGames.map((game, idx) => (
                    <tr key={game.game_id || idx}>
                      <td style={{ padding: '0.75rem', textAlign: 'left', verticalAlign: 'middle', color: '#eaeaea' }}>
                        {game.game_name}
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'center', verticalAlign: 'middle', color: '#eaeaea' }}>
                        {game.play_count}
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'right', verticalAlign: 'middle', color: '#eaeaea', fontWeight: 'bold' }}>
                        {game.total_score}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  )
}


