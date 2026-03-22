import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useCharges, useChargeSummary } from '../hooks/useCharges'
import { fetchChargingTrend } from '../api/stats'
import { syncCharges } from '../api/charges'
import StatCard from '../components/common/StatCard'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { fmtKwh, fmtCost, fmtDateTime } from '../utils/formatters'

const CHARGER_COLORS: Record<string, string> = {
  home: 'bg-blue-500/20 text-blue-400',
  supercharger: 'bg-red-500/20 text-red-400',
  dc_fast: 'bg-yellow-500/20 text-yellow-400',
  destination: 'bg-purple-500/20 text-purple-400',
}

export default function Charging() {
  const [days, setDays] = useState(30)
  const qc = useQueryClient()
  const { data: sessions, isLoading } = useCharges({ limit: 100 })
  const { data: summary } = useChargeSummary()
  const { data: trend } = useQuery({
    queryKey: ['charging-trend', days],
    queryFn: () => fetchChargingTrend(days),
  })
  const syncMutation = useMutation({
    mutationFn: syncCharges,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['charges'] })
      qc.invalidateQueries({ queryKey: ['charging-trend'] })
    },
  })

  if (isLoading) return <LoadingSpinner full />

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Charging</h1>
        <button
          onClick={() => syncMutation.mutate()}
          disabled={syncMutation.isPending}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {syncMutation.isPending ? <LoadingSpinner /> : null}
          Sync Now
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Sessions" value={String(summary?.total_sessions ?? 0)} />
        <StatCard label="Total Energy" value={fmtKwh(summary?.total_kwh_added)} />
        <StatCard label="Home Cost" value={fmtCost(summary?.total_electricity_cost_usd)} />
        <StatCard label="Supercharger Cost" value={fmtCost(summary?.total_supercharger_cost_usd)} />
      </div>

      {/* Simple session list instead of complex chart for now */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Energy Added by Day</h2>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-gray-800 text-gray-300 text-sm rounded-lg px-3 py-1 border border-gray-700"
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
          </select>
        </div>
        {trend && trend.length > 0 ? (
          <div className="space-y-1">
            {trend.map((point, i) => (
              <div key={i} className="flex justify-between text-sm py-1 border-b border-gray-800 last:border-0">
                <span className="text-gray-400">{point.date}</span>
                <span className="text-white">{fmtKwh(point.kwh_added)}</span>
                <span className="text-gray-400">{fmtCost(point.cost_usd)}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${CHARGER_COLORS[point.charger_type ?? ''] ?? 'bg-gray-700 text-gray-400'}`}>
                  {point.charger_type ?? 'unknown'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm py-8 text-center">No charging data for this period.</p>
        )}
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Session History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
                <th className="text-left p-3">Date</th>
                <th className="text-left p-3">Location</th>
                <th className="text-left p-3">Type</th>
                <th className="text-right p-3">kWh</th>
                <th className="text-right p-3">Miles Added</th>
                <th className="text-right p-3">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {sessions?.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center text-gray-500 py-8">
                    No charge sessions yet. Click "Sync Now" to pull your history.
                  </td>
                </tr>
              )}
              {sessions?.map((s) => (
                <tr key={s.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="p-3 text-gray-300">{fmtDateTime(s.started_at)}</td>
                  <td className="p-3 text-gray-300 truncate max-w-[160px]">{s.location_name ?? '—'}</td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${CHARGER_COLORS[s.charger_type ?? ''] ?? 'bg-gray-700 text-gray-400'}`}>
                      {s.charger_type ?? 'unknown'}
                    </span>
                  </td>
                  <td className="p-3 text-right text-white">{fmtKwh(s.kwh_added)}</td>
                  <td className="p-3 text-right text-gray-400">{s.miles_added ? `${s.miles_added.toFixed(0)} mi` : '—'}</td>
                  <td className="p-3 text-right text-white">
                    {fmtCost(s.electricity_cost_usd ?? s.supercharger_cost_usd)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
