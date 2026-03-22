import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchSettings, updateSettings } from '../api/settings'

export const useSettings = () =>
  useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
  })

export const useUpdateSettings = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateSettings,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings'] }),
  })
}
