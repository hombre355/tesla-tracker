export const fmtMiles = (val: number | null | undefined) =>
  val == null ? '—' : `${val.toFixed(1)} mi`

export const fmtKwh = (val: number | null | undefined) =>
  val == null ? '—' : `${val.toFixed(2)} kWh`

export const fmtEfficiency = (val: number | null | undefined) =>
  val == null ? '—' : `${val.toFixed(2)} mi/kWh`

export const fmtCost = (val: number | null | undefined) =>
  val == null ? '—' : `$${val.toFixed(2)}`

export const fmtPct = (val: number | null | undefined) =>
  val == null ? '—' : `${val.toFixed(0)}%`

export const fmtDate = (iso: string | null | undefined) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export const fmtDateTime = (iso: string | null | undefined) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
