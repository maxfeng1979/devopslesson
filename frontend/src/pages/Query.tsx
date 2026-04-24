import { useState } from 'react'
import { query } from '../api'
import { useNavigate } from 'react-router-dom'

interface FormItem {
  id: number
  name: string
  contact: string
  note: string
  username: string
  created_at: string
}

interface CouponItem {
  id: number
  name: string
  grabbed_at: string
  username: string
}

export default function Query() {
  const [tab, setTab] = useState<'form' | 'coupon'>('form')
  const [keyword, setKeyword] = useState('')
  const [forms, setForms] = useState<FormItem[]>([])
  const [coupons, setCoupons] = useState<CouponItem[]>([])
  const navigate = useNavigate()

  const handleSearch = async () => {
    try {
      if (tab === 'form') {
        const res = await query.forms(keyword || undefined)
        setForms(res.data.forms)
      } else {
        const res = await query.coupons(keyword || undefined)
        setCoupons(res.data.coupons)
      }
    } catch {
      console.error('Search failed')
    }
  }

  return (
    <div className="container">
      <h1>查询</h1>
      <button className="btn" onClick={() => navigate('/home')} style={{ marginBottom: 20 }}>
        返回
      </button>
      <div className="card">
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <button
            className="btn"
            onClick={() => setTab('form')}
            style={{ background: tab === 'form' ? '#007bff' : '#6c757d' }}
          >
            表单记录
          </button>
          <button
            className="btn"
            onClick={() => setTab('coupon')}
            style={{ background: tab === 'coupon' ? '#007bff' : '#6c757d' }}
          >
            优惠券记录
          </button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            className="input"
            placeholder="搜索关键词"
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn" onClick={handleSearch}>搜索</button>
        </div>
      </div>

      {tab === 'form' ? (
        <div className="card">
          <h3>表单记录</h3>
          {forms.length === 0 ? <p>暂无记录</p> : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #ddd' }}>
                  <th style={{ textAlign: 'left', padding: 8 }}>姓名</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>联系方式</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>备注</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>提交人</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>时间</th>
                </tr>
              </thead>
              <tbody>
                {forms.map(f => (
                  <tr key={f.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: 8 }}>{f.name}</td>
                    <td style={{ padding: 8 }}>{f.contact}</td>
                    <td style={{ padding: 8 }}>{f.note}</td>
                    <td style={{ padding: 8 }}>{f.username}</td>
                    <td style={{ padding: 8 }}>{new Date(f.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        <div className="card">
          <h3>优惠券记录</h3>
          {coupons.length === 0 ? <p>暂无记录</p> : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #ddd' }}>
                  <th style={{ textAlign: 'left', padding: 8 }}>优惠券</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>领取人</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>领取时间</th>
                </tr>
              </thead>
              <tbody>
                {coupons.map(c => (
                  <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: 8 }}>{c.name}</td>
                    <td style={{ padding: 8 }}>{c.username}</td>
                    <td style={{ padding: 8 }}>{new Date(c.grabbed_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}