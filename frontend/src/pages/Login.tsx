import { useState } from 'react'
import { auth } from '../api'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      if (isRegister) {
        await auth.register(username, password)
        setIsRegister(false)
        setError('注册成功，请登录')
      } else {
        const res = await auth.login(username, password)
        localStorage.setItem('token', res.data.access_token)
        navigate('/home')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '操作失败')
    }
  }

  return (
    <div className="container" style={{ maxWidth: 400, marginTop: 100 }}>
      <div className="card">
        <h2>{isRegister ? '注册' : '登录'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>用户名</label>
            <input
              className="input"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>密码</label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p style={{ color: 'red', marginBottom: 12 }}>{error}</p>}
          <button className="btn" type="submit" style={{ width: '100%' }}>
            {isRegister ? '注册' : '登录'}
          </button>
        </form>
        <p style={{ marginTop: 16, textAlign: 'center' }}>
          {isRegister ? '已有账号？' : '没有账号？'}
          <span
            style={{ color: '#007bff', cursor: 'pointer', marginLeft: 4 }}
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? '登录' : '注册'}
          </span>
        </p>
      </div>
    </div>
  )
}