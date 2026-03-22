import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchAuthStatus, syncVehicles } from '../api/vehicles'
import { useSettings, useUpdateSettings } from '../hooks/useSettings'
import LoadingSpinner from '../components/common/LoadingSpinner'

export default function Settings() {
  const qc = useQueryClient()
  const { data: settings, isLoading } = useSettings()
  const { data: authStatus } = useQuery({ queryKey: ['auth-status'], queryFn: fetchAuthStatus })
  const updateMutation = useUpdateSettings()
  const syncMutation = useMutation({
    mutationFn: syncVehicles,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['auth-status'] }),
  })

  const [form, setForm] = useState({
    electricity_rate_per_kwh: '',
    gas_price_per_gallon: '',
    comparison_mpg: '',
    sync_interval_minutes: '',
  })

  useEffect(() => {
    if (settings) {
      setForm({
        electricity_rate_per_kwh: String(settings.electricity_rate_per_kwh),
        gas_price_per_gallon: String(settings.gas_price_per_gallon),
        comparison_mpg: String(settings.comparison_mpg),
        sync_interval_minutes: String(settings.sync_interval_minutes),
      })
    }
  }, [settings])

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({
      electricity_rate_per_kwh: parseFloat(form.electricity_rate_per_kwh),
      gas_price_per_gallon: parseFloat(form.gas_price_per_gallon),
      comparison_mpg: parseFloat(form.comparison_mpg),
      sync_interval_minutes: parseInt(form.sync_interval_minutes),
    })
  }

  if (isLoading) return <LoadingSpinner full />

  return (
    <div className="space-y-6 max-w-lg">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      {/* Auth Status */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">Tesla Account</h2>
        {authStatus?.authenticated ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-400 text-sm">
              <span className="w-2 h-2 rounded-full bg-green-400 inline-block" />
              {authStatus.vehicle_count} vehicle{authStatus.vehicle_count !== 1 ? 's' : ''} connected
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => syncMutation.mutate()}
                disabled={syncMutation.isPending}
                className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
              >
                {syncMutation.isPending ? <LoadingSpinner /> : null}
                Sync Now
              </button>
              <a
                href="/api/auth/login"
                className="bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
              >
                Re-authenticate
              </a>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">Not connected</span>
            <a
              href="/api/auth/login"
              className="bg-tesla-red hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Connect Tesla Account
            </a>
          </div>
        )}
      </div>

      {/* Cost Settings */}
      <form onSubmit={handleSave} className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-4">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Cost & Comparison</h2>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Electricity Rate ($/kWh)
          </label>
          <input
            type="number"
            step="0.001"
            min="0.01"
            value={form.electricity_rate_per_kwh}
            onChange={(e) => setForm((f) => ({ ...f, electricity_rate_per_kwh: e.target.value }))}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-tesla-red"
          />
          <p className="text-xs text-gray-500 mt-1">Check your electric bill for your local rate.</p>
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Gas Price ($/gallon)
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={form.gas_price_per_gallon}
            onChange={(e) => setForm((f) => ({ ...f, gas_price_per_gallon: e.target.value }))}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-tesla-red"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Comparison Vehicle MPG
          </label>
          <input
            type="number"
            step="0.5"
            min="1"
            value={form.comparison_mpg}
            onChange={(e) => setForm((f) => ({ ...f, comparison_mpg: e.target.value }))}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-tesla-red"
          />
          <p className="text-xs text-gray-500 mt-1">The MPG of the gas car you're comparing against.</p>
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Sync Interval (minutes)
          </label>
          <select
            value={form.sync_interval_minutes}
            onChange={(e) => setForm((f) => ({ ...f, sync_interval_minutes: e.target.value }))}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-tesla-red"
          >
            <option value="1">Every 1 minute</option>
            <option value="5">Every 5 minutes</option>
            <option value="15">Every 15 minutes</option>
            <option value="30">Every 30 minutes</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">More frequent polling captures shorter trips but uses more API quota.</p>
        </div>

        <button
          type="submit"
          disabled={updateMutation.isPending}
          className="w-full bg-tesla-red hover:bg-red-700 text-white py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
        </button>
        {updateMutation.isSuccess && (
          <p className="text-green-400 text-sm text-center">Settings saved!</p>
        )}
      </form>
    </div>
  )
}
