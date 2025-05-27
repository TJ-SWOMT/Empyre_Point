<script setup>
import { ref, onMounted, computed, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import { marked } from 'marked'
import { useSlideScale } from '../composables/useSlideScale'

// Function to render element content with markdown
const renderElementContent = (element) => {
  return marked(element.content || '')
}

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

const { scale, DESIGN_WIDTH, DESIGN_HEIGHT } = useSlideScale()

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

onMounted(() => {
  fetchSlides()
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})

watch(currentSlide, () => nextTick(() => {}))

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
          width: DESIGN_WIDTH + 'px',
          height: DESIGN_HEIGHT + 'px',
          position: 'absolute',
          left: '50%',
          top: '50%',
          transform: `translate(-50%, -50%) scale(${scale})`,
          transformOrigin: 'top left'
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
                   zIndex: element.z_index,
                   fontFamily: element.font_family,
                   fontSize: `${element.font_size}px`,
                   color: element.font_color,
                   fontWeight: element.bold ? 'bold' : 'normal',
                   fontStyle: element.italic ? 'italic' : 'normal',
                   textDecoration: element.underline ? 'underline' : 'none',
                   textAlign: element.text_align,
                   background: 'rgba(0,0,0,0)',
                   border: 'none',
                   boxSizing: 'border-box',
                   display: 'flex',
                   alignItems: 'center',
                   justifyContent: 'center',
                   padding: 0
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
                <div v-html="renderElementContent(element)" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;"></div>
              </div>
            </div>
          </template>
        </div>
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
  display: block;
  position: relative;
  width: 100vw;
  height: 80vh;
  overflow: hidden;
  margin: 0 auto;
}

.slide-display {
  width: 960px;
  height: 540px;
  background-color: white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  position: absolute;
  overflow: hidden;
  border: 1px solid #ccc;
  cursor: pointer;
  transform-origin: top left;
  box-sizing: border-box;
  /* left/top/translate handled inline */
}

.slide-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 960px;  /* Match edit view dimensions */
  height: 540px; /* Match edit view dimensions */
  pointer-events: none;
  overflow: visible;
}

.text-element {
  position: absolute;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.9);
  border: 2px solid rgba(0,0,0,0.5);
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  min-width: 0;
  min-height: 0;
  padding: 0;
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

/* Markdown Styles */
.markdown-content {
  width: 100%;
  height: 100%;
  /* overflow: auto; */
}

.markdown-content :deep(h1) {
  font-size: 2em;
  margin: 0.67em 0;
  font-weight: bold;
}

.markdown-content :deep(h2) {
  font-size: 1.5em;
  margin: 0.83em 0;
  font-weight: bold;
}

.markdown-content :deep(h3) {
  font-size: 1.17em;
  margin: 1em 0;
  font-weight: bold;
}

.markdown-content :deep(ul) {
  list-style-type: disc;
  margin: 1em 0;
  padding-left: 2em;
}

.markdown-content :deep(li) {
  margin: 0.5em 0;
}

.markdown-content :deep(a) {
  color: #007bff;
  text-decoration: underline;
}

.markdown-content :deep(a:hover) {
  color: #0056b3;
}

.markdown-content :deep(code) {
  font-family: monospace;
  background-color: #f8f9fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background-color: #f8f9fa;
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
  margin: 1em 0;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  font-size: 0.9em;
  white-space: pre;
}

.markdown-content :deep(strong) {
  font-weight: bold;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(br) {
  margin: 0.5em 0;
}
</style> 