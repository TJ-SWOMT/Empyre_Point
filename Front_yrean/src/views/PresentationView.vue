<script setup>
import { useRoute } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import PresentationSlidesView from './PresentationSlidesView.vue'
import { useRouter } from 'vue-router'

const route = useRoute()
const presentationId = route.params.id
const router = useRouter()

const addSlide = () => {
  console.log('addSlide')

  router.push(`/presentations/${presentationId}/slides/new`)
}
</script>

<template>
  <div class="presentation-container">
    <h1>Presentation {{ presentationId }}</h1>
    <PresentationSlidesView />
    <button @click="addSlide">Add Slide</button>
  </div>
</template>
