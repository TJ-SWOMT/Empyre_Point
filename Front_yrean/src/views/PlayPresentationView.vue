<script setup>
import { ref, onMounted, computed, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slides = ref([])
const currentSlideIndex = ref(0)
const error = ref('')
const isLoading = ref(true)
const slideElements = ref({})
const elementsLoaded = ref({}) // Track which slides have their elements loaded
const slideWrapperRef = ref(null)
const scale = ref(1)

const currentSlide = computed(() => slides.value[currentSlideIndex.value] || null)
const isFirstSlide = computed(() => currentSlideIndex.value === 0)
const isLastSlide = computed(() => currentSlideIndex.value === slides.value.length - 1)
const isCurrentSlideReady = computed(() => {
  if (!currentSlide.value) return false
  return elementsLoaded.value[currentSlide.value.slide_id] === true
})

const fetchSlideElements = async (slideId) => {
  try {
    console.log('Fetching elements for slide:', slideId)
    elementsLoaded.value[slideId] = false
    const response = await presentationApi.getSlideElements(slideId)
    console.log('Raw elements response for slide', slideId, ':', response)
    
    if (response.success && response.elements) {
      // Process elements to normalize the data structure
      const processedElements = response.elements.map(element => {
        // Log the raw element for debugging
        console.log('Processing element:', element)
        const processed = {
          element_id: element.element_id,
          element_type: element.element_type,
          x_position: parseFloat(element.x_position),
          y_position: parseFloat(element.y_position),
          width: parseFloat(element.width),
          height: parseFloat(element.height),
          z_index: element.z_index || 0,
          content: element.element_data?.content || 'Empty Text',
          font_family: element.element_data?.font_family || 'Arial',
          font_size: element.element_data?.font_size || 24,
          font_color: element.element_data?.font_color || '#000000',
          bold: element.element_data?.bold || false,
          italic: element.element_data?.italic || false,
          underline: element.element_data?.underline || false,
          text_align: element.element_data?.text_align || 'left'
        }
        console.log('Processed element:', processed)
        return processed
      })
      slideElements.value[slideId] = processedElements
      console.log('Final processed elements for slide', slideId, ':', processedElements)
    }
    elementsLoaded.value[slideId] = true
  } catch (err) {
    console.error('Error fetching slide elements:', err)
    elementsLoaded.value[slideId] = false
  }
}

const fetchSlides = async () => {
  try {
    isLoading.value = true
    error.value = ''
    console.log('Fetching presentation with ID:', presentationId)
    const response = await presentationApi.getPresentation(presentationId)
    console.log('Full presentation response:', JSON.stringify(response, null, 2))
    
    if (response.error) {
      throw new Error(response.error)
    }
    
    if (!response.success || !response.presentation?.slides) {
      throw new Error('Failed to fetch presentation slides')
    }
    
    // Log the raw slides data
    console.log('Raw slides data:', JSON.stringify(response.presentation.slides, null, 2))
    
    // Sort slides by slide_number and filter out any invalid slides
    slides.value = response.presentation.slides
      .filter(slide => {
        const isValid = slide && typeof slide === 'object' && slide.slide_id && slide.slide_number
        if (!isValid) {
          console.warn('Invalid slide found:', slide)
        }
        return isValid
      })
      .sort((a, b) => a.slide_number - b.slide_number)
    
    console.log('Processed slides with details:', slides.value.map(slide => ({
      id: slide.slide_id,
      number: slide.slide_number,
      title: slide.title
    })))
    
    if (slides.value.length === 0) {
      throw new Error('No slides found in this presentation')
    }
    
    // Start with the first slide (slide_number === 1)
    currentSlideIndex.value = slides.value.findIndex(slide => slide.slide_number === 1)
    if (currentSlideIndex.value === -1) {
      console.warn('Slide number 1 not found, using first slide')
      currentSlideIndex.value = 0
    }

    // Fetch elements for all slides
    console.log('Fetching elements for slides:', slides.value.map(s => s.slide_id))
    await Promise.all(slides.value.map(slide => fetchSlideElements(slide.slide_id)))
    console.log('All slide elements:', Object.fromEntries(
      Object.entries(slideElements.value).map(([id, elements]) => [
        id,
        elements.map(e => ({ id: e.element_id, type: e.element_type, content: e.content }))
      ])
    ))
  } catch (err) {
    console.error('Error in fetchSlides:', err)
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

function calculateScale() {
  // Get available viewport size (subtract some margin)
  const margin = 40
  const maxW = window.innerWidth - margin * 2
  const maxH = window.innerHeight - 120 // leave space for nav controls
  const scaleW = maxW / 1000
  const scaleH = maxH / 600
  scale.value = Math.min(scaleW, scaleH, 1) // never upscale above 1
}

onMounted(() => {
  fetchSlides()
  window.addEventListener('keydown', handleKeyPress)
  window.addEventListener('resize', calculateScale)
  nextTick(() => calculateScale())
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
  window.removeEventListener('resize', calculateScale)
})

watch(currentSlide, () => nextTick(() => calculateScale()))

// Add a watch to log when current slide changes
watch(currentSlide, (newSlide) => {
  if (newSlide) {
    console.log('Current slide changed to:', {
      id: newSlide.slide_id,
      number: newSlide.slide_number,
      elements: slideElements.value[newSlide.slide_id]?.length || 0
    })
  }
})
</script>

<template>
  <div class="play-presentation-container" @click="nextSlide">
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="isLoading" class="loading">
      Loading presentation...
    </div>
    <div v-else-if="currentSlide" class="slide-scale-wrapper" ref="slideWrapperRef">
      <div 
        class="slide-display"
        :style="{
          backgroundColor: currentSlide.background_color || '#FFFFFF',
          transform: `scale(${scale})`,
          margin: '0 auto',
        }"
      >
        <!-- Background image -->
        <div v-if="currentSlide.background_image_url" 
             class="background-image"
             :style="{ backgroundImage: `url(${currentSlide.background_image_url})` }">
        </div>
        <!-- Loading indicator for current slide -->
        <div v-if="!isCurrentSlideReady" class="slide-loading">
          Loading slide content...
        </div>
        <!-- Slide elements -->
        <div v-else class="slide-elements">
          <template v-if="slideElements[currentSlide.slide_id]?.length > 0">
            <div v-for="element in slideElements[currentSlide.slide_id]" 
                 :key="element.element_id"
                 class="text-element"
                 :style="{
                   position: 'absolute',
                   left: `${element.x_position}px`,
                   top: `${element.y_position}px`,
                   width: `${element.width}px`,
                   height: `${element.height}px`,
                   fontFamily: element.font_family,
                   fontSize: `${element.font_size}px`,
                   color: element.font_color,
                   fontWeight: element.bold ? 'bold' : 'normal',
                   fontStyle: element.italic ? 'italic' : 'normal',
                   textDecoration: element.underline ? 'underline' : 'none',
                   textAlign: element.text_align,
                   zIndex: element.z_index,
                   pointerEvents: 'none',
                   backgroundColor: 'rgba(255, 255, 255, 0.9)',
                   border: '2px solid rgba(0, 0, 0, 0.5)',
                   padding: '6px',
                   boxSizing: 'border-box',
                   display: 'flex',
                   alignItems: 'center',
                   justifyContent: 'center',
                   overflow: 'hidden',
                 }">
              <div class="element-content" :style="{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: element.text_align,
                overflow: 'hidden',
                wordBreak: 'break-word',
                color: element.font_color,
                fontSize: `${element.font_size}px`,
                fontWeight: element.bold ? 'bold' : 'normal',
                fontStyle: element.italic ? 'italic' : 'normal',
                textDecoration: element.underline ? 'underline' : 'none',
                padding: '2px',
                lineHeight: '1.2'
              }">
                {{ element.content }}
              </div>
            </div>
          </template>
          <div v-else class="debug-info">
            No elements on this slide (Slide {{ currentSlide.slide_number }})
          </div>
        </div>
        <!-- Debug overlay -->
        <!-- <div class="debug-overlay" v-if="currentSlide">
          <div>Presentation ID: {{ presentationId }}</div>
          <div>Slide ID: {{ currentSlide.slide_id }}</div>
          <div>Slide Number: {{ currentSlide.slide_number }}</div>
          <div>Elements: {{ slideElements[currentSlide.slide_id]?.length || 0 }}</div>
          <div>Total Slides: {{ slides.length }}</div>
          <div>Elements Loaded: {{ isCurrentSlideReady ? 'Yes' : 'No' }}</div>
          <div v-if="slideElements[currentSlide.slide_id]?.length > 0">
            First Element: {{ JSON.stringify(slideElements[currentSlide.slide_id][0]) }}
          </div>
        </div> -->
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

.slide-scale-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 80vh;
  /* Center the slide */
  overflow: hidden;
}

.slide-display {
  width: 1000px;
  height: 600px;
  background-color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  /* Responsive scaling */
  transform-origin: top left;
  margin: 0 auto;
}

/* Responsive scaling for .slide-display */
@media (max-width: 1200px), (max-height: 800px) {
  .slide-scale-wrapper {
    width: 100vw;
    height: 80vh;
  }
  .slide-display {
    /* Scale to fit viewport, maintaining 16:9 */
    /* Calculate scale factor in JS if needed for perfect fit */
    max-width: 100vw;
    max-height: 80vh;
  }
}

.slide-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 1000px;
  height: 600px;
  pointer-events: none;
  overflow: visible;
}

.text-element {
  position: absolute;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(0, 0, 0, 0.5);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.element-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  word-break: break-word;
  line-height: 1.2;
  padding: 2px;
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

.slide-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 1000;
}

.debug-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1000;
}
</style> 