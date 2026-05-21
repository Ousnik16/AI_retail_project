import { useEffect, useState } from 'react'
import { fetchForecast } from '../api/api'

export default function Forecasting() {
  const [forecast, setForecast] = useState([])
  const [productId, setProductId] = useState('laptop-pro-15')

  useEffect(() => {
    fetchForecast(productId).then((res) => setForecast(res.data.forecast || [])).catch(() => {})
  }, [productId])

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
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {forecast.slice(0, 8).map((item, index) => (
            <div key={index} className="rounded-lg border border-slate-100 p-4">
              <div className="font-semibold">{new Date(item.ds).toLocaleDateString()}</div>
              <div className="mt-2 text-2xl font-semibold text-slate-950">{Number(item.yhat).toFixed(1)}</div>
              <div className="text-sm text-slate-500">
                Range {Number(item.yhat_lower).toFixed(1)} - {Number(item.yhat_upper).toFixed(1)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
