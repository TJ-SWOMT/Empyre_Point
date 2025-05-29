<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import '../assets/styles/empyre-point.css'

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