import { NavLink } from 'react-router-dom'

const links = [
  { label: 'Dashboard', path: '/dashboard', roles: ['admin', 'customer'] },
  { label: 'Products', path: '/products', roles: ['admin', 'customer'] },
  { label: 'Customers', path: '/customers', roles: ['admin'] },
  { label: 'Retail Pipeline', path: '/pipeline', roles: ['admin'] },
  { label: 'Recommendations', path: '/recommendations', roles: ['admin', 'customer'] },
  { label: 'Forecasting', path: '/forecasting', roles: ['admin'] },
  { label: 'Reviews', path: '/reviews', roles: ['admin', 'customer'] },
  { label: 'AI Insights', path: '/insights', roles: ['admin', 'customer'] },
]

export default function Sidebar({ roles = [] }) {
  const visibleLinks = links.filter((item) => item.roles.some((role) => roles.includes(role)))

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-slate-900 text-white shadow-lg">
      <div className="p-6 text-2xl font-semibold">Retail AI</div>
      <nav className="mt-6 space-y-2 px-4">
        {visibleLinks.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block rounded-xl px-4 py-3 text-sm hover:bg-slate-700 ${isActive ? 'bg-slate-800 font-semibold' : 'bg-slate-900'}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
