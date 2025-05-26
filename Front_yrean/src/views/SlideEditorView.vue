<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slideId = route.params.slide_id
const error = ref('')
const isSubmitting = ref(false)
const isEditMode = computed(() => !!slideId)

// Initialize background color from session storage, but use presentation-specific key
const getStoredBackgroundColor = () => {
    const storedColor = sessionStorage.getItem(`slideBackgroundColor_${presentationId}`)
    return storedColor || '#FFFFFF'
}

const backgroundColor = ref(getStoredBackgroundColor())
const slideData = ref(null)

// Watch for changes to backgroundColor and save to session storage with presentation-specific key
watch(backgroundColor, (newColor) => {
    sessionStorage.setItem(`slideBackgroundColor_${presentationId}`, newColor)
})

const texts = ref([])

const loadSlideData = async () => {
    if (!isEditMode.value) return

    try {
        const response = await presentationApi.getPresentation(presentationId)
        if (response.error) throw new Error(response.error)
        
        // Convert slideId to number for comparison since it comes from route params
        const slide = response.presentation.slides.find(s => Number(s.slide_id) === Number(slideId))
        if (slide) {
            slideData.value = {
                ...slide,
                slide_id: Number(slide.slide_id) // Ensure consistent type
            }
            backgroundColor.value = slide.background_color || '#FFFFFF'
        } else {
            throw new Error('Slide not found')
        }
    } catch (err) {
        error.value = handleApiError(err)
    }
}

const saveSlide = async () => {
    try {
        isSubmitting.value = true
        error.value = ''
        
        let response
        if (isEditMode.value) {
            if (!slideData.value) {
                throw new Error('Slide data not loaded')
            }
            // Update existing slide
            response = await presentationApi.updateSlide(
                Number(slideId), // Ensure slideId is a number
                slideData.value.slide_number,
                backgroundColor.value,
                slideData.value.background_image_url
            )
        } else {
            // Create new slide
            response = await presentationApi.createSlide(
                presentationId,
                1,  // The backend will handle the slide number
                backgroundColor.value
            )
        }
        
        if (response.error) {
            throw new Error(response.error)
        }
        
        // Redirect back to the presentation view
        router.push(`/presentations/${presentationId}`)
    } catch (err) {
        error.value = handleApiError(err)
    } finally {
        isSubmitting.value = false
    }
}

const addText = () => {
    texts.value.push({
        id: texts.value.length + 1,
        text: ''
    })
}

const deleteText = (id) => {
    texts.value = texts.value.filter(text => text.id !== id)
}

const addImage = () => {
    console.log('addImage')
}

const box = ref(null)
const pageX = ref(null) 
const pageY = ref(null)

onMounted(async () => {
    if (isEditMode.value) {
        await loadSlideData()
    }

    box.value = document.querySelector(".slide-container")
    pageX.value = document.getElementById("x")
    pageY.value = document.getElementById("y")

    if (box.value) {
        const updateDisplay = (event) => {
            if (pageX.value && pageY.value) {
                pageX.value.innerText = event.pageX
                pageY.value.innerText = event.pageY
            }
        }

        box.value.addEventListener("mousemove", updateDisplay)
        box.value.addEventListener("mouseenter", updateDisplay)
        box.value.addEventListener("mouseleave", updateDisplay)
    }
})
</script>

<template>
    <div>
        <div class="header-container">
            <h1>{{ isEditMode ? 'Edit Slide' : 'Create Slide' }}</h1>
            <div class="controls">
                <div class="color-picker">
                    <label for="backgroundColor">Background Color:</label>
                    <input 
                        type="color" 
                        id="backgroundColor" 
                        v-model="backgroundColor"
                        title="Choose slide background color"
                    />
                </div>
                <button @click="addText">Add Text</button>
                <button @click="addImage">Add Image</button>
            </div>
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <div class="slide-container" :style="{ backgroundColor: backgroundColor }">
            <form v-for="text in texts" :key="text.id">
                <input type="text" placeholder="Text" />
                <button @click="deleteText(text.id)">x</button>
            </form>
            <p><code>pageX</code>: <span id="x">n/a</span></p>
            <p><code>pageY</code>: <span id="y">n/a</span></p>
        </div>

        <div class="action-buttons">
            <button @click="router.push(`/presentations/${presentationId}`)" class="cancel-button">
                Cancel
            </button>
            <button @click="saveSlide" :disabled="isSubmitting" class="save-button">
                {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Save Changes' : 'Create Slide') }}
            </button>
        </div>
    </div>
</template>

<style scoped>
.slide-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid #ccc;
    background-color: white;
    width: 960px;  /* Half of 1920px for better visibility */
    height: 540px; /* Half of 1080px to maintain 16:9 ratio */
    margin: 20px auto;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    max-width: 960px;
    margin: 0 auto;
}

.controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.color-picker {
    display: flex;
    align-items: center;
    gap: 8px;
}

.color-picker label {
    font-size: 14px;
    color: #666;
}

.color-picker input[type="color"] {
    width: 40px;
    height: 40px;
    padding: 0;
    border: 2px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.color-picker input[type="color"]::-webkit-color-swatch-wrapper {
    padding: 0;
}

.color-picker input[type="color"]::-webkit-color-swatch {
    border: none;
    border-radius: 2px;
}

.error-message {
    color: #dc3545;
    margin: 10px 0;
    text-align: center;
}

.action-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 20px;
}

.cancel-button, .save-button {
    padding: 10px 20px;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.cancel-button {
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    color: #666;
}

.cancel-button:hover {
    background-color: #e9ecef;
}

.save-button {
    background-color: #007bff;
    border: 1px solid #0056b3;
    color: white;
}

.save-button:hover {
    background-color: #0056b3;
}

.save-button:disabled {
    background-color: #ccc;
    border-color: #999;
    cursor: not-allowed;
}
</style> 