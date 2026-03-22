export default function LoadingSpinner({ full = false }: { full?: boolean }) {
  if (full) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-tesla-red border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  return <div className="w-5 h-5 border-2 border-tesla-red border-t-transparent rounded-full animate-spin inline-block" />
}
