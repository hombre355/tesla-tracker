export default function Connect() {
  return (
    <div className="flex flex-col items-center justify-center h-screen gap-6 px-4">
      <div className="text-tesla-red text-5xl">⚡</div>
      <h1 className="text-3xl font-bold text-white">Tesla Tracker</h1>
      <p className="text-gray-400 text-center max-w-sm">
        Track your energy usage, charging costs, and see how much you save compared to a gas car.
      </p>
      <a
        href="/api/auth/login"
        className="bg-tesla-red hover:bg-red-700 text-white px-8 py-3 rounded-xl font-semibold text-lg transition-colors"
      >
        Connect Tesla Account
      </a>
    </div>
  )
}
