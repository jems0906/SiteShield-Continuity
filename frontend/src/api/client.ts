export type Role = 'analyst' | 'reviewer' | 'vendor' | 'leadership'

const baseUrl = import.meta.env.VITE_API_URL ?? ''
let csrfToken = ''

export interface SessionUser {
  username: string
  role: Role
  csrf_token: string
}


export function setCsrfToken(token: string) {
  csrfToken = token
}

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${baseUrl}/api${path}`, {
    credentials: 'include',
  })
  if (!response.ok) throw new Error(`Request failed (${response.status})`)
  return response.json() as Promise<T>
}

export async function postJson<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}/api${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  })
  if (!response.ok) throw new Error(`Request failed (${response.status})`)
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export async function login(username: string, password: string): Promise<SessionUser> {
  const response = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) throw new Error('Sign-in failed. Check your username and password.')
  return response.json() as Promise<SessionUser>
}

export async function currentUser(): Promise<SessionUser> {
  const response = await fetch(`${baseUrl}/api/auth/me`, { credentials: 'include' })
  if (!response.ok) throw new Error('No active session')
  return response.json() as Promise<SessionUser>
}

export async function logout(): Promise<void> {
  await postJson<void>('/auth/logout')
  csrfToken = ''
}

export interface Asset {
  id: string
  category: string
  owner: string
  inspection_date: string
  status: string
  site: string
  availability: number
}

export interface EventRecord {
  id: string
  source_record_id: string
  asset_id: string
  occurred_at: string
  classification: string
  summary: string
  duplicate_of: string | null
}

export interface Finding {
  id: string
  asset_id: string
  checklist_item: string
  evidence_reference: string
  result: string
  priority: string
  owner: string
  corrective_action: string
  status: string
}

export interface WorkOrder {
  id: string
  asset_id: string
  title: string
  scope: string
  accountable_owner: string
  scheduled_window: string
  status: string
  completion_record: string
  acceptance_criteria: string[]
  reviewer_acceptance: string
  diagnostic: { hypothesis?: string; vendor_assessment?: string; repeated_activations?: string[] }
  functional_retest: { passed?: boolean; coverage_reviewed?: boolean; notes?: string }
}

export interface Handoff {
  id: string
  shift: string
  open_incidents: string[]
  unresolved_defects: string[]
  work_in_progress: string[]
  temporary_arrangements: string[]
  next_owner: string
  acknowledged_by: string
}

export interface Exercise {
  id: string
  title: string
  scenario_type: string
  timeline: { time: string; inject: string }[]
  decisions: { prompt: string; decision: string; owner: string }[]
  communications: { audience: string; draft: string }[]
  findings: string[]
  improvements: { action: string; owner: string; due: string; status: string }[]
  business_impact: Record<string, string | string[]>
}

export interface Metrics {
  window_days: number
  event_count: number
  repeat_events: number
  repeat_events_per_monitored_device_day: number
  device_availability_percent: number
  unresolved_faults: number
  mean_time_to_repair_hours: number | null
  confirmed_actionable_events: number
  duplicate_records_excluded: number
  simulated_comparison: {
    is_constructed_fixture: boolean
    window_days_each: number
    before_distinct_activations: number
    after_distinct_activations: number
    before_duplicate_records: number
    after_duplicate_records: number
    note: string
  }
  definitions: Record<string, string>
  demonstration: boolean
  notice: string
}

export interface AuthMethods {
  entra_enabled: boolean
  local_password_enabled: boolean
}

export async function getAuthMethods(): Promise<AuthMethods> {
  const response = await fetch(`${baseUrl}/api/auth/methods`)
  if (!response.ok) throw new Error(`Request failed (${response.status})`)
  return response.json() as Promise<AuthMethods>
}

export function entraLoginUrl(): string {
  return `${baseUrl}/api/auth/entra/login`
}