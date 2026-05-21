import { useEffect, useState } from 'react'
import { fetchDashboardOverview } from '../api/api'
import Card from '../components/Card'

const emptyOverview = {
  total_sales: 0,
  order_count: 0,
  active_users: 0,
  customer_insights: [],
  top_selling_products: [],
  basket_analysis: [],
  recommendation_performance: {},
}

export default function Dashboard({ roles = [] }) {
  const [overview, setOverview] = useState(emptyOverview)
  const isAdmin = roles.includes('admin')

  useEffect(() => {
    fetchDashboardOverview().then((res) => setOverview({ ...emptyOverview, ...res.data })).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Dashboard & Analytics</h2>
        <p className="mt-1 text-sm text-slate-500">
          {isAdmin
            ? 'Sales, customers, top products, basket analysis, and recommendation performance.'
            : 'Your retail overview, recommended products, and AI-assisted shopping intelligence.'}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <Card title="Total Sales" value={`$${Number(overview.total_sales || 0).toFixed(2)}`} />
        <Card title="Orders" value={overview.order_count || 0} />
        <Card title={isAdmin ? 'Active Users' : 'Customer Segments'} value={overview.active_users || 0} />
        <Card title="Offer Conversion" value={`${Math.round((overview.recommendation_performance.conversion_rate || 0) * 100)}%`} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">
          <h3 className="text-lg font-semibold">Top-Selling Products</h3>
          <div className="mt-4 overflow-hidden rounded-lg border border-slate-100">
            {overview.top_selling_products.map((product) => (
              <div key={product.product_id} className="grid grid-cols-[1fr_auto] gap-4 border-b border-slate-100 p-4 last:border-b-0">
                <div>
                  <p className="font-medium text-slate-900">{product.name || product.product_id}</p>
                  <p className="text-sm text-slate-500">{product.category || 'Retail product'}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{product.units} units</p>
                  <p className="text-sm text-slate-500">${Number(product.revenue || 0).toFixed(0)}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Recommendation Performance</h3>
          <dl className="mt-4 space-y-4 text-sm">
            <div className="flex items-center justify-between">
              <dt className="text-slate-500">Click-through rate</dt>
              <dd className="font-semibold">{Math.round((overview.recommendation_performance.click_through_rate || 0) * 100)}%</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-slate-500">Conversion rate</dt>
              <dd className="font-semibold">{Math.round((overview.recommendation_performance.conversion_rate || 0) * 100)}%</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-slate-500">Offers generated</dt>
              <dd className="font-semibold">{overview.recommendation_performance.personalized_offers_generated || 0}</dd>
            </div>
          </dl>
        </section>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Customer Insights</h3>
          <div className="mt-4 space-y-3">
            {overview.customer_insights.slice(0, 3).map((customer) => (
              <div key={customer.user_id} className="rounded-lg bg-slate-50 p-4">
                <p className="font-medium">{customer.persona}</p>
                <p className="mt-1 text-sm text-slate-500">
                  {customer.user_id} · {customer.orders} orders · ${Number(customer.total_spent || 0).toFixed(0)}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Common Baskets</h3>
          <div className="mt-4 space-y-3">
            {overview.basket_analysis.slice(0, 4).map((basket, index) => (
              <div key={index} className="rounded-lg bg-slate-50 p-4">
                <p className="font-medium">{basket.products.join(' + ')}</p>
                <p className="mt-1 text-sm text-slate-500">Purchased together {basket.support_count} times</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
