import { useEffect, useState } from 'react'
import { fetchForecast, updateInventory } from '../api/api'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts'

const defaultMultiplier = 2

export default function Forecasting({ roles = [] }) {
  const [forecast, setForecast] = useState([])
  const [productId, setProductId] = useState('laptop-pro-15')
  const [multiplier, setMultiplier] = useState(defaultMultiplier)
  const isAdmin = roles.includes('admin')

  useEffect(() => {
    fetchForecast(productId).then((res) => setForecast(res.data.forecast || [])).catch(() => {})
  }, [productId])

  const topUpInventory = async () => {
    if (!isAdmin) return
    try {
      // Sum forecasted demand for next 7 days and request that quantity as top-up
      const next = forecast.slice(0, 7)
      const expected = Math.ceil(next.reduce((s, it) => s + Number(it.yhat || 0), 0) * multiplier)
      await updateInventory([{ product_id: productId, quantity_delta: expected }])
      alert(`Requested inventory top-up of ${expected} units for ${productId}`)
    } catch (e) {
      alert('Unable to request inventory update')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h2 className="text-2xl font-semibold">Demand Forecasting</h2>
          <p className="mt-1 text-sm text-slate-500">Predicts upcoming product demand from transaction history with a demo fallback.</p>
        </div>
        <select
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm"
          value={productId}
          onChange={(event) => setProductId(event.target.value)}
        >
          <option value="laptop-pro-15">Laptop Pro 15</option>
          <option value="wireless-mouse">Wireless Mouse</option>
          <option value="mechanical-keyboard">Mechanical Keyboard</option>
          <option value="gaming-monitor">Gaming Monitor</option>
        </select>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Forecast (next 14 days)</h3>
        <div className="mt-4 h-56">
          <ResponsiveContainer>
            <LineChart data={forecast || []}>
              <XAxis dataKey="ds" tickFormatter={(d) => new Date(d).toLocaleDateString()} />
              <YAxis />
              <Tooltip labelFormatter={(d) => new Date(d).toLocaleDateString()} formatter={(v) => Number(v).toFixed(2)} />
              <Line type="monotone" dataKey="yhat" stroke="#0ea5a4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {forecast.slice(0, 8).map((item, index) => (
            <div key={index} className="rounded-lg border border-slate-100 p-4">
              <div className="font-semibold">{new Date(item.ds).toLocaleDateString()}</div>
              <div className="mt-2 text-2xl font-semibold text-slate-950">{Number(item.yhat).toFixed(1)}</div>
              <div className="text-sm text-slate-500">Range {Number(item.yhat_lower).toFixed(1)} - {Number(item.yhat_upper).toFixed(1)}</div>
            </div>
          ))}
        </div>

        {isAdmin && (
          <div className="mt-6 flex items-center gap-3">
            <label className="text-sm text-slate-600">Top-up multiplier</label>
            <input type="number" min="1" className="w-24 rounded-lg border border-slate-300 px-3 py-2" value={multiplier} onChange={(e) => setMultiplier(Number(e.target.value || 1))} />
            <button className="rounded-lg bg-emerald-600 px-4 py-2 text-white" onClick={topUpInventory}>Request inventory top-up</button>
          </div>
        )}
      </div>
    </div>
  )
}
