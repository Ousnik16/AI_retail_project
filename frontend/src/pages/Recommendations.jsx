import { useEffect, useState } from 'react'
import { fetchBasketAnalysis, fetchRecommendations, ingestTransaction } from '../api/api'

export default function Recommendations({ user }) {
  const [data, setData] = useState({ recommendations: [], personalized_offers: [] })
  const [baskets, setBaskets] = useState([])
  const [userId, setUserId] = useState(user?.email || user?.id || 'customer@retail.ai')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadData = () => {
    fetchRecommendations(userId).then((res) => setData(res.data)).catch(() => {})
    fetchBasketAnalysis().then((res) => setBaskets(res.data.shopping_combinations || [])).catch(() => {})
  }

  useEffect(() => {
    loadData()
  }, [userId])

  const handlePurchase = async (item) => {
    if (!userId) {
      setError('Please enter a customer ID before purchasing.')
      return
    }

    setMessage('')
    setError('')

    try {
      await ingestTransaction({
        user_id: userId,
        channel: 'online',
        items: [
          {
            product_id: item.product_id || item._id,
            name: item.name || item._id || item.product_id,
            category: item.category || 'General',
            quantity: 1,
            unit_price: item.price || 0,
          },
        ],
      })

      setMessage(`Purchased ${item.name || item.product_id || item._id} for ${userId}. Recommendations updated.`)
      loadData()
    } catch (purchaseError) {
      setError('Unable to record purchase. Please try again.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Product Recommendation Engine</h2>
          <p className="mt-1 text-sm text-slate-500">Customer-specific recommendations driven by actual purchase behavior and recent order history.</p>
        </div>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-600">Customer ID</span>
          <input
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm outline-none focus:border-cyan-500"
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
          />
        </label>
      </div>

      {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{message}</div>}
      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">{error}</div>}

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Customer profile</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            <div>Orders: <span className="font-semibold">{data.user_profile?.orders || 0}</span></div>
            <div>Total spent: <span className="font-semibold">${Number(data.user_profile?.total_spent || 0).toFixed(2)}</span></div>
            <div>Top categories: <span className="font-semibold">{(data.user_profile?.top_categories || []).join(', ') || 'None yet'}</span></div>
            <div>Top brands: <span className="font-semibold">{(data.user_profile?.top_brands || []).join(', ') || 'None yet'}</span></div>
            <div>Favorite category: <span className="font-semibold">{data.user_profile?.favorite_category || 'N/A'}</span></div>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
          <h3 className="text-lg font-semibold">Recent purchases</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            {data.recent_purchases?.length > 0 ? (
              data.recent_purchases.map((item, index) => (
                <div key={`${item.product_id}-${index}`} className="rounded-lg bg-slate-50 p-4">
                  <p className="font-medium">{item.name}</p>
                  <p className="mt-1 text-slate-500">Qty {item.quantity} · {new Date(item.purchased_at).toLocaleDateString()}</p>
                </div>
              ))
            ) : (
              <p className="text-slate-500">No recent purchases found for this customer.</p>
            )}
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.recommendations.length > 0 ? (
          data.recommendations.map((item, index) => (
            <div key={index} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-medium text-cyan-700">Recommended item</p>
              <h3 className="mt-2 text-lg font-semibold">{item.name || item._id || item.product_id}</h3>
              <p className="mt-1 text-sm text-slate-500">{item.category || 'General'}</p>
              <p className="mt-2 text-sm text-slate-500">{item.reason || `Purchased ${item.count} times by similar customers`}</p>
              <p className="mt-4 text-lg font-semibold">${Number(item.price || 0).toFixed(2)}</p>
              <button
                className="mt-4 inline-flex items-center justify-center rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-700"
                type="button"
                onClick={() => handlePurchase(item)}
              >
                Buy now
              </button>
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:col-span-2 lg:col-span-3">
            <p className="text-sm text-slate-500">No personalized recommendations available for this customer yet.</p>
          </div>
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Personalized Offers</h3>
          <div className="mt-4 space-y-3">
            {(data.personalized_offers || []).map((offer) => (
              <div key={offer} className="rounded-lg bg-emerald-50 px-4 py-3 font-medium text-emerald-800">
                {offer}
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Basket Analysis</h3>
          <div className="mt-4 space-y-3">
            {baskets.map((basket, index) => (
              <div key={index} className="rounded-lg bg-slate-50 p-4">
                <p className="font-medium">{basket.products.join(' + ')}</p>
                <p className="mt-1 text-sm text-slate-500">Support count: {basket.support_count}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
