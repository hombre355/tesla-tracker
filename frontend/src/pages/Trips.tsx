import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTrips, useTripSummary } from '../hooks/useTrips'
import { fetchEfficiencyTrend } from '../api/stats'
import StatCard from '../components/common/StatCard'
import EfficiencyChart from '../components/charts/EfficiencyChart'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { fmtMiles, fmtKwh, fmtEfficiency, fmtCost, fmtDateTime } from '../utils/formatters'

export default function Trips() {
  const [days, setDays] = useState(30)
  const { data: trips, isLoading } = useTrips({ limit: 100 })
  const { data: summary } = useTripSummary()
  const { data: trend } = useQuery({
    queryKey: ['efficiency-trend', days],
    queryFn: () => fetchEfficiencyTrend(days),
  })

  if (isLoading) return <LoadingSpinner full />

  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-2xl font-bold text-white">Trips</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Trips" value={String(summary?.total_trips ?? 0)} />
        <StatCard label="Total Miles" value={fmtMiles(summary?.total_miles)} />
        <StatCard label="Total Energy" value={fmtKwh(summary?.total_kwh_used)} />
        <StatCard label="Avg Efficiency" value={fmtEfficiency(summary?.avg_efficiency_mi_per_kwh)} />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Efficiency Trend</h2>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-gray-800 text-gray-300 text-sm rounded-lg px-3 py-1 border border-gray-700"
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
            <option value={365}>1 year</option>
          </select>
        </div>
        {trend && trend.length > 0 ? (
          <EfficiencyChart data={trend} />
        ) : (
          <p className="text-gray-500 text-sm py-8 text-center">No data for this period.</p>
        )}
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Trip History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
                <th className="text-left p-3">Date</th>
                <th className="text-right p-3">Miles</th>
                <th className="text-right p-3">kWh Used</th>
                <th className="text-right p-3">Efficiency</th>
                <th className="text-right p-3">Start %</th>
                <th className="text-right p-3">End %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {trips?.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center text-gray-500 py-8">
                    No trips recorded yet.
                  </td>
                </tr>
              )}
              {trips?.map((trip) => (
                <tr key={trip.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="p-3 text-gray-300">{fmtDateTime(trip.started_at)}</td>
                  <td className="p-3 text-right text-white">{fmtMiles(trip.miles_driven)}</td>
                  <td className="p-3 text-right text-white">{fmtKwh(trip.kwh_used)}</td>
                  <td className="p-3 text-right text-white">{fmtEfficiency(trip.efficiency_mi_per_kwh)}</td>
                  <td className="p-3 text-right text-gray-400">{trip.start_battery_pct ? `${trip.start_battery_pct.toFixed(0)}%` : '—'}</td>
                  <td className="p-3 text-right text-gray-400">{trip.end_battery_pct ? `${trip.end_battery_pct.toFixed(0)}%` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
