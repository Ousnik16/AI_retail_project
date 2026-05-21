import { useEffect, useMemo, useState } from 'react'
import { createProduct, fetchProducts, getApiErrorMessage } from '../api/api'

const blankProduct = {
  sku: '',
  name: '',
  category: '',
  price: '',
  brand: '',
  inventory_quantity: '',
  tags: '',
}

export default function Products({ roles = [] }) {
  const [products, setProducts] = useState([])
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('all')
  const [form, setForm] = useState(blankProduct)
  const [status, setStatus] = useState('')
  const isAdmin = roles.includes('admin')

  const loadProducts = () => {
    fetchProducts().then((res) => setProducts(res.data)).catch(() => setProducts([]))
  }

  useEffect(() => {
    loadProducts()
  }, [])

  const categories = useMemo(() => ['all', ...new Set(products.map((product) => product.category).filter(Boolean))], [products])
  const filtered = useMemo(
    () =>
      products.filter((product) => {
        const text = `${product.name} ${product.category} ${product.brand} ${(product.tags || []).join(' ')}`.toLowerCase()
        return text.includes(query.toLowerCase()) && (category === 'all' || product.category === category)
      }),
    [products, query, category],
  )

  const handleCreate = async (event) => {
    event.preventDefault()
    setStatus('')
    try {
      await createProduct({
        ...form,
        price: Number(form.price),
        inventory_quantity: Number(form.inventory_quantity),
        tags: form.tags.split(',').map((tag) => tag.trim()).filter(Boolean),
      })
      setForm(blankProduct)
      setStatus('Product created and catalog refreshed.')
      loadProducts()
    } catch (err) {
      setStatus(getApiErrorMessage(err, 'Unable to create product.'))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Products</h2>
          <p className="mt-1 text-sm text-slate-500">
            {isAdmin ? 'Manage inventory and product metadata.' : 'Explore available products and discover items for your next order.'}
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-[1fr_180px]">
          <input
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm outline-none focus:border-cyan-500"
            placeholder="Search products"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <select className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm" value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((item) => (
              <option key={item} value={item}>
                {item === 'all' ? 'All categories' : item}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isAdmin && (
        <form onSubmit={handleCreate} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-3 md:grid-cols-3">
            {[
              ['sku', 'SKU'],
              ['name', 'Name'],
              ['category', 'Category'],
              ['price', 'Price'],
              ['brand', 'Brand'],
              ['inventory_quantity', 'Inventory'],
              ['tags', 'Tags, comma separated'],
            ].map(([key, label]) => (
              <input
                key={key}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-cyan-500"
                placeholder={label}
                value={form[key]}
                type={key === 'price' || key === 'inventory_quantity' ? 'number' : 'text'}
                onChange={(event) => setForm({ ...form, [key]: event.target.value })}
                required={key !== 'tags'}
              />
            ))}
            <button className="rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800">Add Product</button>
          </div>
          {status && <p className="mt-3 text-sm text-slate-600">{status}</p>}
        </form>
      )}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filtered.length > 0 ? (
          filtered.map((product) => (
            <div key={product.id || product.sku} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold">{product.name}</h3>
                  <p className="text-sm text-slate-500">{product.brand} · {product.category}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${product.inventory_quantity < 45 ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'}`}>
                  {product.inventory_quantity} in stock
                </span>
              </div>
              <p className="mt-4 text-2xl font-semibold">${Number(product.price || 0).toFixed(2)}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(product.tags || []).map((tag) => (
                  <span key={tag} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{tag}</span>
                ))}
              </div>
            </div>
          ))
        ) : (
          <p className="text-slate-500">No products found.</p>
        )}
      </div>
    </div>
  )
}
