import { useEffect, useState } from 'react'
import { fetchReviewSentiment } from '../api/api'

export default function Reviews() {
  const [sentiment, setSentiment] = useState([])

  useEffect(() => {
    fetchReviewSentiment().then((res) => setSentiment(res.data.sentiment || [])).catch(() => setSentiment([]))
  }, [])

  const positive = sentiment.filter((item) => item.label === 'POSITIVE').length
  const negative = sentiment.filter((item) => item.label === 'NEGATIVE').length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Reviews & Sentiment</h2>
        <p className="mt-1 text-sm text-slate-500">Customer review intelligence, product sentiment, and feedback trends.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Analyzed reviews</p>
          <p className="mt-2 text-3xl font-semibold">{sentiment.length}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Positive</p>
          <p className="mt-2 text-3xl font-semibold text-emerald-700">{positive}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Needs attention</p>
          <p className="mt-2 text-3xl font-semibold text-amber-700">{negative}</p>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="space-y-3">
          {sentiment.length > 0 ? (
            sentiment.map((item) => (
              <div key={item.review_id} className="flex items-center justify-between gap-4 rounded-lg bg-slate-50 p-4">
                <div>
                  <p className="font-semibold">{item.product_id}</p>
                  <p className="text-sm text-slate-500">Confidence {(Number(item.score || 0) * 100).toFixed(1)}%</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.label === 'POSITIVE' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                  {item.label}
                </span>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">No review sentiment available yet. Seed data or connect MongoDB to analyze reviews.</p>
          )}
        </div>
      </div>
    </div>
  )
}
