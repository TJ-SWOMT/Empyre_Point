<script setup>
import { ref, onMounted, computed, nextTick, onBeforeUnmount, watch } from 'vue'
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

// For responsive scaling per thumbnail
const thumbnailRefs = ref([])
const thumbnailScales = ref([])
const DESIGN_WIDTH = 960
const DESIGN_HEIGHT = 540
let observers = []

function setThumbnailRef(el, idx) {
  if (el) {
    thumbnailRefs.value[idx] = el
  }
}

function updateThumbnailScale(idx) {
  const el = thumbnailRefs.value[idx]
  if (!el) return
  const width = el.clientWidth
  const height = el.clientHeight
  const scaleW = width / DESIGN_WIDTH
  const scaleH = height / DESIGN_HEIGHT
  thumbnailScales.value[idx] = Math.min(scaleW, scaleH) * 0.9
}

function setupResizeObservers() {
  observers.forEach(obs => obs.disconnect())
  observers = []
  slides.value.forEach((_, idx) => {
    const el = thumbnailRefs.value[idx]
    if (el) {
      const obs = new ResizeObserver(() => updateThumbnailScale(idx))
      obs.observe(el)
      observers.push(obs)
      // Initial update
      updateThumbnailScale(idx)
    }
  })
}

onMounted(() => {
  nextTick(() => setupResizeObservers())
})

onBeforeUnmount(() => {
  observers.forEach(obs => obs.disconnect())
})

// Re-setup observers when slides change
watch(slides, () => {
  nextTick(() => setupResizeObservers())
})

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
                 :ref="el => setThumbnailRef(el, index)"
                 :style="{ backgroundColor: slide.background_color }">
              <div class="thumbnail-content"
                   :style="{
                     width: DESIGN_WIDTH + 'px',
                     height: DESIGN_HEIGHT + 'px',
                     position: 'absolute',
                     top: '50%',
                     left: '50%',
                     transform: `translate(-50%, -50%) scale(${thumbnailScales[index] || 1})`,
                     transformOrigin: 'center center'
                   }">
                <div v-if="slide.background_image_url" 
                     class="background-image"
                     :style="{ backgroundImage: `url(${slide.background_image_url})` }">
                </div>
                <div class="thumbnail-text-elements">
                  <template v-for="element in slideElements[slide.slide_id]" :key="element.element_id">
                    <div v-if="element.element_type === 'text'"
                         class="thumbnail-text-element"
                         :style="{
                           left: `${(element.x_position / DESIGN_WIDTH) * 100}%`,
                           top: `${(element.y_position / DESIGN_HEIGHT) * 100}%`,
                           width: `${(element.width / DESIGN_WIDTH) * 100}%`,
                           height: `${(element.height / DESIGN_HEIGHT) * 100}%`,
                           zIndex: element.z_index
                         }">
                      {{ element.content }}
                    </div>
                    <div v-else-if="element.element_type === 'image'"
                         class="thumbnail-image-block"
                         :style="{
                           left: `${(element.x_position / DESIGN_WIDTH) * 100}%`,
                           top: `${(element.y_position / DESIGN_HEIGHT) * 100}%`,
                           width: `${(element.width / DESIGN_WIDTH) * 100}%`,
                           height: `${(element.height / DESIGN_HEIGHT) * 100}%`,
                           zIndex: element.z_index
                         }">
                      <img :src="element.content" alt="" style="width:100%;height:100%;object-fit:contain;" />
                    </div>
                  </template>
                </div>
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
.thumbnail {
  width: clamp(160px, 40vw, 320px);
  height: clamp(90px, 22.5vw, 180px);
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: var(--white);
  box-shadow: var(--shadow);
  flex-shrink: 0;
}
.thumbnail-content {
  /* All positioning and scaling is now inline style for centering and scaling */
}
.slide-thumbnail:hover {
  transform: scale(1.5);
  z-index: 2;
}
.thumbnail-text-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 1;
  transition: none;
}
.thumbnail-text-element {
  position: absolute;
  font-size: 16px;
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
  overflow: hidden;
}
.thumbnail-image-block img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 0;
}
</style>