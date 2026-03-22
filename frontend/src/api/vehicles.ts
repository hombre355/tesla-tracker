import api from './client'

export interface Vehicle {
  id: number
  vin: string
  display_name: string | null
  model: string | null
  color: string | null
  pack_capacity_kwh: number | null
  is_active: boolean
  created_at: string
}

export const fetchVehicles = () =>
  api.get<Vehicle[]>('/vehicles').then((r) => r.data)

export const syncVehicles = () =>
  api.post('/vehicles/sync').then((r) => r.data)

export const fetchAuthStatus = () =>
  api.get<{ authenticated: boolean; vehicle_count: number }>('/auth/status').then((r) => r.data)
