const API_BASE_URL = 'http://localhost:5001/api'

const getAuthHeader = () => {
  const userData = sessionStorage.getItem('user')
  if (!userData) return {}
  try {
    const user = JSON.parse(userData)
    return {
      'Authorization': `Bearer ${user.user_id}`
    }
  } catch (err) {
    console.error('Error parsing user data:', err)
    return {}
  }
}

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
        ...getAuthHeader()
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
        ...getAuthHeader()
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
        ...getAuthHeader()
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
        ...getAuthHeader()
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
        ...getAuthHeader()
      }
    })
    return response.json()
  },

  // Slide endpoints
  async createSlide(presentation_id, slide_number, background_color = '#FFFFFF', background_image_url = null, title = '') {
    const response = await fetch(`${API_BASE_URL}/presentations/${presentation_id}/slides`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ slide_number, background_color, background_image_url, title })
    })
    return response.json()
  },

  async updateSlide(slide_id, slide_number, background_color, background_image_url, title) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ slide_number, background_color, background_image_url, title })
    })
    return response.json()
  },

  async deleteSlide(slide_id) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    })
    return response.json()
  },

  // Element endpoints
  async getSlideElements(slide_id) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}/elements`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    })
    return response.json()
  },

  async createTextElement(slide_id, elementData) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}/elements/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({
        ...elementData,
        element_type: 'text'
      })
    })
    return response.json()
  },

  async updateElement(element_id, elementData) {
    const response = await fetch(`${API_BASE_URL}/elements/${element_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(elementData)
    })
    return response.json()
  },

  async deleteElement(element_id) {
    const response = await fetch(`${API_BASE_URL}/elements/${element_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      }
    })
    return response.json()
  },

  // Image upload endpoint
  async uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/upload/image`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: formData
    })
    return response.json()
  },

  // Image element endpoints
  async createImageElement(slide_id, elementData) {
    const response = await fetch(`${API_BASE_URL}/slides/${slide_id}/elements/image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({
        ...elementData,
        element_type: 'image'
      })
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