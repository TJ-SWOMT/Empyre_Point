<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slides = ref([])
const error = ref('')
const isLoading = ref(true)

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
    console.log('Raw slides data:', JSON.stringify(response.presentation.slides, null, 2))
    
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
  <div class="slides-container">
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <div v-if="isLoading" class="loading">
      Loading slides...
    </div>

    <div v-else-if="!slides || slides.length === 0" class="no-slides">
      <p>No slides for this presentation.</p>
    </div>

    <div v-else class="slides-grid">
      <template v-for="(slide, index) in slides" :key="slide.slide_id">
        <div v-if="slide && slide.slide_id" 
             class="slide-thumbnail"
             @click="router.push(`/presentations/${presentationId}/slides/${Number(slide.slide_id)}`)"
             role="button"
             tabindex="0"
             @keyup.enter="router.push(`/presentations/${presentationId}/slides/${Number(slide.slide_id)}`)">
          <div class="thumbnail" 
               :style="{ backgroundColor: slide.background_color }">
            <!-- Placeholder for slide content -->
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
</template>

<style scoped>
.slides-container {
  padding: 20px;
}

.error-message {
  color: #dc3545;
  margin: 10px 0;
  text-align: center;
}

.loading {
  text-align: center;
  color: #666;
  margin: 20px 0;
}

.no-slides {
  text-align: center;
  color: #666;
  margin: 20px 0;
}

.slides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.slide-thumbnail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.slide-thumbnail:hover {
  transform: scale(1.02);
}

.slide-thumbnail:focus {
  outline: 2px solid #007bff;
  outline-offset: 2px;
}

.thumbnail {
  width: 200px;
  height: 112.5px; /* 16:9 aspect ratio */
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.background-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.slide-number {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
</style>