import { useEffect, useState } from 'react'
import { fetchInsights } from '../api/api'

const prompts = [
  'Generate a monthly retail summary',
  'Which customer segment should we target this week?',
  'Which products are at risk of inventory shortages?',
  'Create a product performance report with bundle ideas',
]

export default function Insights({ user }) {
  const [question, setQuestion] = useState(prompts[0])
  const [insight, setInsight] = useState(null)
  const [loading, setLoading] = useState(false)

  const ask = async (nextQuestion = question) => {
    setLoading(true)
    try {
      const res = await fetchInsights(nextQuestion)
      setInsight(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    ask(prompts[0])
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">LLM Retail Insights</h2>
        <p className="mt-1 text-sm text-slate-500">Ask dynamic questions over sales, customers, baskets, products, and inventory.</p>
      </div>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap gap-2">
          {prompts.map((prompt) => (
            <button
              key={prompt}
              className="rounded-full border border-slate-200 px-3 py-2 text-sm hover:border-cyan-400 hover:text-cyan-700"
              onClick={() => {
                setQuestion(prompt)
                ask(prompt)
              }}
            >
              {prompt}
            </button>
          ))}
        </div>
        <form
          className="mt-4 flex flex-col gap-3 sm:flex-row"
          onSubmit={(event) => {
            event.preventDefault()
            ask()
          }}
        >
          <input
            className="min-w-0 flex-1 rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-cyan-500"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about sales, customers, inventory, or recommendations"
          />
          <button className="rounded-lg bg-slate-950 px-5 py-3 font-semibold text-white hover:bg-slate-800" disabled={loading}>
            {loading ? 'Thinking...' : 'Ask AI'}
          </button>
        </form>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <h3 className="text-lg font-semibold">Answer</h3>
            {insight?.source && <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">{insight.source}</span>}
          </div>
          <p className="mt-4 whitespace-pre-wrap leading-7 text-slate-700">{insight?.insight || 'Ask a question to generate a retail insight.'}</p>
          {insight?.warning && <p className="mt-4 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-700">{insight.warning}</p>}
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">Context Used</h3>
          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between gap-4"><dt className="text-slate-500">User</dt><dd className="font-semibold">{user?.name || 'Retail user'}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Sales</dt><dd className="font-semibold">${Number(insight?.context?.sales?.total_sales || 0).toFixed(0)}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Orders</dt><dd className="font-semibold">{insight?.context?.sales?.order_count || 0}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Top products</dt><dd className="font-semibold">{insight?.context?.top_selling_products?.length || 0}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Basket signals</dt><dd className="font-semibold">{insight?.context?.basket_analysis?.length || 0}</dd></div>
          </dl>
        </div>
      </section>
    </div>
  )
}
