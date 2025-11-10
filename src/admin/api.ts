import axios from 'axios'
import type { AxiosInstance } from 'axios'

// Raw API response type (what the backend actually returns)
type RawAdminResult = {
    result_id: string
    user: string  // user ID
    user_name: string
    team?: string  // team ID
    team_name?: string
    game?: string  // game ID
    game_name?: string
    points_scored: number
    score?: number
    verified_by_admin?: boolean
    [key: string]: any  // allow other fields
}

// Transformed type (what the frontend expects)
export type AdminResult = {
    result_id: string
    user: {
        id: string
        name: string
        email: string
    }
    team?: {
        team_id: string
        team_name: string
    }
    game?: {
        game_id: string
        name: string
    }
    score: number
    verified_by_admin?: boolean
}

// Transform raw API response to expected format
function transformResult(raw: RawAdminResult, userEmail: string = ''): AdminResult {
    const userId = typeof raw.user === 'string' ? raw.user : (raw.user as any)?.id || ''
    return {
        result_id: raw.result_id,
        user: {
            id: userId,
            name: raw.user_name || '',
            email: userEmail,
        },
        team: raw.team && raw.team_name ? {
            team_id: typeof raw.team === 'string' ? raw.team : (raw.team as any)?.team_id || '',
            team_name: raw.team_name,
        } : undefined,
        game: raw.game && raw.game_name ? {
            game_id: typeof raw.game === 'string' ? raw.game : (raw.game as any)?.game_id || '',
            name: raw.game_name,
        } : undefined,
        score: (() => {
            const scoreValue = raw.score ?? raw.points_scored ?? 0
            // Ensure score is a number
            if (typeof scoreValue === 'number') {
                return scoreValue
            }
            if (typeof scoreValue === 'string') {
                const parsed = parseInt(scoreValue, 10)
                return isNaN(parsed) ? 0 : parsed
            }
            return 0
        })(),
        verified_by_admin: raw.verified_by_admin,
    }
}

export type AdminResultsResponse = {
    results: AdminResult[]
    count: number
}

function createClient(): AxiosInstance {
    const baseURL = '/api/'
    const instance = axios.create({ baseURL })
    instance.interceptors.request.use((config) => {
        // Use the same token key as src/api/client.ts
        const token = localStorage.getItem('access_token') || localStorage.getItem('accessToken') || localStorage.getItem('access')
        if (token) {
            config.headers = config.headers || {}
                ; (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
        }
        return config
    })
    return instance
}

const client = createClient()

export async function fetchAllResults(params?: { user_id?: string; team_id?: string; game_id?: string }, usersMap?: Map<string, string>): Promise<AdminResultsResponse> {
    const { data } = await client.get<{ results: RawAdminResult[]; count: number }>('admin/results/', { params })
    // Transform the results to match expected format
    const transformedResults = data.results.map(r => {
        const userId = typeof r.user === 'string' ? r.user : (r.user as any)?.id || ''
        const email = usersMap?.get(userId) || ''
        return transformResult(r, email)
    })
    return {
        results: transformedResults,
        count: data.count,
    }
}

export async function createResult(user_id: string, data?: { game_id?: string; team_id?: string; score?: number }): Promise<AdminResult> {
    const { data: result } = await client.post<RawAdminResult>('admin/results/', {
        user_id,
        ...data,
    })
    // Try to get user email
    let email = ''
    try {
        const usersData = await fetchUsers()
        email = usersData.users.find(u => u.id === user_id)?.email || ''
    } catch (e) {
        console.warn('Failed to fetch user email for created result:', e)
    }
    return transformResult(result, email)
}

export async function updateResult(result_id: string, update: Partial<Pick<AdminResult, 'score' | 'verified_by_admin'>>): Promise<AdminResult> {
    const { data } = await client.put<RawAdminResult>(`admin/results/${result_id}/`, update)
    // Try to get user email
    let email = ''
    try {
        const userId = typeof data.user === 'string' ? data.user : (data.user as any)?.id || ''
        if (userId) {
            const usersData = await fetchUsers()
            email = usersData.users.find(u => u.id === userId)?.email || ''
        }
    } catch (e) {
        console.warn('Failed to fetch user email for updated result:', e)
    }
    return transformResult(data, email)
}

export type UserSummary = { id: string; name: string; email: string }
export type UsersResponse = { users: UserSummary[]; count: number }

export async function fetchUsers(): Promise<UsersResponse> {
    const { data } = await client.get<UsersResponse>('users/')
    return data
}
