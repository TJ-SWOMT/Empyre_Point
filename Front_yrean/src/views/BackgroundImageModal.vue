<script setup>
import { ref, computed, watch } from 'vue'
import { presentationApi, handleApiError } from '../services/api'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  currentImage: {
    type: String,
    default: null
  },
  currentOpacity: {
    type: Number,
    default: 1
  },
  currentFit: {
    type: String,
    default: 'cover'
  }
})

const emit = defineEmits(['close', 'update', 'remove'])

const isUploading = ref(false)
const error = ref('')
const opacity = ref(props.currentOpacity)
const fit = ref(props.currentFit)
const previewUrl = ref(props.currentImage)

const isEditMode = computed(() => !!props.currentImage)

const fitOptions = [
  { value: 'cover', label: 'Cover (Fill)' },
  { value: 'contain', label: 'Contain (Fit)' },
  { value: 'stretch', label: 'Stretch' }
]

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  let imgUrl = null
  try {
    isUploading.value = true
    error.value = ''

    // Create a temporary image to get dimensions
    const img = new Image()
    imgUrl = URL.createObjectURL(file)

    // Wait for image to load
    await new Promise((resolve, reject) => {
      img.onload = resolve
      img.onerror = reject
      img.src = imgUrl
    })

    // Upload the image using the presentationApi
    const uploadResponse = await presentationApi.uploadImage(file)
    if (uploadResponse.error) {
      throw new Error(uploadResponse.error)
    }

    previewUrl.value = uploadResponse.image_url
    emit('update', {
      image_url: uploadResponse.image_url,
      opacity: opacity.value,
      fit: fit.value
    })
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error uploading image:', err)
  } finally {
    isUploading.value = false
    if (imgUrl) {
      URL.revokeObjectURL(imgUrl)
    }
  }
}

const handleOpacityChange = () => {
  emit('update', {
    image_url: previewUrl.value,
    opacity: opacity.value,
    fit: fit.value
  })
}

const handleFitChange = () => {
  emit('update', {
    image_url: previewUrl.value,
    opacity: opacity.value,
    fit: fit.value
  })
}

const handleRemove = () => {
  previewUrl.value = null
  emit('remove')
}

const handleClose = () => {
  previewUrl.value = props.currentImage
  opacity.value = props.currentOpacity
  fit.value = props.currentFit
  emit('close')
}

const handleOk = () => {
  emit('close')
}

watch(() => props.currentImage, (newImage) => {
  previewUrl.value = newImage
})

watch(() => props.currentOpacity, (newOpacity) => {
  opacity.value = newOpacity
})

watch(() => props.currentFit, (newFit) => {
  fit.value = newFit
})
</script>

<template>
  <div v-if="show" class="background-image-modal-overlay" @click="handleClose">
    <div class="background-image-modal-content" @click.stop>
      <div class="background-image-modal-header">
        <h2>{{ isEditMode ? 'Edit Background Image' : 'Set Background Image' }}</h2>
        <button class="background-image-modal-close-button" @click="handleClose">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">{{ error }}</div>

        <!-- Upload Section - Only show when no image exists -->
        <div v-if="!isEditMode" class="background-image-upload-section">
          <label class="background-image-upload-button">
            <input
              type="file"
              accept="image/*"
              @change="handleFileSelect"
              :disabled="isUploading"
            />
            {{ isUploading ? 'Uploading...' : 'Upload Image' }}
          </label>
        </div>

        <!-- Preview - Always show when there's an image -->
        <div v-if="previewUrl" class="background-image-preview-section">
          <div
            class="background-image-preview-container"
            :style="{
              backgroundImage: `url(${previewUrl})`,
              backgroundSize: fit === 'stretch' ? '100% 100%' : fit,
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
              opacity: opacity
            }"
          ></div>
        </div>

        <!-- Controls - Always show when there's an image -->
        <div v-if="previewUrl" class="background-image-controls-section">
          <!-- Fit Options -->
          <div class="background-image-control-group">
            <label for="fit">Image Fit:</label>
            <select id="fit" v-model="fit" @change="handleFitChange">
              <option v-for="option in fitOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- Opacity -->
          <div class="background-image-control-group">
            <label for="opacity">Opacity:</label>
            <input
              id="opacity"
              type="range"
              v-model.number="opacity"
              min="0"
              max="1"
              step="0.1"
              @input="handleOpacityChange"
            />
            <span class="background-image-opacity-value">{{ Math.round(opacity * 100) }}%</span>
          </div>

          <!-- Action Buttons -->
          <div class="background-image-action-buttons">
            <!-- Remove Button -->
            <button class="background-image-remove-button" @click="handleRemove">
              Remove Background Image
            </button>
            
            <!-- Upload New Button - Only show in edit mode -->
            <button v-if="isEditMode" class="background-image-upload-new-button" @click="previewUrl = null">
              Upload New Image
            </button>
          </div>

          <!-- Modal Action Buttons -->
          <div class="background-image-modal-action-buttons">
            <button class="background-image-cancel-button" @click="handleClose">Cancel</button>
            <button class="background-image-ok-button" @click="handleOk">OK</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 