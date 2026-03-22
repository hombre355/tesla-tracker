import api from './client'

export interface Trip {
  id: number
  vehicle_id: number
  started_at: string
  ended_at: string | null
  miles_driven: number | null
  kwh_used: number | null
  efficiency_mi_per_kwh: number | null
  start_battery_pct: number | null
  end_battery_pct: number | null
  start_location: string | null
  end_location: string | null
}

export interface TripSummary {
  total_trips: number
  total_miles: number
  total_kwh_used: number
  avg_efficiency_mi_per_kwh: number | null
  period: string
}

export const fetchTrips = (params?: Record<string, unknown>) =>
  api.get<Trip[]>('/trips', { params }).then((r) => r.data)

export const fetchTripSummary = (params?: Record<string, unknown>) =>
  api.get<TripSummary>('/trips/stats/summary', { params }).then((r) => r.data)
