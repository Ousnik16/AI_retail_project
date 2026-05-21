export default function Card({ title, value, children }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-3 text-sm uppercase tracking-wider text-slate-500">{title}</div>
      <div className="text-3xl font-semibold text-slate-900">{value}</div>
      <div className="mt-4 text-slate-600">{children}</div>
    </div>
  )
}
