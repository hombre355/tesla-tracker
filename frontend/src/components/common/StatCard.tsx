import clsx from 'clsx'

interface Props {
  label: string
  value: string
  sub?: string
  trend?: 'up' | 'down' | 'neutral'
  trendLabel?: string
  accent?: boolean
}

export default function StatCard({ label, value, sub, trend, trendLabel, accent }: Props) {
  return (
    <div className={clsx(
      'rounded-xl p-4 flex flex-col gap-1',
      accent ? 'bg-tesla-red/20 border border-tesla-red/40' : 'bg-gray-900 border border-gray-800'
    )}>
      <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-gray-400">{sub}</p>}
      {trendLabel && (
        <p className={clsx(
          'text-xs font-medium',
          trend === 'up' && 'text-green-400',
          trend === 'down' && 'text-red-400',
          trend === 'neutral' && 'text-gray-400',
        )}>
          {trendLabel}
        </p>
      )}
    </div>
  )
}
