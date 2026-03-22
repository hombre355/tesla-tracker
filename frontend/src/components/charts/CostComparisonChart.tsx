import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { ComparisonMonth } from '../../api/stats'

interface Props {
  data: ComparisonMonth[]
}

export default function CostComparisonChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <ComposedChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#9CA3AF' }} />
        <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#9CA3AF' }} unit=" $" />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#9CA3AF' }} unit=" $" />
        <Tooltip
          contentStyle={{ background: '#1F2937', border: '1px solid #374151', borderRadius: 8 }}
          labelStyle={{ color: '#F9FAFB' }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar yAxisId="left" dataKey="electricity_cost_usd" name="Electricity" fill="#3B82F6" radius={[2, 2, 0, 0]} />
        <Bar yAxisId="left" dataKey="gas_equivalent_cost_usd" name="Gas (est.)" fill="#F59E0B" radius={[2, 2, 0, 0]} />
        <Line yAxisId="right" dataKey="cumulative_savings_usd" name="Cumulative Savings" stroke="#10B981" strokeWidth={2} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
