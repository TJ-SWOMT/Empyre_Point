<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id

const title = ref('')
const description = ref('')
const error = ref('')
const isSubmitting = ref(false)

const loadPresentation = async () => {
  try {
    const response = await presentationApi.getPresentation(presentationId)
    if (response.success) {
      title.value = response.presentation.title || ''
      description.value = response.presentation.description || ''
    } else {
      error.value = response.error || 'Failed to load presentation'
    }
  } catch (err) {
    error.value = handleApiError(err)
  }
}

const saveChanges = async () => {
  try {
    isSubmitting.value = true
    error.value = ''

    const response = await presentationApi.updatePresentation(presentationId, {
      title: title.value,
      description: description.value
    })

    if (response.success) {
      router.push(`/presentations/${presentationId}`)
    } else {
      error.value = response.error || 'Failed to update presentation'
    }
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  router.push(`/presentations/${presentationId}`)
}

onMounted(loadPresentation)
</script>

<template>
  <div class="edit-presentation-modal-overlay">
    <div class="edit-presentation-modal-content">
      <div class="edit-presentation-modal-header">
        <h2>Edit Presentation</h2>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="edit-presentation-form-group">
        <label for="title">Title:</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="Enter presentation title"
        />
      </div>

      <div class="edit-presentation-form-group">
        <label for="description">Description:</label>
        <textarea
          id="description"
          v-model="description"
          placeholder="Enter presentation description"
          rows="4"
        ></textarea>
      </div>

      <div class="edit-presentation-modal-actions">
        <button @click="handleCancel" class="edit-presentation-cancel-button">Cancel</button>
        <button
          @click="saveChanges"
          :disabled="isSubmitting"
          class="edit-presentation-save-button"
        >
          {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>
