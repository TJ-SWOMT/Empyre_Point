<script setup>
import { ref, onMounted, computed, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import { marked } from 'marked'
import { useSlideScale } from '../composables/useSlideScale'
import '../styles/empyre-point.css'

// Custom renderer for marked to ensure links open in a new tab
const renderer = new marked.Renderer()
renderer.link = function(token) {
  // For marked v5+, token is an object
  const safeHref = typeof token.href === 'string' ? token.href : '';
  const safeText = typeof token.text === 'string' ? token.text : '';
  return `<a href="${safeHref}" target="_blank" rel="noopener noreferrer" style="color:#1976d2;text-decoration:underline;cursor:pointer;">${safeText}</a>`;
}

const renderElementContent = (element) => {
  return marked(element.content || '', { renderer })
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

const availableHeight = ref(window.innerHeight - 120) // adjust as needed for nav
const availableWidth = ref(window.innerWidth)

const { scale, DESIGN_WIDTH, DESIGN_HEIGHT, calculateScale } = useSlideScale(
  availableHeight,
  availableWidth
)

function updateAvailableHeight() {
  availableHeight.value = window.innerHeight - 120 // adjust as needed
  availableWidth.value = window.innerWidth
  calculateScale()
}

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
        if (element.element_type === 'image') {
          // Handle image element
          return {
            element_id: element.element_id,
            element_type: 'image',
            x_position: parseFloat(element.x_position),
            y_position: parseFloat(element.y_position),
            width: parseFloat(element.width),
            height: parseFloat(element.height),
            z_index: element.z_index || 0,
            image_url: element.element_data?.image_url || '',
            alt_text: element.element_data?.alt_text || '',
          }
        } else {
          // Default: treat as text
          return {
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
        }
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
  window.addEventListener('resize', updateAvailableHeight)
  document.body.classList.add('play-mode')
  updateAvailableHeight()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
  window.removeEventListener('resize', updateAvailableHeight)
  document.body.classList.remove('play-mode')
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
  <div class="play-presentation-container">
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="isLoading" class="loading">
      Loading presentation...
    </div>
    <div v-else-if="currentSlide" class="slide-scale-wrapper play-view" ref="slideWrapperRef"
      :style="{
        width: '100%',
        height: availableHeight + 'px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden'
      }"
    >
      <div 
        class="slide-display"
        :style="{
          backgroundColor: currentSlide.background_color || '#FFFFFF',
          width: DESIGN_WIDTH + 'px',
          height: DESIGN_HEIGHT + 'px',
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
          position: 'relative'
        }"
      >
        <!-- Background image -->
        <div v-if="currentSlide.background_image_url" 
             class="background-image"
             :style="{
               backgroundImage: `url(${currentSlide.background_image_url})`,
               backgroundSize: currentSlide.background_image_fit || 'cover',
               backgroundPosition: currentSlide.background_image_position || 'center',
               backgroundRepeat: 'no-repeat',
               opacity: currentSlide.background_image_opacity || 1,
               position: 'absolute',
               top: 0,
               left: 0,
               right: 0,
               bottom: 0,
               zIndex: 0
             }">
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
                 :class="element.element_type === 'image' ? 'image-element' : 'text-element'"
                 :style="{
                   position: 'absolute',
                   left: `${element.x_position}px`,
                   top: `${element.y_position}px`,
                   width: `${element.width}px`,
                   height: `${element.height}px`,
                   zIndex: element.z_index,
                   ...(element.element_type === 'text' ? {
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
                     display: 'block',
                     padding: 0,
                     overflow: 'hidden',
                     wordBreak: 'break-word',
                     whiteSpace: 'pre-wrap',
                   } : {
                     background: 'transparent',
                     border: 'none',
                     boxSizing: 'border-box',
                     display: 'flex',
                     alignItems: 'center',
                     justifyContent: 'center',
                     overflow: 'hidden',
                     padding: 0
                   })
                 }">
              <!-- Render text element -->
              <template v-if="element.element_type === 'text'">
                <div class="element-content" :style="{
                  width: '100%',
                  height: '100%',
                  display: 'block',
                  textAlign: element.text_align,
                  overflow: 'hidden',
                  color: element.font_color,
                  fontSize: `${element.font_size}px`,
                  fontWeight: element.bold ? 'bold' : 'normal',
                  fontStyle: element.italic ? 'italic' : 'normal',
                  textDecoration: element.underline ? 'underline' : 'none',
                  padding: '2px',
                  lineHeight: '1.2'
                }">
                  <div 
                    v-html="renderElementContent(element)" 
                    style="width:100%;height:100%;"
                  ></div>
                </div>
              </template>
              <!-- Render image element -->
              <template v-else-if="element.element_type === 'image'">
                <div class="image-container" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;">
                  <img :src="element.image_url" :alt="element.alt_text" style="max-width:100%;max-height:100%;object-fit:contain;" />
                </div>
              </template>
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