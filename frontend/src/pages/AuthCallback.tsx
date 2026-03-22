import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/common/LoadingSpinner'

export default function AuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    // The backend handles the OAuth callback and redirects here after success.
    // Just redirect to dashboard.
    navigate('/dashboard', { replace: true })
  }, [navigate])

  return (
    <div className="flex flex-col items-center justify-center h-screen gap-4">
      <LoadingSpinner full />
      <p className="text-gray-400">Connecting your Tesla...</p>
    </div>
  )
}
