import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getApiErrorMessage, registerUser } from '../api/api'
import AuthLayout from '../components/AuthLayout'

export default function Register() {
  const [payload, setPayload] = useState({ email: '', name: '', password: '', role: 'customer' })
  const [status, setStatus] = useState({ type: '', message: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus({ type: '', message: '' })
    setIsSubmitting(true)
    try {
      await registerUser(payload)
      setStatus({ type: 'success', message: 'Registration successful. Redirecting to login...' })
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      setStatus({ type: 'error', message: getApiErrorMessage(err, 'Unable to register user.') })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      eyebrow="Start smarter"
      title="Create account"
      subtitle="Set up your retail workspace and begin exploring product, customer, forecasting, and review intelligence."
      switchText="Already have an account?"
      switchTo="/login"
      switchLabel="Sign in"
    >
      <form onSubmit={handleSubmit} className="mt-7 space-y-5">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Email</span>
          <input
            className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
            type="email"
            placeholder="Email"
            value={payload.email}
            onChange={(e) => setPayload({ ...payload, email: e.target.value })}
            autoComplete="email"
            required
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Name</span>
          <input
            className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
            type="text"
            placeholder="Name"
            value={payload.name}
            onChange={(e) => setPayload({ ...payload, name: e.target.value })}
            autoComplete="name"
            required
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Password</span>
          <input
            className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
            type="password"
            placeholder="Password"
            value={payload.password}
            onChange={(e) => setPayload({ ...payload, password: e.target.value })}
            autoComplete="new-password"
            minLength={6}
            required
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Account type</span>
          <select
            className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
            value={payload.role}
            onChange={(e) => setPayload({ ...payload, role: e.target.value })}
          >
            <option value="customer">Customer</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        {status.message && (
          <p
            className={`rounded-lg px-4 py-3 text-sm ${
              status.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'
            }`}
          >
            {status.message}
          </p>
        )}
        <button
          className="w-full rounded-lg bg-slate-950 px-4 py-3 font-semibold text-white shadow-lg shadow-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating account...' : 'Create account'}
        </button>
      </form>
    </AuthLayout>
  )
}
