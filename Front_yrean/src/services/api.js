import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001/api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => Promise.reject(error))

// Auth endpoints
export const authApi = {
  async login(username, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password })
    })
    return response.json()
  },

  async register(username, email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password })
    })
    return response.json()
  }
}

// Presentation endpoints
export const presentationApi = {
  
  async createPresentation(user_id, title, description) {
    console.log('title', title)
    console.log('description', description)
    const response = await fetch(`${API_BASE_URL}/presentations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user_id}`
      },
      body: JSON.stringify({ user_id, title, description })
    })
    console.log('response', response)
    return response.json()
  },

  async getPresentation(presentation_id) {
    const response = await fetch(`${API_BASE_URL}/presentations/${presentation_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    return response.json()
  },

  async getUserPresentations(user_id) {
    console.log('user_id', user_id)
    console.log('API_BASE_URL', API_BASE_URL)
    const response = await fetch(`${API_BASE_URL}/user/${user_id}/presentations`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    console.log(response)
    return response.json()
  },

  async updatePresentation(presentation_id, title, description) {
    const response = await fetch(`${API_BASE_URL}/presentations/${presentation_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ title, description })
    })
    return response.json()
  },

  async deletePresentation(presentation_id) {
    const response = await fetch(`${API_BASE_URL}/presentations/${presentation_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    return response.json()
  },

  // Slide endpoints
  async createSlide(presentation_id, slide_number, background_color = '#FFFFFF', background_image_url = null) {
    const response = await fetch(`${API_BASE_URL}/presentations/${presentation_id}/slides`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ slide_number, background_color, background_image_url })
    })
    return response.json()
  },

  async updateSlide(slide_id, slide_number, background_color, background_image_url) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ slide_number, background_color, background_image_url })
    })
    return response.json()
  },

  async deleteSlide(slide_id) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    return response.json()
  }
}

// Helper function to handle API errors
export const handleApiError = (error) => {
  if (error.response) {
    return error.response.data.error || 'An error occurred'
  }
  return error.message || 'An unexpected error occurred'
}

export default api 