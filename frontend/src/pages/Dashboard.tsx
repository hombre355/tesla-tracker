import { useQuery } from '@tanstack/react-query'
import { fetchDashboard } from '../api/stats'
import { useTrips } from '../hooks/useTrips'
import { useCharges } from '../hooks/useCharges'
import StatCard from '../components/common/StatCard'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { fmtMiles, fmtKwh, fmtCost, fmtDateTime } from '../utils/formatters'

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
    refetchInterval: 60_000,
  })
  const { data: recentTrips } = useTrips({ limit: 5 })
  const { data: recentCharges } = useCharges({ limit: 5 })

  if (isLoading) return <LoadingSpinner full />

  const m = stats?.this_month
  const c = stats?.charging

  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      <p className="text-gray-400 -mt-4 text-sm">This month's summary</p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard label="Trips" value={String(m?.trips ?? 0)} />
        <StatCard label="Miles Driven" value={fmtMiles(m?.miles_driven)} />
        <StatCard label="Energy Used" value={fmtKwh(m?.kwh_used)} />
        <StatCard label="Electricity Cost" value={fmtCost(m?.electricity_cost_usd)} />
        <StatCard label="Gas Equivalent" value={fmtCost(m?.gas_equivalent_cost_usd)} sub="est. cost" />
        <StatCard
          label="Savings vs Gas"
          value={fmtCost(m?.savings_usd)}
          accent
          trend="up"
          trendLabel="vs comparable gas car"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent Trips */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">Recent Trips</h2>
          {recentTrips?.length === 0 && (
            <p className="text-gray-500 text-sm">No trips recorded yet. Drive your Tesla to see data here.</p>
          )}
          <div className="divide-y divide-gray-800">
            {recentTrips?.map((trip) => (
              <div key={trip.id} className="py-2 flex justify-between text-sm">
                <div>
                  <p className="text-white">{fmtDateTime(trip.started_at)}</p>
                  <p className="text-gray-400">{fmtMiles(trip.miles_driven)} · {fmtKwh(trip.kwh_used)}</p>
                </div>
                <p className="text-gray-300 font-medium self-center">
                  {trip.efficiency_mi_per_kwh ? `${trip.efficiency_mi_per_kwh.toFixed(1)} mi/kWh` : '—'}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Charges */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">Recent Charges</h2>
          {recentCharges?.length === 0 && (
            <p className="text-gray-500 text-sm">No charging sessions yet.</p>
          )}
          <div className="divide-y divide-gray-800">
            {recentCharges?.map((s) => (
              <div key={s.id} className="py-2 flex justify-between text-sm">
                <div>
                  <p className="text-white">{fmtDateTime(s.started_at)}</p>
                  <p className="text-gray-400">
                    {s.location_name ?? s.charger_type ?? 'Unknown'} · {fmtKwh(s.kwh_added)}
                  </p>
                </div>
                <p className="text-gray-300 font-medium self-center">
                  {fmtCost(s.electricity_cost_usd ?? s.supercharger_cost_usd)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
