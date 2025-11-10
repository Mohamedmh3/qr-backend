import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export type AuthUser = {
  id: string
  name: string
  email: string
  role: string
  qr_id?: string
  qr_image_url?: string | null
}

export type AuthResponse = {
  user: AuthUser
  tokens: { access: string; refresh?: string }
}

export const storage = {
  get token() {
    return localStorage.getItem('access_token') || ''
  },
  set token(value: string) {
    localStorage.setItem('access_token', value)
  },
  clear() {
    localStorage.removeItem('access_token')
  },
}

export const api = axios.create({
  baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
  // Don't add Authorization header for login/register endpoints
  const publicEndpoints = ['/login/', '/register/', '/debug/login/']
  const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.endsWith(endpoint))
  
  if (!isPublicEndpoint) {
    const token = storage.token
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/login/', { email, password })
  storage.token = data.tokens.access
  return data
}

export type AdminResult = {
  result_id: string
  user: string
  user_name: string
  team: string
  team_name: string
  game: string
  game_name: string
  points_scored: number
  score?: number  // Alias for points_scored (returned by API)
  played_at: string
  notes?: string | null
  verified_by_admin: boolean
  admin_user?: string | null
  admin_name?: string | null
}

export async function fetchAllResults(params?: {
  user_id?: string
  team_id?: string
  game_id?: string
}): Promise<{ results: AdminResult[]; count: number }> {
  const { data } = await api.get<{ results: AdminResult[]; count: number }>(
    '/admin/results/',
    { params }
  )
  return data
}

export async function updateResult(result_id: string, payload: Partial<AdminResult>) {
  const { data } = await api.put<AdminResult>(`/admin/results/${result_id}/`, payload)
  return data
}

export type Game = {
  game_id: string
  game_name: string
  game_description?: string
  max_points: number
  min_points: number
  is_active: boolean
  total_plays?: number
  created_at?: string
  updated_at?: string
}

export type GamesResponse = {
  games: Game[]
  count: number
}

export async function fetchGames(): Promise<GamesResponse> {
  const { data } = await api.get<GamesResponse>('/games/')
  return data
}


