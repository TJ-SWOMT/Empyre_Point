<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import '../assets/styles/main.css'

const router = useRouter()
const presentations = ref([])
const error = ref('')
const isLoading = ref(true)
const username = ref('')
const presentationSureness = ref({})

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

const checkSureness = (presentationId, event) => {
  event.preventDefault()
  event.stopPropagation()
  presentationSureness.value[presentationId] = !presentationSureness.value[presentationId]
}

const deletePresentation = async (presentationId, event) => {
  event.preventDefault()
  event.stopPropagation()
  try {
    await presentationApi.deletePresentation(presentationId)
    await fetchPresentations()
  } catch (err) {
    error.value = handleApiError(err)
  }
}

const resetSureness = (presentationId, event) => {
  if (!presentationSureness.value[presentationId]) {
    presentationSureness.value[presentationId] = false
  }
}

onMounted(fetchPresentations)
</script>

<template>
  <div class="container">
    <div class="header_user_presentations">
      <div class="header_user_presentations_text">{{ username }}'s Presentations!!!!!!</div>
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
>
        <h3>{{ presentation.title }}</h3>
        <p v-if="presentation.description">{{ presentation.description }}</p>
        <div class="presentation-meta">
          <span>Created: {{ new Date(presentation.created_at).toLocaleDateString() }}</span>
          <br>
          <span v-if="presentation.slide_count">Slides: {{ presentation.slide_count }}</span>
        </div>
        <button @click="viewPresentation(presentation.presentation_id)" class="btn btn-secondary">View Presentation</button>
        <button 
          @click.stop="presentationSureness[presentation.presentation_id] ? deletePresentation(presentation.presentation_id, $event) : checkSureness(presentation.presentation_id, $event)" 
          class="btn btn-danger"
        >
          {{ !presentationSureness[presentation.presentation_id] ? 'Delete Presentation' : 'Click again to delete' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Only keep component-specific styles that aren't in main.css */
.no-presentations {
  text-align: center;
  padding: var(--spacing-xl);
}

.presentation-meta {
  margin: var(--spacing-md) 0;
  color: var(--text-light);
  font-size: 0.9rem;
}

.presentation-card {
  margin-top: var(--spacing-sm);
  width: 100%;
}

.header_user_presentations {
  /* margin-top: 100px; */
  right: 0;
  top: calc(var(--header-height) - 10px);
  position: fixed;
  color: white;
  background-color: var(--white);
  width: 100%;
  height: 100px;
  display: flex; /* Make the container a flex container */
  align-items: center; /* Vertically center content along the cross-axis */
  justify-content: center;
  box-shadow: inset 10px 10px 100px rgba(53, 89, 126, 1);

}

.header_user_presentations_text {
  background-color: var(--primary-color);
  color: var(--white);
  border: var(--button-border);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  font-size: 2rem;
  font-weight: bold;
}
</style>

