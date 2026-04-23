import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Home from './pages/Home'
import Coupon from './pages/Coupon'
import Query from './pages/Query'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token')
  return token ? <>{children}</> : <Navigate to="/" />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<PrivateRoute><Home /></PrivateRoute>} />
        <Route path="/coupon" element={<PrivateRoute><Coupon /></PrivateRoute>} />
        <Route path="/query" element={<PrivateRoute><Query /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}