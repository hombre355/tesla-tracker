import api from './client'

export interface ChargeSession {
  id: number
  vehicle_id: number
  started_at: string
  ended_at: string | null
  location_name: string | null
  charger_type: string | null
  kwh_added: number | null
  start_battery_pct: number | null
  end_battery_pct: number | null
  peak_power_kw: number | null
  electricity_cost_usd: number | null
  supercharger_cost_usd: number | null
  miles_added: number | null
}

export interface ChargeSummary {
  total_sessions: number
  total_kwh_added: number
  total_electricity_cost_usd: number
  total_supercharger_cost_usd: number
  avg_kwh_per_session: number | null
  period: string
}

export const fetchCharges = (params?: Record<string, unknown>) =>
  api.get<ChargeSession[]>('/charges', { params }).then((r) => r.data)

export const fetchChargeSummary = (params?: Record<string, unknown>) =>
  api.get<ChargeSummary>('/charges/stats/summary', { params }).then((r) => r.data)

export const syncCharges = () =>
  api.post('/charges/sync').then((r) => r.data)
