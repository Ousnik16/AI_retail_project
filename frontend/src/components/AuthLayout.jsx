import { Link } from 'react-router-dom'

const highlights = [
  { label: 'Demand sensing', value: 'Live' },
  { label: 'Recommendations', value: 'AI' },
  { label: 'Retail insights', value: '24/7' },
]

export default function AuthLayout({ children, eyebrow, title, subtitle, switchText, switchTo, switchLabel }) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative flex min-h-[360px] flex-col justify-between overflow-hidden bg-[linear-gradient(135deg,#0f172a_0%,#111827_45%,#042f2e_100%)] p-8 sm:p-10 lg:p-12">
          <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-slate-950/70 to-transparent" />
          <div className="relative">
            <Link to="/login" className="inline-flex items-center gap-3 text-lg font-semibold">
              <span className="grid h-11 w-11 place-items-center rounded-lg bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-950/40">
                RI
              </span>
              Smart Retail Intelligence
            </Link>
          </div>

          <div className="relative max-w-2xl py-12 lg:py-0">
            <p className="text-sm font-semibold uppercase text-cyan-200">{eyebrow}</p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
              Turn storefront data into sharper retail decisions.
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-slate-200 sm:text-lg">{subtitle}</p>
          </div>

          <div className="relative grid gap-3 sm:grid-cols-3">
            {highlights.map((item) => (
              <div key={item.label} className="rounded-lg border border-white/15 bg-white/10 p-4 backdrop-blur">
                <p className="text-2xl font-semibold text-white">{item.value}</p>
                <p className="mt-1 text-sm text-slate-200">{item.label}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="flex items-center justify-center bg-slate-50 px-5 py-10 text-slate-900 sm:px-8">
          <div className="w-full max-w-md">
            <div className="rounded-lg border border-slate-200 bg-white p-7 shadow-2xl shadow-slate-200/70 sm:p-9">
              <p className="text-sm font-semibold uppercase text-cyan-700">{eyebrow}</p>
              <h2 className="mt-3 text-3xl font-semibold text-slate-950">{title}</h2>
              {children}
            </div>
            <p className="mt-6 text-center text-sm text-slate-600">
              {switchText}{' '}
              <Link to={switchTo} className="font-semibold text-cyan-700 hover:text-cyan-900">
                {switchLabel}
              </Link>
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}
