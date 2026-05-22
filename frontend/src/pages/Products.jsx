import { useEffect, useMemo, useState } from 'react'
import { createProduct, deleteProduct, fetchProducts, getApiErrorMessage, updateProduct } from '../api/api'

const blankProduct = {
  sku: '',
  name: '',
  category: '',
  price: '',
  brand: '',
  inventory_quantity: '',
  stock_alert_threshold: '10',
  tags: '',
}

const productFields = [
  ['sku', 'SKU'],
  ['name', 'Name'],
  ['category', 'Category'],
  ['price', 'Price'],
  ['brand', 'Brand'],
  ['inventory_quantity', 'Inventory'],
  ['stock_alert_threshold', 'Stock alert threshold'],
  ['tags', 'Tags, comma separated'],
]

function toProductPayload(values) {
  return {
    ...values,
    price: Number(values.price),
    inventory_quantity: Number(values.inventory_quantity),
    stock_alert_threshold: Number(values.stock_alert_threshold),
    tags: values.tags.split(',').map((tag) => tag.trim()).filter(Boolean),
  }
}

export default function Products({ roles = [] }) {
  const [products, setProducts] = useState([])
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('all')
  const [form, setForm] = useState(blankProduct)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState(blankProduct)
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
      await createProduct(toProductPayload(form))
      setForm(blankProduct)
      setStatus('Product created and catalog refreshed.')
      loadProducts()
    } catch (err) {
      setStatus(getApiErrorMessage(err, 'Unable to create product.'))
    }
  }

  const startEditing = (product) => {
    setEditingId(product.id || product.sku)
    setEditForm({
      sku: product.sku || '',
      name: product.name || '',
      category: product.category || '',
      price: String(product.price ?? ''),
      brand: product.brand || '',
      inventory_quantity: String(product.inventory_quantity ?? ''),
      stock_alert_threshold: String(product.stock_alert_threshold ?? 10),
      tags: (product.tags || []).join(', '),
    })
  }

  const handleUpdate = async (event, product) => {
    event.preventDefault()
    const productId = product.id || product.sku
    setStatus('')
    try {
      await updateProduct(productId, toProductPayload(editForm))
      setEditingId(null)
      setStatus(`${editForm.name} updated.`)
      loadProducts()
    } catch (err) {
      setStatus(getApiErrorMessage(err, 'Unable to update product.'))
    }
  }

  const handleDelete = async (product) => {
    const productId = product.id || product.sku
    setStatus('')
    try {
      await deleteProduct(productId)
      setStatus(`${product.name} deleted from the catalog.`)
      loadProducts()
    } catch (err) {
      setStatus(getApiErrorMessage(err, 'Unable to delete product.'))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Products</h2>
          <p className="mt-1 text-sm text-slate-500">
            {isAdmin ? 'Manage inventory, product metadata, and stock alerts.' : 'Explore available products and discover items for your next order.'}
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
            {productFields.map(([key, label]) => (
              <input
                key={key}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-cyan-500"
                placeholder={label}
                value={form[key]}
                type={key === 'price' || key === 'inventory_quantity' || key === 'stock_alert_threshold' ? 'number' : 'text'}
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
          filtered.map((product) => {
            const productId = product.id || product.sku
            const threshold = Number(product.stock_alert_threshold ?? 10)
            const inventory = Number(product.inventory_quantity || 0)
            const stockAlert = inventory <= threshold

            return (
              <div key={productId} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                {editingId === productId ? (
                  <form onSubmit={(event) => handleUpdate(event, product)} className="space-y-3">
                    <div className="grid gap-3 sm:grid-cols-2">
                      {productFields.map(([key, label]) => (
                        <input
                          key={key}
                          className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-cyan-500"
                          placeholder={label}
                          value={editForm[key]}
                          type={key === 'price' || key === 'inventory_quantity' || key === 'stock_alert_threshold' ? 'number' : 'text'}
                          onChange={(event) => setEditForm({ ...editForm, [key]: event.target.value })}
                          required={key !== 'tags'}
                        />
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button className="rounded-lg bg-slate-950 px-3 py-2 text-sm font-semibold text-white">Save</button>
                      <button type="button" className="rounded-lg border border-slate-200 px-3 py-2 text-sm" onClick={() => setEditingId(null)}>
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <>
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold">{product.name}</h3>
                        <p className="text-sm text-slate-500">{product.brand} - {product.category}</p>
                      </div>
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${stockAlert ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-700'}`}>
                        {inventory} in stock
                      </span>
                    </div>

                    {isAdmin && stockAlert && (
                      <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                        Stock alert: inventory is at or below the threshold of {threshold}.
                      </div>
                    )}

                    <p className="mt-4 text-2xl font-semibold">${Number(product.price || 0).toFixed(2)}</p>
                    {isAdmin && <p className="mt-1 text-sm text-slate-500">Alert threshold: {threshold}</p>}

                    <div className="mt-4 flex flex-wrap gap-2">
                      {(product.tags || []).map((tag) => (
                        <span key={tag} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{tag}</span>
                      ))}
                    </div>

                    {isAdmin && (
                      <div className="mt-5 flex flex-wrap gap-2">
                        <button className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold hover:bg-slate-50" onClick={() => startEditing(product)}>
                          Edit product
                        </button>
                        <button className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 hover:bg-rose-100" onClick={() => handleDelete(product)}>
                          Delete product
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            )
          })
        ) : (
          <p className="text-slate-500">No products found.</p>
        )}
      </div>
    </div>
  )
}
