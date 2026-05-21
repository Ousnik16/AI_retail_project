export default function Navbar({ user }) {
  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_email')
    localStorage.removeItem('user_roles')
    window.location.href = '/login'
  }

  return (
    <header className="flex items-center justify-between bg-white px-6 py-4 shadow-sm">
      <div>
        <h1 className="text-xl font-semibold">Smart Retail Intelligence</h1>
        <p className="text-sm text-slate-500">{user.name || 'Retail user'} · {(user.roles || []).join(', ')}</p>
      </div>
      <button onClick={handleLogout} className="rounded-lg bg-slate-900 px-4 py-2 text-white hover:bg-slate-700">
        Logout
      </button>
    </header>
  )
}
