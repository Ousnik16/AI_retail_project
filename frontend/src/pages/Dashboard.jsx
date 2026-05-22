import { useEffect, useState } from 'react'
import { fetchDashboardOverview } from '../api/api'
import Card from '../components/Card'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts'

const emptyOverview = {
  total_sales: 0,
  order_count: 0,
  active_users: 0,
  customer_insights: [],
  top_selling_products: [],
  basket_analysis: [],
  recommendation_performance: {},
  total_spent: 0,
  average_order: 0,
  spending_by_day: [],
  spending_by_category: [],
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
        <h2 className="text-2xl font-semibold">{isAdmin ? 'Dashboard & Analytics' : 'My Shopping Dashboard'}</h2>
        <p className="mt-1 text-sm text-slate-500">
          {isAdmin
            ? 'Sales, customers, top products, basket analysis, and recommendation performance.'
            : 'Track your orders, spending trend, and category preferences.'}
        </p>
      </div>

      {isAdmin ? (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <Card title="Total Sales" value={`$${Number(overview.total_sales || 0).toFixed(2)}`} />
          <Card title="Orders" value={overview.order_count || 0} />
          <Card title="Active Users" value={overview.active_users || 0} />
          <Card title="Offer Conversion" value={`${Math.round((overview.recommendation_performance.conversion_rate || 0) * 100)}%`} />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <Card title="Total Spent" value={`$${Number(overview.total_spent || 0).toFixed(2)}`} />
          <Card title="Orders" value={overview.order_count || 0} />
          <Card title="Average Order" value={`$${Number(overview.average_order || 0).toFixed(2)}`} />
          <Card title="Categories" value={(overview.spending_by_category || []).length} />
        </div>
      )}

      {!isAdmin && (
        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold">My Spending Trend</h3>
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <LineChart data={overview.spending_by_day || []}>
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={(v) => `$${v}`} />
                  <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
                  <Line type="monotone" dataKey="total_sales" name="Spent" stroke="#06b6d4" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold">Spending by Category</h3>
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={overview.spending_by_category || []} dataKey="total_spent" nameKey="category" outerRadius={82} fill="#8884d8">
                    {(overview.spending_by_category || []).map((entry, index) => (
                      <Cell key={`customer-cell-${index}`} fill={["#06b6d4", "#0ea5a4", "#7c3aed", "#f97316"][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>
      )}

      {isAdmin && <div className="grid gap-6 xl:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">
          <h3 className="text-lg font-semibold">Sales (last 30 days)</h3>
          <div className="mt-4 h-56">
            <ResponsiveContainer>
              <LineChart data={overview.sales_by_day || []}>
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(v) => `$${v}`} />
                <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
                <Line type="monotone" dataKey="total_sales" stroke="#06b6d4" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="rounded-lg border border-slate-100 p-4">
              <h4 className="text-sm font-medium">Spending by Category</h4>
              <div className="mt-2 h-40">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={overview.spending_by_category || []} dataKey="total_spent" nameKey="category" outerRadius={60} fill="#8884d8">
                      {(overview.spending_by_category || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={["#06b6d4", "#0ea5a4", "#7c3aed", "#f97316"][index % 4]} />
                      ))}
                    </Pie>
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-lg border border-slate-100 p-4">
              <h4 className="text-sm font-medium">Top Products (units)</h4>
              <div className="mt-2 h-40">
                <ResponsiveContainer>
                  <BarChart data={overview.top_selling_products || []} layout="vertical">
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip formatter={(v) => `${v} units`} />
                    <Bar dataKey="units" fill="#06b6d4" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
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
      </div>}

      {isAdmin && <div className="grid gap-6 xl:grid-cols-2">
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
      </div>}
    </div>
  )
}
