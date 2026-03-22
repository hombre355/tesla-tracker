import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface MonthData {
  month: string
  home_kwh?: number
  supercharger_kwh?: number
  home_cost?: number
  supercharger_cost?: number
}

interface Props {
  data: MonthData[]
  mode?: 'kwh' | 'cost'
}

export default function ChargingCostChart({ data, mode = 'cost' }: Props) {
  const isCost = mode === 'cost'
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#9CA3AF' }} />
        <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} unit={isCost ? ' $' : ' kWh'} />
        <Tooltip
          contentStyle={{ background: '#1F2937', border: '1px solid #374151', borderRadius: 8 }}
          labelStyle={{ color: '#F9FAFB' }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey={isCost ? 'home_cost' : 'home_kwh'} name="Home" fill="#3B82F6" stackId="a" radius={[0, 0, 0, 0]} />
        <Bar dataKey={isCost ? 'supercharger_cost' : 'supercharger_kwh'} name="Supercharger" fill="#E31937" stackId="a" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
