<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import '../assets/styles/empyre-point.css'

const router = useRouter()
const presentations = ref([])
const error = ref('')
const isLoading = ref(true)
const username = ref('')
const presentationSureness = ref({})

const fetchPresentations = async () => {
  try {
    isLoading.value = true
    const user = JSON.parse(sessionStorage.getItem('user'))
    username.value = user.username
    console.log(user)
    if (!user || !user.user_id) {
      throw new Error('User not found')
    }
    const response = await presentationApi.getUserPresentations(user.user_id)
    console.log('response', response)
    console.log(response.presentations)
    if (response.error) {
      throw new Error(response.error)
    }
    presentations.value = response.presentations || []
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    isLoading.value = false
  }
}

const createNewPresentation = () => {
  router.push('/create-presentation')
}

const viewPresentation = presentationId => {
  router.push(`/presentations/${presentationId}`)
}

const checkSureness = (presentationId, event) => {
  console.log('checkSureness', presentationId, event)
  sessionStorage.setItem('pId', presentationId)
  sessionStorage.setItem('e', event)
  // event.preventDefault()
  // event.stopPropagation()
  console.log('presentationSureness', presentationSureness.value)
  presentationSureness.value[presentationId] =
    !presentationSureness.value[presentationId]
  console.log('presentationSureness', presentationSureness.value)
}

const deletePresentation = async (presentationId, event) => {
  event.preventDefault()
  event.stopPropagation()
  try {
    await presentationApi.deletePresentation(presentationId)
    await fetchPresentations()
  } catch (err) {
    error.value = handleApiError(err)
  }
}

const resetSureness = (presentationId, event) => {
  console.log('resetSureness', presentationId, event)
  if (!presentationSureness.value[presentationId]) {
    presentationSureness.value[presentationId] = false
  }
  checkSureness(sessionStorage.getItem('pId'), sessionStorage.getItem('e'))
}

const onClickOutside = (selector, callback) => {
  document.addEventListener('click', e => {
    const elements = document.querySelectorAll(selector)
    let isInside = false
    elements.forEach(el => {
      if (el.contains(e.target)) isInside = true
    })
    if (!isInside) callback()
  })
}
// onClickOutside('.delete-presentation-button', () => console.log('Hello'));
onClickOutside('#delete-presentation-button', () => resetSureness())
// Will log 'Hello' whenever the user clicks outside of #my-element

onMounted(fetchPresentations)
</script>

<template>
  <div class="container">
    <div class="header_user_presentations">
      <div class="header_user_presentations_text">
        {{ username }}'s Presentations
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading">Loading presentations...</div>

    <div v-else-if="presentations.length === 0" class="no-presentations">
      <p>You haven't created any presentations yet.</p>
      <button @click="createNewPresentation" class="btn btn-secondary">
        Create Your First Presentation
      </button>
    </div>

    <div v-else class="presentations-grid">
      <div
        v-for="presentation in presentations"
        :key="presentation.presentation_id"
        class="presentation-card"
      >
        <h3>{{ presentation.title }}</h3>
        <div class="description-container">
          <p v-if="presentation.description" class="truncated-description">
            {{ presentation.description }}
          </p>
          <div v-if="presentation.description" class="tooltip">
            {{ presentation.description }}
          </div>
        </div>
        <div class="presentation-meta">
          <span
            >Created:
            {{ new Date(presentation.created_at).toLocaleDateString() }}</span
          >
          <br />
          <span v-if="presentation.slide_count"
            >Slides: {{ presentation.slide_count }}</span
          >
        </div>
        <button
          @click="viewPresentation(presentation.presentation_id)"
          class="btn btn-secondary"
        >
          View Presentation
        </button>
        <button
          @click.stop="
            presentationSureness[presentation.presentation_id]
              ? deletePresentation(presentation.presentation_id, $event)
              : checkSureness(presentation.presentation_id, $event)
          "
          class="btn btn-danger delete-presentation-button"
        >
          {{
            !presentationSureness[presentation.presentation_id]
              ? 'Delete Presentation'
              : 'Click again to delete'
          }}
        </button>
      </div>
    </div>
  </div>
</template>
