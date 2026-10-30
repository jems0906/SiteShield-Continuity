export type Role = 'analyst' | 'reviewer' | 'vendor' | 'leadership'

const baseUrl = import.meta.env.VITE_API_URL ?? ''

export async function getJson<T>(path: string, role: Role): Promise<T> {
  const response = await fetch(`${baseUrl}/api${path}`, {
    headers: { 'X-Demo-Role': role },
  })
  if (!response.ok) throw new Error(`Request failed (${response.status})`)
  return response.json() as Promise<T>
}

export async function postJson<T>(path: string, role: Role, body?: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}/api${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Demo-Role': role },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  })
  if (!response.ok) throw new Error(`Request failed (${response.status})`)
  return response.json() as Promise<T>
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