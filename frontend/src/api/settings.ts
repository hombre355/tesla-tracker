import api from './client'

export interface AppSettings {
  id: number
  vehicle_id: number | null
  electricity_rate_per_kwh: number
  gas_price_per_gallon: number
  comparison_mpg: number
  sync_interval_minutes: number
}

export const fetchSettings = () =>
  api.get<AppSettings>('/settings').then((r) => r.data)

export const updateSettings = (data: Partial<Omit<AppSettings, 'id' | 'vehicle_id'>>) =>
  api.put<AppSettings>('/settings', data).then((r) => r.data)
