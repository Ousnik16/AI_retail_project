import { useEffect, useState } from 'react'
import { fetchStreamEvents, ingestBrowsingEvent, ingestOnlineOrder, ingestTransaction } from '../api/api'

const demoTransaction = {
  user_id: 'demo_user_id',
  channel: 'store',
  items: [
    { product_id: 'laptop-pro-15', name: 'Laptop Pro 15', category: 'Computers', quantity: 1, unit_price: 1299 },
    { product_id: 'wireless-mouse', name: 'Wireless Mouse', category: 'Accessories', quantity: 1, unit_price: 39 },
  ],
}

export default function Pipeline() {
  const [events, setEvents] = useState([])
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  const refreshEvents = () => {
    fetchStreamEvents()
      .then((res) => setEvents(res.data.events || []))
      .catch(() => setEvents([]))
  }

  useEffect(() => {
    refreshEvents()
    const timer = setInterval(refreshEvents, 5000)
    return () => clearInterval(timer)
  }, [])

  const runAction = async (label, action) => {
    setMessage('')
    setError('')
    setIsRunning(true)
    try {
      await action()
      setMessage(`${label} completed`)
      refreshEvents()
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail || err.response?.data?.message
      setError(detail || (status ? `Request failed with status ${status}.` : 'Unable to reach the retail pipeline API.'))
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Transaction Ingestion & Streaming Pipeline</h2>
        <p className="mt-1 text-sm text-slate-500">Collect transactions, online orders, purchases, browsing history, and inventory updates.</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <button
          className="rounded-lg border border-slate-200 bg-white p-6 text-left shadow-sm hover:border-cyan-400"
          disabled={isRunning}
          onClick={() => runAction('Live transaction ingestion', () => ingestTransaction(demoTransaction))}
        >
          <p className="font-semibold">Ingest Retail Transaction</p>
          <p className="mt-2 text-sm text-slate-500">Adds a store purchase and updates inventory in real time.</p>
        </button>
        <button
          className="rounded-lg border border-slate-200 bg-white p-6 text-left shadow-sm hover:border-cyan-400"
          disabled={isRunning}
          onClick={() => runAction('Online order analysis', () => ingestOnlineOrder({ ...demoTransaction, channel: 'online' }))}
        >
          <p className="font-semibold">Ingest Online Order</p>
          <p className="mt-2 text-sm text-slate-500">Streams an order event into recommendation and analytics data.</p>
        </button>
        <button
          className="rounded-lg border border-slate-200 bg-white p-6 text-left shadow-sm hover:border-cyan-400"
          disabled={isRunning}
          onClick={() =>
            runAction('Browsing history ingestion', () =>
              ingestBrowsingEvent({
                user_id: 'demo_user_id',
                product_id: 'gaming-monitor',
                product_name: 'Gaming Monitor',
                category: 'Displays',
                event_type: 'view',
                session_id: 'demo-session',
              }),
            )
          }
        >
          <p className="font-semibold">Capture Browsing Event</p>
          <p className="mt-2 text-sm text-slate-500">Records product browsing history for behavior analysis.</p>
        </button>
      </div>

      {message && <div className="rounded-lg bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">{message}</div>}
      {error && <div className="rounded-lg bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{error}</div>}

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Live Stream Events</h3>
        <div className="mt-4 space-y-3">
          {events.length > 0 ? (
            events.map((event, index) => (
              <div key={index} className="rounded-lg bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-4">
                  <p className="font-medium">{event.type}</p>
                  <p className="text-xs text-slate-500">{new Date(event.created_at).toLocaleTimeString()}</p>
                </div>
                <pre className="mt-2 max-h-28 overflow-auto text-xs text-slate-500">{JSON.stringify(event.payload, null, 2)}</pre>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">No stream events yet. Run one ingestion action above.</p>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold">PySpark Data Cleaning Coverage</h3>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {['Remove duplicates', 'Handle missing values', 'Normalize product names', 'Clean transaction logs'].map((item) => (
            <div key={item} className="rounded-lg bg-cyan-50 px-4 py-3 text-sm font-medium text-cyan-800">
              {item}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
