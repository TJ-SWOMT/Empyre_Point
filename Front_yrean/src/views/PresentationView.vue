<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import PresentationSlidesView from './PresentationSlidesView.vue'
import { useRouter } from 'vue-router'

import '../assets/styles/empyre-point.css'

const route = useRoute()
const presentationId = route.params.id
const presentationTitle = ref('')
const presentationDescription = ref('')
const router = useRouter()
const hasSlides = ref(false)
const error = ref('')

const checkForSlides = async () => {
  try {
    const response = await presentationApi.getPresentation(presentationId)
    console.log('response', response)
    if (response.success) {
      if (response.presentation?.slides[0].slide_number) {
        hasSlides.value = true
      } else {
        hasSlides.value = false
      }
      if (response.presentation?.title) {
        presentationTitle.value = response.presentation.title
      } else {
        presentationTitle.value = 'Presentation ' + presentationId
      }
      if (response.presentation?.description) {
        console.log('response.presentation.description', response.presentation.description)
        presentationDescription.value = response.presentation.description
        console.log('presentationDescription', presentationDescription.value)
      } else {
        presentationDescription.value = ''
      }
    } else {
      error.value = response.error || 'Failed to load presentation'
    }
  } catch (err) {
    error.value = handleApiError(err)
  }
}

const addSlide = () => {
  router.push(`/presentations/${presentationId}/slides/new`)
}

const editPresentation = () => {
  router.push(`/presentations/${presentationId}/edit`)
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
    <div class="create-presentation-header">
      <div class="create-presentation-title" v-if=presentationTitle>{{ presentationTitle }}</div>
      <div class="create-presentation-title" v-else>Your Presentation</div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </div>
    <div class="presentation-actions">
      <button @click="addSlide">Add Slide</button>
      <button @click="editPresentation">Edit Presentation</button>
      <button 
        :disabled="!hasSlides"
        @click="playPresentation"
        class="play-button"
      >
        Play Presentation
      </button>
      <div v-if=presentationDescription class="presentation-description">{{ presentationDescription }}</div>
    </div>
    <div class="slides-container">
      <PresentationSlidesView />
    </div>
  </div>
</template>
