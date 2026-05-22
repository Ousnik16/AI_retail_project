import { Routes, Route, Navigate } from 'react-router-dom'
import { useMemo } from 'react'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Customers from './pages/Customers'
import Recommendations from './pages/Recommendations'
import Forecasting from './pages/Forecasting'
import Insights from './pages/Insights'
import Reviews from './pages/Reviews'
import Pipeline from './pages/Pipeline'
import Login from './pages/Login'
import Register from './pages/Register'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import './index.css'

function App() {
  const token = localStorage.getItem('access_token')
  const user = useMemo(() => {
    let roles = ['customer']
    try {
      roles = JSON.parse(localStorage.getItem('user_roles') || '["customer"]')
    } catch {
      roles = ['customer']
    }
    return {
      id: localStorage.getItem('user_id') || '',
      email: localStorage.getItem('user_email') || '',
      name: localStorage.getItem('user_name') || '',
      roles,
    }
  }, [token])
  const canAccess = (allowedRoles) => token && allowedRoles.some((role) => user.roles.includes(role))
  const protectedRoute = (element, allowedRoles = ['admin', 'customer']) =>
    canAccess(allowedRoles) ? element : <Navigate to={token ? '/dashboard' : '/login'} />

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {token && <Sidebar roles={user.roles} />}
      <div className={token ? 'md:pl-64' : ''}>
        {token && <Navbar user={user} />}
        <main className={token ? 'p-6' : 'p-0'}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={protectedRoute(<Dashboard roles={user.roles} />)} />
            <Route path="/products" element={protectedRoute(<Products roles={user.roles} />)} />
            <Route path="/customers" element={protectedRoute(<Customers />, ['admin'])} />
            <Route path="/pipeline" element={protectedRoute(<Pipeline />, ['admin'])} />
            <Route path="/recommendations" element={protectedRoute(<Recommendations user={user} />)} />
            <Route path="/forecasting" element={protectedRoute(<Forecasting />, ['admin'])} />
            <Route path="/insights" element={protectedRoute(<Insights user={user} />)} />
            <Route path="/reviews" element={protectedRoute(<Reviews user={user} />, ['admin', 'customer'])} />
            <Route path="/*" element={<Navigate to={token ? '/dashboard' : '/login'} />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
