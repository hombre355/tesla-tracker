import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function Connect() {
  const navigate = useNavigate()
  const [accessToken, setAccessToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/connect', {
        access_token: accessToken.replace(/\s+/g, ''),
        refresh_token: refreshToken.replace(/\s+/g, ''),
      })
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Connection failed. Check your tokens and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-6 px-4 py-12">
      <div className="text-tesla-red text-5xl">⚡</div>
      <h1 className="text-3xl font-bold text-white">Connect Your Tesla</h1>

      <div className="bg-gray-800 rounded-2xl p-6 max-w-lg w-full space-y-4">
        <h2 className="text-white font-semibold text-lg">Step 1 — Get your tokens</h2>
        <p className="text-gray-400 text-sm">
          Visit{' '}
          <a
            href="https://www.myteslamate.com/tesla-token"
            target="_blank"
            rel="noopener noreferrer"
            className="text-tesla-red underline"
          >
            myteslamate.com/tesla-token
          </a>{' '}
          and sign in with your Tesla account. Copy the <strong className="text-white">Access Token</strong> and{' '}
          <strong className="text-white">Refresh Token</strong> it generates.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-gray-800 rounded-2xl p-6 max-w-lg w-full space-y-4">
        <h2 className="text-white font-semibold text-lg">Step 2 — Paste your tokens</h2>

        <div className="space-y-2">
          <label className="text-gray-300 text-sm font-medium">Access Token</label>
          <textarea
            value={accessToken}
            onChange={e => setAccessToken(e.target.value)}
            rows={4}
            required
            placeholder="ey..."
            className="w-full bg-gray-900 text-gray-100 text-xs rounded-lg p-3 border border-gray-700 focus:border-tesla-red focus:outline-none resize-none font-mono"
          />
        </div>

        <div className="space-y-2">
          <label className="text-gray-300 text-sm font-medium">Refresh Token</label>
          <textarea
            value={refreshToken}
            onChange={e => setRefreshToken(e.target.value)}
            rows={4}
            required
            placeholder="ey..."
            className="w-full bg-gray-900 text-gray-100 text-xs rounded-lg p-3 border border-gray-700 focus:border-tesla-red focus:outline-none resize-none font-mono"
          />
        </div>

        {error && (
          <p className="text-red-400 text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading || !accessToken || !refreshToken}
          className="w-full bg-tesla-red hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-xl font-semibold text-lg transition-colors"
        >
          {loading ? 'Connecting...' : 'Connect Tesla'}
        </button>
      </form>
    </div>
  )
}
