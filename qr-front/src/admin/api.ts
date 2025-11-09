import axios from 'axios'
import type { AxiosInstance } from 'axios'

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

export type AdminResultsResponse = {
  results: AdminResult[]
  count: number
}

function createClient(): AxiosInstance {
  const baseURL = '/api/'
  const instance = axios.create({ baseURL })
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken') || localStorage.getItem('access')
    if (token) {
      config.headers = config.headers || {}
      ;(config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
    }
    return config
  })
  return instance
}

const client = createClient()

export async function fetchAllResults(params?: { user_id?: string; team_id?: string; game_id?: string }): Promise<AdminResultsResponse> {
  const { data } = await client.get<AdminResultsResponse>('admin/results/', { params })
  return data
}

export async function updateResult(result_id: string, update: Partial<Pick<AdminResult, 'score' | 'verified_by_admin'>>): Promise<AdminResult> {
  const { data } = await client.put<AdminResult>(`admin/results/${result_id}/`, update)
  return data as unknown as AdminResult
}

export type UserSummary = { id: string; name: string; email: string }
export type UsersResponse = { users: UserSummary[]; count: number }

export async function fetchUsers(): Promise<UsersResponse> {
  const { data } = await client.get<UsersResponse>('users/')
  return data
}


