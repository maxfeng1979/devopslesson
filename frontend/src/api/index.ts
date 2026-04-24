import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const auth = {
  register: (username: string, password: string) =>
    api.post('/auth/register', { username, password }),
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  me: () => api.get('/auth/me')
}

export const form = {
  submit: (data: { name: string; contact: string; note?: string }) =>
    api.post('/form/submit', data),
  list: () => api.get('/form/list')
}

export const coupon = {
  list: () => api.get('/coupons/list'),
  grab: (couponId: number) => api.post('/coupons/grab', { coupon_id: couponId }),
  my: () => api.get('/coupons/my')
}

export const query = {
  forms: (keyword?: string) => api.get('/query/forms', { params: { keyword } }),
  coupons: (keyword?: string) => api.get('/query/coupons', { params: { keyword } })
}

export default api