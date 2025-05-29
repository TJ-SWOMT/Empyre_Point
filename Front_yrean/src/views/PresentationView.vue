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
.presentation-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  background-color: var(--background-color);
  overflow: hidden;
}

.presentation-header {
  flex: 0 0 auto;
  width: 100%;
  background-color: var(--white);
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-md) 0 var(--spacing-xs) 0;
}

.presentation-title {
  background-color: var(--primary-color);
  color: var(--white);
  border: var(--button-border);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: var(--spacing-xs);
}

.presentation-actions {
  flex: 0 0 auto;
  width: 100%;
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  background-color: var(--background-color);
  box-sizing: border-box;
  padding: var(--spacing-md) 0;
  z-index: 10;
}

.slides-container {
  flex: 1 1 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
  min-height: 0;
}

@media (max-width: 900px) {
  .presentation-header {
    padding: var(--spacing-sm) 0 var(--spacing-xs) 0;
  }
  .presentation-title {
    font-size: 1.5rem;
    padding: var(--spacing-xs) var(--spacing-sm);
  }
  .presentation-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) 0;
  }
}

@media (max-width: 600px) {
  .presentation-header {
    padding: var(--spacing-xs) 0;
  }
  .presentation-title {
    font-size: 1.1rem;
    padding: var(--spacing-xs) var(--spacing-xs);
  }
  .presentation-actions {
    flex-direction: column;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) 0;
  }
}
</style>
