import { useQuery } from '@tanstack/react-query'
import { fetchCharges, fetchChargeSummary } from '../api/charges'

export const useCharges = (params?: Record<string, unknown>) =>
  useQuery({
    queryKey: ['charges', params],
    queryFn: () => fetchCharges(params),
  })

export const useChargeSummary = (params?: Record<string, unknown>) =>
  useQuery({
    queryKey: ['charge-summary', params],
    queryFn: () => fetchChargeSummary(params),
  })
