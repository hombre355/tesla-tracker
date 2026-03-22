import { useQuery } from '@tanstack/react-query'
import { fetchAuthStatus } from '../../api/vehicles'

export default function Navbar() {
  const { data: status } = useQuery({
    queryKey: ['auth-status'],
    queryFn: fetchAuthStatus,
    refetchInterval: 60_000,
  })

  return (
    <header className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-end px-6 shrink-0">
      {status?.authenticated ? (
        <span className="flex items-center gap-2 text-sm text-green-400">
          <span className="w-2 h-2 rounded-full bg-green-400 inline-block" />
          {status.vehicle_count} vehicle{status.vehicle_count !== 1 ? 's' : ''} connected
        </span>
      ) : (
        <a
          href="/api/auth/login"
          className="text-sm bg-tesla-red hover:bg-red-700 text-white px-4 py-1.5 rounded-lg transition-colors"
        >
          Connect Tesla
        </a>
      )}
    </header>
  )
}
