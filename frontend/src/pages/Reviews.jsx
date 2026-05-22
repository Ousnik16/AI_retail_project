import { useEffect, useState } from 'react'
import { createReview, fetchProducts, fetchReviewSentiment, fetchReviewInsights, getApiErrorMessage } from '../api/api'

const blankReview = {
  product_id: '',
  rating: '5',
  title: '',
  review_text: '',
}

export default function Reviews({ user }) {
  const [sentiment, setSentiment] = useState([])
  const [products, setProducts] = useState([])
  const [form, setForm] = useState(blankReview)
  const [status, setStatus] = useState('')
  const roles = user?.roles || []
  const isCustomer = roles.includes('customer') && !roles.includes('admin')
  const isAdmin = roles.includes('admin')

  const loadSentiment = () => {
    fetchReviewSentiment().then((res) => setSentiment(res.data.sentiment || [])).catch(() => setSentiment([]))
  }

  useEffect(() => {
    loadSentiment()
    fetchProducts().then((res) => setProducts(res.data || [])).catch(() => setProducts([]))
  }, [])

  const positive = sentiment.filter((item) => item.label === 'POSITIVE').length
  const negative = sentiment.filter((item) => item.label === 'NEGATIVE').length
  const [insight, setInsight] = useState(null)
  const [loadingInsight, setLoadingInsight] = useState(false)

  const askInsight = async (q = 'Summarize review-driven business actions') => {
    setLoadingInsight(true)
    try {
      const res = await fetchReviewInsights(q)
      setInsight(res.data)
    } catch (e) {
      setInsight(null)
    } finally {
      setLoadingInsight(false)
    }
  }

  const submitReview = async (event) => {
    event.preventDefault()
    setStatus('')
    try {
      await createReview({
        ...form,
        rating: Number(form.rating),
      })
      setForm(blankReview)
      setStatus('Review submitted. Your feedback is now part of the review intelligence model.')
      loadSentiment()
    } catch (err) {
      setStatus(getApiErrorMessage(err, 'Unable to submit review.'))
    }
  }

  const visibleSentiment = sentiment

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">{isCustomer ? 'Product Reviews' : 'Reviews & Sentiment'}</h2>
        <p className="mt-1 text-sm text-slate-500">
          {isCustomer ? 'Share product feedback so the retail team can improve stock, quality, and recommendations.' : 'Customer review intelligence, product sentiment, and feedback trends.'}
        </p>
      </div>

      {isCustomer && (
        <form onSubmit={submitReview} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="grid gap-4 lg:grid-cols-[1fr_120px]">
            <select
              className="rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-500"
              value={form.product_id}
              onChange={(event) => setForm({ ...form, product_id: event.target.value })}
              required
            >
              <option value="">Select product</option>
              {products.map((product) => (
                <option key={product.sku || product.id} value={product.sku || product.id}>
                  {product.name}
                </option>
              ))}
            </select>
            <select
              className="rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-500"
              value={form.rating}
              onChange={(event) => setForm({ ...form, rating: event.target.value })}
            >
              {[5, 4, 3, 2, 1].map((rating) => (
                <option key={rating} value={rating}>{rating} stars</option>
              ))}
            </select>
          </div>
          <input
            className="mt-4 w-full rounded-lg border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500"
            placeholder="Review title"
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            required
          />
          <textarea
            className="mt-4 min-h-32 w-full rounded-lg border border-slate-300 px-4 py-3 text-sm leading-6 outline-none focus:border-cyan-500"
            placeholder="Tell us what worked, what did not, and whether stock or product quality should be improved."
            value={form.review_text}
            onChange={(event) => setForm({ ...form, review_text: event.target.value })}
            required
          />
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button className="rounded-lg bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800">Submit Review</button>
            {status && <p className="text-sm text-slate-600">{status}</p>}
          </div>
        </form>
      )}

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

      {isAdmin && (
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold">Admin Review Intelligence</h4>
              <p className="text-sm text-slate-500">Generate stock, quality, and merchandising actions from customer reviews.</p>
            </div>
            <button className="rounded-lg bg-slate-950 px-3 py-2 text-sm text-white" onClick={() => askInsight()} disabled={loadingInsight}>
              {loadingInsight ? 'Thinking...' : 'Generate insights'}
            </button>
          </div>

          {insight?.insight && (
            <div className="mt-4 rounded-lg border border-cyan-100 bg-cyan-50 p-4">
              <div className="font-medium">AI Recommendation</div>
              <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-700">{insight.insight}</p>
            </div>
          )}

          {insight?.actions?.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {insight.actions.map((action, index) => (
                <span key={`${action.label}-${index}`} className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
                  {action.label}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h4 className="text-sm font-semibold">{isCustomer ? 'Your Review Signals' : 'Review Sentiment'}</h4>
              <p className="text-sm text-slate-500">Analyzed reviews: {visibleSentiment.length}</p>
            </div>
          </div>

          {visibleSentiment.length > 0 ? (
            visibleSentiment.map((item) => (
              <div key={item.review_id} className="flex items-center justify-between gap-4 rounded-lg bg-slate-50 p-4">
                <div>
                  <p className="font-semibold">{item.title || item.product_id}</p>
                  <p className="text-sm text-slate-500">{item.product_id} - {item.rating || '-'} stars - Confidence {(Number(item.score || 0) * 100).toFixed(1)}%</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.label === 'POSITIVE' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                  {item.label}
                </span>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">{isCustomer ? 'You have not submitted reviews yet.' : 'No review sentiment available yet. Seed data or connect MongoDB to analyze reviews.'}</p>
          )}
        </div>
      </div>
    </div>
  )
}
