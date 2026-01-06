import api from './index'

export default {
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  
  register(userData) {
    return api.post('/auth/register', userData)
  },
  
  getProfile() {
    return api.get('/auth/profile')
  },
  
  updateProfile(userData) {
    return api.put('/auth/profile', userData)
  },
  
  getUsers() {
    return api.get('/auth/users')
  }
}

