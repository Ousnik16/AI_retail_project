import { useEffect, useState } from 'react'
import { fetchCustomerInsights, fetchReviewInsights } from '../api/api'

export default function Customers() {
  const [segments, setSegments] = useState([])

  useEffect(() => {
    fetchCustomerInsights().then((res) => setSegments(res.data.customer_segments || [])).catch(() => {})
  }, [])

  const [insights, setInsights] = useState({})
  const [loadingInsight, setLoadingInsight] = useState(null)

  const loadCustomerInsight = async (userId) => {
    setLoadingInsight(userId)
    try {
      const res = await fetchReviewInsights(`Generate review insights for ${userId}`, userId)
      setInsights((s) => ({ ...s, [userId]: res.data }))
    } catch (e) {
      setInsights((s) => ({ ...s, [userId]: { insight: 'Unable to generate insights.' } }))
    } finally {
      setLoadingInsight(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Customer Behaviour Analysis</h2>
        <p className="mt-1 text-sm text-slate-500">Purchase frequency, buying patterns, preferred categories, and seasonal behaviour.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {segments.map((customer) => (
          <div key={customer.user_id} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold">{customer.persona}</h3>
                <p className="text-sm text-slate-500">{customer.user_id}</p>
              </div>
              <span className="rounded-full bg-cyan-50 px-3 py-1 text-sm font-medium text-cyan-700">
                {customer.orders} orders
              </span>
            </div>
            <dl className="mt-5 grid gap-3 text-sm sm:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-slate-500">Purchase frequency</dt>
                <dd className="font-semibold">{customer.purchase_frequency || customer.orders} purchases</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-slate-500">Total spent</dt>
                <dd className="font-semibold">${Number(customer.total_spent || 0).toFixed(0)}</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3 sm:col-span-2">
                <dt className="text-slate-500">Preferred categories</dt>
                <dd className="font-semibold">{(customer.preferred_categories || []).join(', ') || 'General retail'}</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3 sm:col-span-2">
                <dt className="text-slate-500">Seasonal behaviour</dt>
                <dd className="font-semibold">{customer.seasonal_behaviour || 'Not enough seasonal data yet'}</dd>
              </div>
              <div className="sm:col-span-2">
                <button
                  className="mt-3 rounded-lg bg-slate-950 px-3 py-2 text-sm font-semibold text-white"
                  onClick={() => loadCustomerInsight(customer.user_id)}
                >
                  {loadingInsight === customer.user_id ? 'Thinking...' : 'Analyze reviews for this customer'}
                </button>

                {insights[customer.user_id]?.insight && (
                  <div className="mt-3 rounded-lg border border-slate-100 bg-slate-50 p-3 text-sm">
                    <div className="font-semibold">Review-driven insight</div>
                    <div className="mt-2">{insights[customer.user_id].insight}</div>
                  </div>
                )}
              </div>
            </dl>
          </div>
        ))}
      </div>
    </div>
  )
}
