<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const router = useRouter()
const presentations = ref([])
const error = ref('')
const isLoading = ref(true)
const username = ref('')

const fetchPresentations = async () => {
  try {
    isLoading.value = true
    const user = JSON.parse(sessionStorage.getItem('user'))
    username.value = user.username
    console.log(user)
    if (!user || !user.user_id) {
      throw new Error('User not found')
    }
    const response = await presentationApi.getUserPresentations(user.user_id)
    console.log('response', response)
    console.log(response.presentations)
    if (response.error) {
      throw new Error(response.error)
    }
    presentations.value = response.presentations || []
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    isLoading.value = false
  }
}

const createNewPresentation = () => {
  router.push('/create-presentation')
}

const viewPresentation = (presentationId) => {
  router.push(`/presentations/${presentationId}`)
}

const deletePresentation = (presentationId) => {
  presentationApi.deletePresentation(presentationId)
}

onMounted(fetchPresentations)
</script>

<template>
  <div class="container">
    <div class="header">
      <h1>{{ username }}'s Presentations</h1>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading">
      Loading presentations...
    </div>

    <div v-else-if="presentations.length === 0" class="no-presentations">
      <p>You haven't created any presentations yet.</p>
      <button @click="createNewPresentation" class="btn btn-secondary">Create Your First Presentation</button>
    </div>

    <div v-else class="presentations-grid">
      <div v-for="presentation in presentations" 
           :key="presentation.presentation_id" 
           class="presentation-card"
           @click="viewPresentation(presentation.presentation_id)">
        <h3>{{ presentation.title }}</h3>
        <p v-if="presentation.description">{{ presentation.description }}</p>
        <div class="presentation-meta">
          <span>Created: {{ new Date(presentation.created_at).toLocaleDateString() }}</span>
          <span v-if="presentation.slide_count">Slides: {{ presentation.slide_count }}</span>
        </div>
        <button @click="viewPresentation(presentation.presentation_id)" class="btn btn-secondary"> View Presentation</button>
        <button @click="deletePresentation(presentation.presentation_id)" class="btn btn-danger"> Delete Presentation</button>
      </div>
    </div>
  </div>
</template>

