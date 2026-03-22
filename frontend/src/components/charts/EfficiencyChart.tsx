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
import type { EfficiencyPoint } from '../../api/stats'

interface Props {
  data: EfficiencyPoint[]
}

export default function EfficiencyChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9CA3AF' }} />
        <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#9CA3AF' }} unit=" mi" />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#9CA3AF' }} unit=" mi/kWh" />
        <Tooltip
          contentStyle={{ background: '#1F2937', border: '1px solid #374151', borderRadius: 8 }}
          labelStyle={{ color: '#F9FAFB' }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar yAxisId="left" dataKey="miles" name="Miles" fill="#3B82F6" opacity={0.7} radius={[2, 2, 0, 0]} />
        <Line yAxisId="right" dataKey="efficiency_mi_per_kwh" name="mi/kWh" stroke="#E31937" strokeWidth={2} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
