<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import '../assets/styles/main.css'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slides = ref([])
const error = ref('')
const isLoading = ref(true)
const slidesGrid = ref(null)

const slidesGridClass = computed(() => {
  if (!slides.value || slides.value.length === 0) return ''
  if (slides.value.length === 1) return 'slides-center'
  // If the slides fit in the viewport, use space-between, else flex-start
  // We'll use a heuristic: if total slide width + gaps < container width, use space-between
  // Otherwise, use flex-start
  // Each slide: 200px + gap (var(--spacing-md)), container: 100vw - margins
  const slideWidth = 200
  const gap = 24 // fallback for var(--spacing-md)
  const margin = 48 // fallback for edge margin
  const totalWidth = slides.value.length * slideWidth + (slides.value.length - 1) * gap
  if (typeof window !== 'undefined') {
    const containerWidth = window.innerWidth - 2 * margin
    if (totalWidth < containerWidth) return 'slides-between'
  }
  return 'slides-scrollable'
})

const fetchSlides = async () => {
  try {
    isLoading.value = true
    error.value = ''
    const response = await presentationApi.getPresentation(presentationId)
    console.log('Full API Response:', JSON.stringify(response, null, 2))
    
    if (response.error) {
      throw new Error(response.error)
    }
    if (!response.success || !response.presentation) {
      throw new Error('Failed to fetch presentation')
    }
    
    // Log the raw slides data
    // console.log('Raw slides data:', JSON.stringify(response.presentation.slides, null, 2))
    
    // More explicit handling of the slides data
    let presentationSlides = response.presentation.slides
    if (!presentationSlides || !Array.isArray(presentationSlides)) {
      console.log('No slides array found, setting to empty array')
      slides.value = []
    } else if (presentationSlides.length === 1 && presentationSlides[0] === null) {
      console.log('Found [null] slides array, setting to empty array')
      slides.value = []
    } else {
      // Filter out any invalid slides and ensure background color is set
      const validSlides = presentationSlides
        .filter(slide => slide && typeof slide === 'object' && slide.slide_id && slide.slide_number)
        .map(slide => ({
          ...slide,
          background_color: slide.background_color || '#FFFFFF' // Ensure background color is set
        }))
      console.log('Filtered valid slides with background colors:', JSON.stringify(validSlides, null, 2))
      slides.value = validSlides
    }
    
    console.log('Final slides value:', JSON.stringify(slides.value, null, 2))
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error fetching slides:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchSlides)
</script>

<template>
  <div class="slides-viewport">

    <div class="slides-scroll">
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="isLoading" class="loading">Loading slides...</div>
      <div v-else-if="!slides || slides.length === 0" class="no-slides">
        <p>No slides for this presentation.</p>
      </div>
      <div v-else :class="['slides-grid', slidesGridClass]" ref="slidesGrid">
        <template v-for="(slide, index) in slides" :key="slide.slide_id">
          <div v-if="slide && slide.slide_id" 
               class="slide-thumbnail"
               @click="router.push(`/presentations/${presentationId}/slides/${Number(slide.slide_id)}`)"
               role="button"
               tabindex="0"
               @keyup.enter="router.push(`/presentations/${presentationId}/slides/${Number(slide.slide_id)}`)">
            <div class="thumbnail" 
                 :style="{ backgroundColor: slide.background_color }">
              <div v-if="slide.background_image_url" 
                   class="background-image"
                   :style="{ backgroundImage: `url(${slide.background_image_url})` }">
              </div>
            </div>
            <div class="slide-number">Slide {{ slide.slide_number }}</div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slides-viewport {
  display: flex;
  /* flex-direction: row; */
  /* align-items: stretch; */
  /* justify-content: center; */

  /* height: 100vh; */
  /* top: calc(var(--header-height) + var(--spacing-md)); */
  width: 100vw;
  box-sizing: border-box;
  /* padding-top: var(--header-height); */
  position: relative;
  background: var(--background-color);
  overflow: visible;
}

.slides-scroll {
  flex: 1;
  display: flex;
  flex-direction: row;
  /* align-items: center; */
  overflow-x: auto;
  overflow-y: hidden;
  height: 60vh;
  position: relative;
  scroll-behavior: smooth;
  /* Hide scrollbar but keep functionality */
  scrollbar-width: none;  /* Firefox */
  -ms-overflow-style: none;  /* IE and Edge */
}

.slides-scroll::-webkit-scrollbar {
  display: none;  /* Chrome, Safari, Opera */
}

.slides-grid {
  display: flex;
  flex-direction: row;
  gap: var(--spacing-md, 24px);
  min-width: min-content;
  margin: 0 48px;
  width: 100%;
  align-items: center;
}

.slides-center {
  justify-content: center;
}

.slides-between {
  justify-content: space-between;
}

.slides-scrollable {
  justify-content: flex-start;
}

/* .fade-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  pointer-events: none;
  z-index: 2;
  background: linear-gradient(to bottom, var(--background-color) 80%, transparent 100%);
} */

.slide-thumbnail {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  cursor: pointer;
  transition: transform 0.2s ease;
  /* Prevent hover scaling from causing layout shifts */
  transform-origin: center center;
}

.slide-thumbnail:hover {
  transform: scale(1.5);
}

.slide-thumbnail:focus {
  outline: 2px solid var(--secondary-color);
  outline-offset: 2px;
}

.thumbnail {
  width: calc(2vw*16);
  height: calc(2vw*9);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: var(--white);
  box-shadow: var(--shadow);
  /* Prevent thumbnail from shrinking */
  flex-shrink: 0;
}

.background-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.slide-number {
  font-size: 0.875rem;
  color: var(--text-light);
  font-weight: 500;
}

.no-slides {
  text-align: center;
  color: var(--text-light);
  margin: var(--spacing-md) 0;
}
</style>