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
const slideElements = ref({})

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

const fetchSlideElements = async (slideId) => {
  try {
    const response = await presentationApi.getSlideElements(slideId)
    if (response.success && response.elements) {
      // Store both text and image elements
      slideElements.value[slideId] = response.elements
        .filter(element => element.element_type === 'text' || element.element_type === 'image')
        .map(element => ({
          element_id: element.element_id,
          element_type: element.element_type,
          x_position: parseFloat(element.x_position),
          y_position: parseFloat(element.y_position),
          width: parseFloat(element.width),
          height: parseFloat(element.height),
          z_index: element.z_index || 0,
          content: element.element_type === 'text' ? element.element_data?.content || '' : null
        }))
    }
  } catch (err) {
    console.error('Error fetching slide elements:', err)
  }
}

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
    
    let presentationSlides = response.presentation.slides
    if (!presentationSlides || !Array.isArray(presentationSlides)) {
      console.log('No slides array found, setting to empty array')
      slides.value = []
    } else if (presentationSlides.length === 1 && presentationSlides[0] === null) {
      console.log('Found [null] slides array, setting to empty array')
      slides.value = []
    } else {
      const validSlides = presentationSlides
        .filter(slide => slide && typeof slide === 'object' && slide.slide_id && slide.slide_number)
        .map(slide => ({
          ...slide,
          background_color: slide.background_color || '#FFFFFF'
        }))
      slides.value = validSlides
      
      // Fetch elements for all slides
      await Promise.all(slides.value.map(slide => fetchSlideElements(slide.slide_id)))
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
               <div class="slide-title">{{ slide.title ? slide.title : 'Untitled' }}</div>
            <div class="thumbnail" 
                 :style="{ backgroundColor: slide.background_color }">
              <div v-if="slide.background_image_url" 
                   class="background-image"
                   :style="{ backgroundImage: `url(${slide.background_image_url})` }">
              </div>
              <!-- Only show text elements on hover -->
              <div class="thumbnail-text-elements">
                <template v-for="element in slideElements[slide.slide_id]" :key="element.element_id">
                  <!-- Text elements -->
                  <div v-if="element.element_type === 'text'"
                       class="thumbnail-text-element"
                       :style="{
                         left: `${(element.x_position / 960) * 100}%`,
                         top: `${(element.y_position / 540) * 100}%`,
                         width: `${(element.width / 960) * 100}%`,
                         height: `${(element.height / 540) * 100}%`,
                         zIndex: element.z_index
                       }">
                    {{ element.content }}
                  </div>
                  <!-- Image elements -->
                  <div v-else-if="element.element_type === 'image'"
                       class="thumbnail-image-block"
                       :style="{
                         left: `${(element.x_position / 960) * 100}%`,
                         top: `${(element.y_position / 540) * 100}%`,
                         width: `${(element.width / 960) * 100}%`,
                         height: `${(element.height / 540) * 100}%`,
                         zIndex: element.z_index
                       }">
                    <div class="image-dimensions">{{ Math.round(element.width) }}×{{ Math.round(element.height) }}</div>
                  </div>
                </template>
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
  width: 100%;
  box-sizing: border-box;
  position: relative;
  background: var(--background-color);
  overflow: visible;
  padding: var(--spacing-md) 0;
}

.slides-scroll {
  flex: 1;
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  overflow-y: hidden;
  height: clamp(300px, 60vh, 600px);
  position: relative;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
  scroll-snap-type: x mandatory; /* Snap to slides */
  scrollbar-width: none;  /* Firefox */
  -ms-overflow-style: none;  /* IE and Edge */
  padding: var(--spacing-md) 0;
}

.slides-scroll::-webkit-scrollbar {
  display: none;  /* Chrome, Safari, Opera */
}

.slides-grid {
  display: flex;
  flex-direction: row;
  gap: var(--spacing-md, 24px);
  min-width: min-content;
  margin: 0 var(--spacing-md);
  width: 100%;
  align-items: center;
  scroll-snap-align: start; /* Snap points for slides */
  height: 100%;
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

.slide-thumbnail {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  cursor: pointer;
  transition: transform 0.2s ease;
  transform-origin: center center;
  scroll-snap-align: center;
  padding: var(--spacing-xs);
  border-radius: var(--border-radius);
  background: transparent;
}

.slide-thumbnail:hover {
  transform: scale(1.5);
}

.slide-thumbnail:active {
  transform: scale(0.98);
}

.slide-thumbnail:focus {
  outline: 2px solid var(--secondary-color);
  outline-offset: 2px;
}

.thumbnail {
  width: clamp(160px, 40vw, 320px);
  height: clamp(90px, 22.5vw, 180px);
  aspect-ratio: 16/9;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: var(--white);
  box-shadow: var(--shadow);
  flex-shrink: 0;
  /* position: relative; */
}

.background-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.slide-number, .slide-title {
  font-size: clamp(0.75rem, 3vw, 0.875rem);
  color: var(--text-light);
  font-weight: 500;
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-slides {
  text-align: center;
  color: var(--text-light);
  margin: var(--spacing-md) 0;
  width: 100%;
  padding: var(--spacing-lg);
}

.thumbnail-text-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
  /* background: rgba(255, 255, 255, 0.1); */
}

.slide-thumbnail:hover .thumbnail-text-elements {
  opacity: 1;
}

.thumbnail-text-element {
  position: absolute;
  font-size: clamp(0.5rem, 2vw, 0.75rem);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #000;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px;
  box-sizing: border-box;
  transform-origin: top left;
  border-radius: 2px;
}

.thumbnail-image-block {
  position: absolute;
  border: 1px dashed #666;
  background: rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transform-origin: top left;
  border-radius: 2px;
}

.image-dimensions {
  font-size: clamp(0.4rem, 1.5vw, 0.6rem);
  color: #666;
  background: rgba(255, 255, 255, 0.9);
  padding: 1px 3px;
  border-radius: 2px;
}

/* Mobile Optimizations */
@media (max-width: 900px) {
  .slides-scroll {
    height: clamp(250px, 50vh, 500px);
    padding: var(--spacing-sm) 0;
  }

  .slides-grid {
    gap: var(--spacing-sm);
    margin: 0 var(--spacing-sm);
  }

  .thumbnail {
    width: clamp(140px, 35vw, 280px);
    height: clamp(78.75px, 19.7vw, 157.5px);
  }
}

@media (max-width: 600px) {
  .slides-scroll {
    height: clamp(200px, 40vh, 400px);
    padding: var(--spacing-xs) 0;
  }

  .slides-grid {
    gap: var(--spacing-xs);
    margin: 0 var(--spacing-xs);
  }

  .thumbnail {
    width: clamp(120px, 30vw, 240px);
    height: clamp(67.5px, 16.9vw, 135px);
  }

  .slide-thumbnail {
    padding: var(--spacing-xs) 0;
  }
}

/* Touch Device Optimizations */
@media (hover: none) and (pointer: coarse) {
  .slide-thumbnail:hover {
    transform: none;
  }

  .slide-thumbnail:hover .thumbnail-text-elements {
    opacity: 0.5;
  }

  .slide-thumbnail:active {
    transform: scale(0.95);
  }

  .slide-thumbnail:active .thumbnail-text-elements {
    opacity: 0.7;
  }
}

/* Landscape Mode Optimizations */
@media (max-height: 600px) and (orientation: landscape) {
  .slides-scroll {
    height: clamp(180px, 35vh, 360px);
  }

  .thumbnail {
    width: clamp(100px, 25vw, 200px);
    height: clamp(56.25px, 14.1vw, 112.5px);
  }
}
</style>