<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slides = ref([])
const currentSlideIndex = ref(0)
const error = ref('')
const isLoading = ref(true)

const currentSlide = computed(() => slides.value[currentSlideIndex.value] || null)
const isFirstSlide = computed(() => currentSlideIndex.value === 0)
const isLastSlide = computed(() => currentSlideIndex.value === slides.value.length - 1)

const fetchSlides = async () => {
  try {
    isLoading.value = true
    error.value = ''
    const response = await presentationApi.getPresentation(presentationId)
    
    if (response.error) {
      throw new Error(response.error)
    }
    
    if (!response.success || !response.presentation?.slides) {
      throw new Error('Failed to fetch presentation slides')
    }
    
    // Sort slides by slide_number and filter out any invalid slides
    slides.value = response.presentation.slides
      .filter(slide => slide && typeof slide === 'object' && slide.slide_id && slide.slide_number)
      .sort((a, b) => a.slide_number - b.slide_number)
    
    if (slides.value.length === 0) {
      throw new Error('No slides found in this presentation')
    }
    
    // Start with the first slide (slide_number === 1)
    currentSlideIndex.value = slides.value.findIndex(slide => slide.slide_number === 1)
    if (currentSlideIndex.value === -1) {
      currentSlideIndex.value = 0 // Fallback to first slide if slide_number 1 not found
    }
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    isLoading.value = false
  }
}

const nextSlide = () => {
  if (!isLastSlide.value) {
    currentSlideIndex.value++
  }
}

const previousSlide = () => {
  if (!isFirstSlide.value) {
    currentSlideIndex.value--
  }
}

const exitPresentation = () => {
  router.push(`/presentations/${presentationId}`)
}

// Handle keyboard navigation
const handleKeyPress = (event) => {
  switch (event.key) {
    case 'ArrowRight':
    case ' ':
      nextSlide()
      break
    case 'ArrowLeft':
      previousSlide()
      break
    case 'Escape':
      exitPresentation()
      break
  }
}

onMounted(() => {
  fetchSlides()
  window.addEventListener('keydown', handleKeyPress)
})

// Cleanup event listener
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<template>
  <div class="play-presentation-container" @click="nextSlide">
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <div v-if="isLoading" class="loading">
      Loading presentation...
    </div>
    
    <div v-else-if="currentSlide" 
         class="slide-display"
         :style="{ backgroundColor: currentSlide.background_color || '#FFFFFF' }">
      <!-- Slide content will go here -->
      <div v-if="currentSlide.background_image_url" 
           class="background-image"
           :style="{ backgroundImage: `url(${currentSlide.background_image_url})` }">
      </div>
    </div>
    
    <!-- Navigation controls -->
    <div class="navigation-controls">
      <button 
        @click.stop="previousSlide" 
        :disabled="isFirstSlide"
        class="nav-button prev-button"
      >
        Previous
      </button>
      
      <span class="slide-counter">
        Slide {{ currentSlide?.slide_number || 0 }} of {{ slides.length }}
      </span>
      
      <button 
        @click.stop="nextSlide" 
        :disabled="isLastSlide"
        class="nav-button next-button"
      >
        Next
      </button>
      
      <button 
        @click.stop="exitPresentation"
        class="exit-button"
      >
        Exit
      </button>
    </div>
  </div>
</template>

<style scoped>
.play-presentation-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 20px;
  box-sizing: border-box;
}

.slide-display {
  width: min(80vw, calc(100vh * 16 / 9 * 0.8));
  aspect-ratio: 16 / 9;
  background-color: white;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  max-height: 80vh;
}

.background-image {
  width: 100%;
  height: 100%;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
}

.navigation-controls {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 20px;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
  padding: 10px 20px;
  border-radius: 8px;
  z-index: 1000;
}

.nav-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.nav-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.nav-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.exit-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.exit-button:hover {
  background-color: #c82333;
}

.slide-counter {
  color: white;
  font-size: 14px;
  min-width: 100px;
  text-align: center;
}

.error-message {
  color: #dc3545;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 10px 20px;
  border-radius: 4px;
  margin: 20px;
  text-align: center;
}

.loading {
  color: white;
  font-size: 18px;
  text-align: center;
}
</style> 