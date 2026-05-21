import { useEffect, useState } from 'react'
import { fetchBasketAnalysis, fetchRecommendations } from '../api/api'

export default function Recommendations({ user }) {
  const [data, setData] = useState({ recommendations: [], personalized_offers: [] })
  const [baskets, setBaskets] = useState([])
  const [userId, setUserId] = useState(user?.email || user?.id || 'customer@retail.ai')

  useEffect(() => {
    fetchRecommendations(userId).then((res) => setData(res.data)).catch(() => {})
    fetchBasketAnalysis().then((res) => setBaskets(res.data.shopping_combinations || [])).catch(() => {})
  }, [userId])

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Product Recommendation Engine</h2>
          <p className="mt-1 text-sm text-slate-500">Similar products, frequently bought items, personalized offers, and basket combinations.</p>
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

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.recommendations.map((item, index) => (
          <div key={index} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-cyan-700">Recommended item</p>
            <h3 className="mt-2 text-lg font-semibold">{item._id}</h3>
            <p className="mt-2 text-sm text-slate-500">{item.reason || `Purchased ${item.count} times by similar customers`}</p>
          </div>
        ))}
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
