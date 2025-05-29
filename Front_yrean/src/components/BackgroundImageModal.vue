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
  emit('close')
}

watch(() => props.currentImage, (newImage) => {
  previewUrl.value = newImage
})
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditMode ? 'Edit Background Image' : 'Set Background Image' }}</h2>
        <button class="close-button" @click="handleClose">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">{{ error }}</div>

        <!-- Upload Section - Only show when no image exists -->
        <div v-if="!isEditMode" class="upload-section">
          <label class="upload-button">
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
        <div v-if="previewUrl" class="preview-section">
          <div
            class="preview-container"
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
        <div v-if="previewUrl" class="controls-section">
          <!-- Fit Options -->
          <div class="control-group">
            <label for="fit">Image Fit:</label>
            <select id="fit" v-model="fit" @change="handleFitChange">
              <option v-for="option in fitOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- Opacity -->
          <div class="control-group">
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
            <span class="opacity-value">{{ Math.round(opacity * 100) }}%</span>
          </div>

          <!-- Action Buttons -->
          <div class="action-buttons">
            <!-- Remove Button -->
            <button class="remove-button" @click="handleRemove">
              Remove Background Image
            </button>
            
            <!-- Upload New Button - Only show in edit mode -->
            <button v-if="isEditMode" class="upload-new-button" @click="previewUrl = null">
              Upload New Image
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #666;
}

.close-button:hover {
  color: #000;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-button:hover {
  background-color: var(--primary-hover);
}

.upload-button input[type="file"] {
  display: none;
}

.preview-section {
  margin-bottom: 20px;
}

.preview-container {
  width: 100%;
  height: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f5f5f5;
}

.controls-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-group label {
  min-width: 100px;
}

.control-group select,
.control-group input[type="range"] {
  flex: 1;
}

.opacity-value {
  min-width: 50px;
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.upload-new-button {
  padding: 10px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  flex: 1;
}

.upload-new-button:hover {
  background-color: var(--primary-hover);
}

.remove-button {
  flex: 1;
}

.error-message {
  color: #dc3545;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8d7da;
  border-radius: 4px;
}
</style> 