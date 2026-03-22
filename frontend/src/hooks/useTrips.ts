import { useQuery } from '@tanstack/react-query'
import { fetchTrips, fetchTripSummary } from '../api/trips'

export const useTrips = (params?: Record<string, unknown>) =>
  useQuery({
    queryKey: ['trips', params],
    queryFn: () => fetchTrips(params),
  })

export const useTripSummary = (params?: Record<string, unknown>) =>
  useQuery({
    queryKey: ['trip-summary', params],
    queryFn: () => fetchTripSummary(params),
  })
