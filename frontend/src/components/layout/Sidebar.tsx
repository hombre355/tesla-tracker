import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  MapIcon,
  BoltIcon,
  ScaleIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { to: '/trips', label: 'Trips', icon: MapIcon },
  { to: '/charging', label: 'Charging', icon: BoltIcon },
  { to: '/comparison', label: 'Comparison', icon: ScaleIcon },
  { to: '/settings', label: 'Settings', icon: Cog6ToothIcon },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col py-6 px-3 shrink-0">
      <div className="flex items-center gap-2 px-3 mb-8">
        <span className="text-tesla-red font-bold text-xl">⚡</span>
        <span className="text-white font-bold text-lg">Tesla Tracker</span>
      </div>
      <nav className="flex flex-col gap-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-tesla-red/20 text-tesla-red font-medium'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              )
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
