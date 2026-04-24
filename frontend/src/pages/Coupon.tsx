import { useState, useEffect } from 'react'
import { coupon } from '../api'
import { useNavigate } from 'react-router-dom'

interface CouponItem {
  id: number
  name: string
  total: number
  remaining: number
}

export default function Coupon() {
  const [coupons, setCoupons] = useState<CouponItem[]>([])
  const [msg, setMsg] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadCoupons()
  }, [])

  const loadCoupons = async () => {
    try {
      const res = await coupon.list()
      setCoupons(res.data.coupons)
    } catch {
      console.error('Failed to load coupons')
    }
  }

  const handleGrab = async (id: number) => {
    try {
      await coupon.grab(id)
      setMsg('抢券成功')
      loadCoupons()
    } catch (err: any) {
      setMsg(err.response?.data?.detail || '抢券失败')
    }
  }

  return (
    <div className="container">
      <h1>抢优惠券</h1>
      <button className="btn" onClick={() => navigate('/home')} style={{ marginBottom: 20 }}>
        返回
      </button>
      {msg && <p style={{ color: msg.includes('成功') ? 'green' : 'red', marginBottom: 12 }}>{msg}</p>}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 16 }}>
        {coupons.map(c => (
          <div key={c.id} className="card">
            <h3>{c.name}</h3>
            <p>剩余: {c.remaining} / {c.total}</p>
            <button
              className="btn"
              onClick={() => handleGrab(c.id)}
              disabled={c.remaining === 0}
              style={{ marginTop: 8 }}
            >
              {c.remaining === 0 ? '已抢完' : '立即抢'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}