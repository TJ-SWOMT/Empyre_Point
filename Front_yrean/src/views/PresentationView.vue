<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import PresentationSlidesView from './PresentationSlidesView.vue'
import { useRouter } from 'vue-router'

const route = useRoute()
const presentationId = route.params.id
const router = useRouter()
const hasSlides = ref(false)
const error = ref('')

const checkForSlides = async () => {
  try {
    const response = await presentationApi.getPresentation(presentationId)
    if (response.success && response.presentation?.slides) {
      hasSlides.value = response.presentation.slides.length > 0
    }
  } catch (err) {
    error.value = handleApiError(err)
  }
}

const addSlide = () => {
  router.push(`/presentations/${presentationId}/slides/new`)
}

const playPresentation = () => {
  console.log('Navigating to play presentation:', `/presentations/${presentationId}/play`)
  console.log('Current route:', route.path)
  console.log('Presentation ID:', presentationId)
  router.push(`/presentations/${presentationId}/play`).catch(err => {
    console.error('Navigation error:', err)
    error.value = 'Failed to navigate to presentation play mode'
  })
}

onMounted(checkForSlides)
</script>

<template>
  <div class="presentation-container">
    <h1>Presentation {{ presentationId }}</h1>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div class="presentation-actions">
      <button @click="addSlide">Add Slide</button>
      <button 
        v-if="hasSlides" 
        @click="playPresentation"
        class="play-button"
      >
        Play Presentation
      </button>
    </div>
    <PresentationSlidesView />
  </div>
</template>

<style scoped>
.presentation-container {
  padding: 20px;
}

.presentation-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.play-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.play-button:hover {
  background-color: #218838;
}

.error-message {
  color: #dc3545;
  margin: 10px 0;
}
</style>
