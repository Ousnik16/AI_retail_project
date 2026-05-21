import { useEffect, useState } from 'react'
import { fetchInsights } from '../api/api'

const prompts = [
  'Generate a monthly retail summary',
  'Which customer segment should we target this week?',
  'Which products are at risk of inventory shortages?',
  'Create a product performance report with bundle ideas',
]

function stripMarkdown(value = '') {
  return value.replace(/\*\*/g, '').replace(/`/g, '').trim()
}

function parseInsight(text = '') {
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)
  const blocks = []

  lines.forEach((line) => {
    const cleaned = stripMarkdown(line)
    const bulletMatch = cleaned.match(/^[-*]\s+(.+)/)
    const numberedMatch = cleaned.match(/^\d+[.)]\s+(.+)/)
    const actionMatch = cleaned.match(/^(.{3,48}?):\s+(.+)/)

    if (bulletMatch || numberedMatch) {
      const previous = blocks[blocks.length - 1]
      const content = bulletMatch?.[1] || numberedMatch?.[1]

      if (previous?.type === 'list') {
        previous.items.push(content)
      } else {
        blocks.push({ type: 'list', items: [content] })
      }
      return
    }

    if (actionMatch) {
      blocks.push({
        type: 'callout',
        title: actionMatch[1],
        body: actionMatch[2],
      })
      return
    }

    if (cleaned.length <= 58 && !cleaned.endsWith('.')) {
      blocks.push({ type: 'heading', text: cleaned })
      return
    }

    blocks.push({ type: 'paragraph', text: cleaned })
  })

  return blocks
}

function InsightOutput({ text }) {
  const blocks = parseInsight(text)

  if (!blocks.length) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
        Ask a question to generate a retail insight.
      </div>
    )
  }

  return (
    <div className="mt-5 space-y-4">
      {blocks.map((block, index) => {
        if (block.type === 'heading') {
          return <h4 key={`${block.text}-${index}`} className="pt-2 text-base font-semibold text-slate-950">{block.text}</h4>
        }

        if (block.type === 'list') {
          return (
            <ul key={`list-${index}`} className="space-y-2">
              {block.items.map((item, itemIndex) => (
                <li key={`${item}-${itemIndex}`} className="flex gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-700">
                  <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-emerald-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          )
        }

        if (block.type === 'callout') {
          return (
            <div key={`${block.title}-${index}`} className="rounded-lg border border-cyan-100 bg-cyan-50 px-4 py-3">
              <div className="text-xs font-semibold uppercase text-cyan-700">{block.title}</div>
              <p className="mt-1 leading-7 text-slate-800">{block.body}</p>
            </div>
          )
        }

        return <p key={`${block.text}-${index}`} className="leading-7 text-slate-700">{block.text}</p>
      })}
    </div>
  )
}

export default function Insights({ user }) {
  const [question, setQuestion] = useState(prompts[0])
  const [insight, setInsight] = useState(null)
  const [loading, setLoading] = useState(false)
  const sales = insight?.context?.sales || {}
  const topProducts = insight?.context?.top_selling_products || []
  const basketSignals = insight?.context?.basket_analysis || []
  const customerSegments = insight?.context?.customer_segments || []

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
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold">AI Brief</h3>
                <p className="mt-1 text-sm text-slate-500">{insight?.question || question}</p>
              </div>
              {insight?.source && <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase text-emerald-700">{insight.source}</span>}
            </div>
          </div>
          <div className="px-6 py-6">
            {loading ? (
              <div className="space-y-3">
                <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200" />
                <div className="h-4 w-full animate-pulse rounded bg-slate-200" />
                <div className="h-4 w-5/6 animate-pulse rounded bg-slate-200" />
                <div className="h-20 animate-pulse rounded-lg bg-slate-100" />
              </div>
            ) : (
              <InsightOutput text={insight?.insight} />
            )}
            {insight?.warning && <p className="mt-5 rounded-lg bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-700">{insight.warning}</p>}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold">Context Used</h3>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase text-slate-500">Sales</div>
                <div className="mt-2 text-2xl font-semibold">${Number(sales.total_sales || 0).toFixed(0)}</div>
              </div>
              <div className="rounded-lg bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase text-slate-500">Orders</div>
                <div className="mt-2 text-2xl font-semibold">{sales.order_count || 0}</div>
              </div>
              <div className="rounded-lg bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase text-slate-500">Segments</div>
                <div className="mt-2 text-2xl font-semibold">{customerSegments.length}</div>
              </div>
              <div className="rounded-lg bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase text-slate-500">Baskets</div>
                <div className="mt-2 text-2xl font-semibold">{basketSignals.length}</div>
              </div>
            </div>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between gap-4"><dt className="text-slate-500">User</dt><dd className="font-semibold">{user?.name || 'Retail user'}</dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Top products</dt><dd className="font-semibold">{topProducts.length}</dd></div>
            </dl>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold">Top Signals</h3>
            <div className="mt-4 space-y-3">
              {topProducts.slice(0, 3).map((product) => (
                <div key={product.product_id || product.name} className="rounded-lg border border-slate-200 px-4 py-3">
                  <div className="font-semibold text-slate-900">{product.name || product.product_id}</div>
                  <div className="mt-1 flex justify-between text-sm text-slate-500">
                    <span>{product.category || 'Product'}</span>
                    <span>{product.units || 0} units</span>
                  </div>
                </div>
              ))}
              {!topProducts.length && <p className="text-sm text-slate-500">No product signals available yet.</p>}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
