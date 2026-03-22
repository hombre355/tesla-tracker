import { useQuery } from '@tanstack/react-query'
import { fetchComparison } from '../api/stats'
import { useSettings } from '../hooks/useSettings'
import StatCard from '../components/common/StatCard'
import CostComparisonChart from '../components/charts/CostComparisonChart'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { fmtCost, fmtMiles } from '../utils/formatters'

export default function Comparison() {
  const { data: settings } = useSettings()
  const { data: comparison, isLoading } = useQuery({
    queryKey: ['comparison'],
    queryFn: () => fetchComparison(),
  })

  if (isLoading) return <LoadingSpinner full />

  const totals = comparison?.reduce(
    (acc, m) => ({
      miles: acc.miles + m.miles,
      elec: acc.elec + m.electricity_cost_usd,
      gas: acc.gas + m.gas_equivalent_cost_usd,
    }),
    { miles: 0, elec: 0, gas: 0 }
  ) ?? { miles: 0, elec: 0, gas: 0 }

  const totalSavings = totals.gas - totals.elec
  const latest = comparison?.at(-1)

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Cost Comparison</h1>
        <p className="text-gray-400 text-sm mt-1">
          Your Tesla vs a {settings?.comparison_mpg ?? 30} MPG gas car at ${settings?.gas_price_per_gallon?.toFixed(2) ?? '3.50'}/gal
          · electricity at ${settings?.electricity_rate_per_kwh?.toFixed(3) ?? '0.130'}/kWh
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Miles" value={fmtMiles(totals.miles)} />
        <StatCard label="Electricity Cost" value={fmtCost(totals.elec)} sub="what you paid" />
        <StatCard label="Gas Equivalent" value={fmtCost(totals.gas)} sub="what you'd have paid" />
        <StatCard
          label="Total Savings"
          value={fmtCost(totalSavings)}
          accent={totalSavings > 0}
          trend={totalSavings > 0 ? 'up' : 'neutral'}
          trendLabel="vs gas car"
        />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">Monthly Cost Breakdown</h2>
        {comparison && comparison.length > 0 ? (
          <CostComparisonChart data={comparison} />
        ) : (
          <p className="text-gray-500 text-sm py-8 text-center">
            No trip data yet. Drive your Tesla to populate this chart.
          </p>
        )}
      </div>

      {comparison && comparison.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800">
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Monthly Breakdown</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
                  <th className="text-left p-3">Month</th>
                  <th className="text-right p-3">Miles</th>
                  <th className="text-right p-3">kWh Used</th>
                  <th className="text-right p-3">Electricity Cost</th>
                  <th className="text-right p-3">Gas Equivalent</th>
                  <th className="text-right p-3">Monthly Savings</th>
                  <th className="text-right p-3">Cumulative</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {comparison.map((m) => (
                  <tr key={m.month} className="hover:bg-gray-800/50 transition-colors">
                    <td className="p-3 text-gray-300 font-medium">{m.month}</td>
                    <td className="p-3 text-right text-white">{fmtMiles(m.miles)}</td>
                    <td className="p-3 text-right text-white">{m.kwh_used.toFixed(1)} kWh</td>
                    <td className="p-3 text-right text-blue-400">{fmtCost(m.electricity_cost_usd)}</td>
                    <td className="p-3 text-right text-yellow-400">{fmtCost(m.gas_equivalent_cost_usd)}</td>
                    <td className="p-3 text-right text-green-400">{fmtCost(m.savings_usd)}</td>
                    <td className="p-3 text-right text-green-300 font-medium">{fmtCost(m.cumulative_savings_usd)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
