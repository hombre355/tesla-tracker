import api from './client'

export interface DashboardStats {
  this_month: {
    trips: number
    miles_driven: number
    kwh_used: number
    electricity_cost_usd: number
    gas_equivalent_cost_usd: number
    savings_usd: number
  }
  charging: {
    sessions: number
    kwh_added: number
    total_cost_usd: number
  }
}

export interface ComparisonMonth {
  month: string
  miles: number
  kwh_used: number
  electricity_cost_usd: number
  gas_equivalent_cost_usd: number
  savings_usd: number
  cumulative_savings_usd: number
}

export interface EfficiencyPoint {
  date: string
  miles: number | null
  kwh_used: number | null
  efficiency_mi_per_kwh: number | null
}

export interface ChargingPoint {
  date: string
  kwh_added: number | null
  cost_usd: number | null
  charger_type: string | null
}

export const fetchDashboard = () =>
  api.get<DashboardStats>('/stats/dashboard').then((r) => r.data)

export const fetchComparison = (params?: Record<string, unknown>) =>
  api.get<ComparisonMonth[]>('/stats/comparison', { params }).then((r) => r.data)

export const fetchEfficiencyTrend = (days = 30) =>
  api.get<EfficiencyPoint[]>('/stats/efficiency/trend', { params: { days } }).then((r) => r.data)

export const fetchChargingTrend = (days = 30) =>
  api.get<ChargingPoint[]>('/stats/charging/trend', { params: { days } }).then((r) => r.data)
