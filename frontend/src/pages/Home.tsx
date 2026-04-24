import { useState } from 'react'
import { auth, form as formApi } from '../api'
import { useNavigate } from 'react-router-dom'

export default function Home() {
  const [username, setUsername] = useState('')
  const [name, setName] = useState('')
  const [contact, setContact] = useState('')
  const [note, setNote] = useState('')
  const [msg, setMsg] = useState('')
  const navigate = useNavigate()

  useState(() => {
    auth.me().then(res => setUsername(res.data.username)).catch(() => navigate('/'))
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await formApi.submit({ name, contact, note })
      setMsg('提交成功')
      setName('')
      setContact('')
      setNote('')
    } catch {
      setMsg('提交失败')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/')
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1>欢迎 {username}</h1>
        <button className="btn" onClick={handleLogout}>退出</button>
      </div>
      <div className="card">
        <h2>测试表单</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>姓名</label>
            <input className="input" value={name} onChange={e => setName(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>联系方式</label>
            <input className="input" value={contact} onChange={e => setContact(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>备注</label>
            <input className="input" value={note} onChange={e => setNote(e.target.value)} />
          </div>
          <button className="btn" type="submit">提交</button>
          {msg && <span style={{ marginLeft: 12 }}>{msg}</span>}
        </form>
      </div>
      <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
        <button className="btn" onClick={() => navigate('/coupon')}>抢优惠券</button>
        <button className="btn" onClick={() => navigate('/query')}>查询</button>
      </div>
    </div>
  )
}