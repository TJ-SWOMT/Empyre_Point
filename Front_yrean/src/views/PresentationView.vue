<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import PresentationSlidesView from './PresentationSlidesView.vue'
import { useRouter } from 'vue-router'
import '../assets/styles/main.css'

const route = useRoute()
const presentationId = route.params.id
const presentationTitle = ref('')
const router = useRouter()
const hasSlides = ref(false)
const error = ref('')

const checkForSlides = async () => {
  try {
    const response = await presentationApi.getPresentation(presentationId)
    console.log('response', response)
    if (response.success && response.presentation.slides[0].slide_number) {
      hasSlides.value = response.presentation.slides.length > 0
    }
    if (response.success && response.presentation?.title){
        presentationTitle.value = response.presentation.title
    } else {
        presentationTitle.value = 'Presentation ' + presentationId
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
    <div class="presentation-header">
      <div class="presentation-title" v-if=presentationTitle>{{ presentationTitle }}</div>
      <div class="presentation-title" v-else>Your Presentation</div>
      <div v-if="error" class="error-message">{{ error }}</div>

    </div>
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

    <div class="slides-container">
      <PresentationSlidesView />
    </div>
  </div>
</template>
<style scoped>
.presentation-header {
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

.presentation-title {
  background-color: var(--primary-color);
  color: var(--white);
  border: var(--button-border);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  font-size: 2rem;
  font-weight: bold;
}
</style>
